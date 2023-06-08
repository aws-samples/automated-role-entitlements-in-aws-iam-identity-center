import time
import sys
import json
import os

import boto3

from account_logic import retrieve_account_information
from entitlement_logic import create_acnt_entitlements, attach_entitlement, create_ps_entitlements
from naming_convention_logic import craft_group_names

def generate_sso_permission_set_dict(sso_id: str, sso_client) -> dict:
    permission_set_dict = {}
    permission_set_list = []

    # Get permission set ARNs up to 100 results
    response = sso_client.list_permission_sets(
        InstanceArn=sso_id,
        MaxResults=100
    )
    permission_set_list = response['PermissionSets']

    # Check for more SSO Permission Sets
    while 'NextToken' in response:
        response = sso_client.list_permission_sets(
            InstanceArn=sso_id,
            NextToken = response['NextToken'],
            MaxResults=100
        )
        permission_set_list.extend(response['PermissionSets'])

    # Get friendly names for each ARN
    for ps in permission_set_list:
        permission_set = sso_client.describe_permission_set(
            InstanceArn=sso_id,
            PermissionSetArn=ps
        )['PermissionSet']
        permission_set_dict[permission_set['Name']] = permission_set['PermissionSetArn']
    
    return permission_set_dict

# Create a User group dictionary -> {GroupName:ARN, ...} from AWS IAM Identity Center (existing User groups synced through SCIM)
def generate_group_dict(ids_id: str, ids_client, account_name: str, all_account_list: list, psnames_list: list) -> dict:
    sso_groups_dict = {} # {DisplayName:Arn}
    group_names = craft_group_names(account_name, all_account_list, psnames_list)
    for group in group_names:
        response = ids_client.list_groups(
            IdentityStoreId=ids_id,
            Filters=[
                {
                    "AttributePath": "DisplayName",
                    "AttributeValue": group
                }
            ]
        )['Groups'] # Currently, API only returns one item matched with required Filters.AttributeValue
        if response:
            sso_groups_dict[group] = response[0]['GroupId']
        else:
            if account_name:
                print(f"{group} was not found in User groups for new AWS Account - {account_name} (Perhaps it hasn't sync'd yet? OR AD Admin did not create the group on Azure AD)")

    return sso_groups_dict
    
def lambda_handler(event, context):
    sso_client = boto3.client('sso-admin')
    ids_client = boto3.client('identitystore')
    org_client = boto3.client('organizations')
    sts_client = boto3.client('sts')

    # get SSO instance ARN
    instances = sso_client.list_instances()['Instances'][0]
    sso_id = instances['InstanceArn']
    ids_id = instances['IdentityStoreId']

    # Generate full list of Permission Sets under the SSO Instance
    sso_permission_sets = generate_sso_permission_set_dict(sso_id, sso_client) #creates dictionary -> {PermissionSetName:ARN}
    
    # The naming convention for automation resources is as follows
    # Account_name = aws-< OU indicator>-<environment>-<account type / name with numerical counter>
    # Permission set template = <job function>-role
    # Group_template = <account name>-<job function>
    
    # Determine if this lambda is being invoked by New Account CW Event or New User group CW Event or New Permission Set Event
    if 'detail' in event and 'eventName' in event['detail'] and event['detail']['eventName'] == 'CreateGroup':
        group_name = event['detail']['requestParameters']['displayName']
        group_id = event['detail']['responseElements']['group']['groupId']
        print(f'Lambda invoked by CloudWatch Event for New User Group - {group_name} created in enterprise identity source synced with AWS IAM Identity Center.')
        account_name = "-".join(group_name.split("-")[0:-1])     
        print('Retrieving Account Information using account_name and module logic')
        account_id = retrieve_account_information(org_client, account_name,"for_group_event")
        print('Retrieving existing Permission Set mapped to the newly created User group')
        ps_name = group_name.split("-")[-1]+"-role"
        if ps_name in sso_permission_sets.keys():
            ps_arn = sso_permission_sets[ps_name]
            print(f'Entitling User group - {group_name} to Account - {account_name} with Permission Set - {ps_name}')
            attach_entitlement(sso_id, sso_client, account_id, group_id, ps_arn, ps_name, group_name)
        else:
            print(f'Permission Set - {ps_name} for the User group - {group_name} is NOT PRESENT in AWS IAM Identity center')
        
    elif 'detail' in event and 'eventName' in event['detail'] and event['detail']['eventName'] == 'CreateManagedAccount':
        account_id = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']
        account_name = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountName']
        print(f'Lambda invoked by CloudWatch Event for New AWS Account - {account_name} vending Event')

        # Get Lambda Environment Variables related to IAM Identity Center
        psnames_list = json.loads(os.environ['new_acnt_perms'])
        print(f'For a new AWS Account, list of baseline roles to be created - {psnames_list}')

        # Generate existing User group Dictionary for the new AWS Account
        print('Fetching existing User groups for the new AWS Account')
        all_account_list = None #This variable is applicable for new Permission Set event
        ad_group_dict = generate_group_dict(ids_id, ids_client, account_name, all_account_list, psnames_list)
        if ad_group_dict:
            # Entitle given Groups to given account ID
            print(f'Entitling relevant SSO groups to the baseline set of IAM roles (Permission Sets) for the new Account - {account_name}.')
            create_acnt_entitlements(sso_id, sso_client, account_id, account_name, ad_group_dict, sso_permission_sets)
        else:
            print(f'NO User groups exist for the new AWS Account - {account_name}')
            exit()

    elif 'detail' in event and 'eventName' in event['detail'] and event['detail']['eventName'] == 'CreatePermissionSet':
        newPermissionSet = {}
        psnames_list = []
        newPermissionSet['Perm_Name'] = event['detail']['responseElements']['permissionSet']['name']
        newPermissionSet['Perm_Arn'] = event['detail']['responseElements']['permissionSet']['permissionSetArn']
        newPermName = newPermissionSet['Perm_Name']
        print(f'Lambda invoked by a CloudWatch Event for New Permission Set Creation - {newPermName}')
        
        if  newPermName.count('-') == 1:
            psnames_list = [newPermName]

            # Generate existing User group Dictionary for the new Permission Set
            print(f'Fetching existing User groups corresponding to existing AWS Accounts for the new Permission Set - {newPermName}')
            account_name = None # This variable is applicable for new AWS Account event
            #To retrieve all the AWS Account names in the organization, in order to form the User group names
            # This step is necessary as AWS IAM Identity Center API call to list groups takes a mandataory filter of User group name
            # To serach if any User group exists for the new Permission Set, we need to lookup with the User group name
            all_account_list = retrieve_account_information(org_client,account_name,"for_ps_event")
            ad_group_dict = generate_group_dict(ids_id, ids_client, account_name, all_account_list, psnames_list)
            if ad_group_dict:
                print(f'For the new Permission Set existing User groups for existing AWS Accounts found are  - {ad_group_dict.keys()}')               
                # Entitle given Groups to given account ID
                print(f'Entitling existing User groups to the new Permission Set - {newPermName} for access to related AWS Accounts.')
                create_ps_entitlements(sso_id, sso_client, all_account_list, ad_group_dict, newPermissionSet)
            else:
                print(f'NO User groups exist for the new Permission Set - {newPermName}')
                exit()
        else:
            print(f'The newly created Permission Set - {newPermName} DO NOT follow enterprise defined naming standard of permission sets')
            exit()