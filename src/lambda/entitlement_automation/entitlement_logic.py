import time
import sys
import json
import os

import boto3

def create_ps_entitlements(sso_id: str, sso_client, all_account_list: list, ad_group_dict: dict, newPermissionSet: dict) -> None:
    entitle_count = 0
    ps_name = newPermissionSet['Perm_Name']
    ps_arn = newPermissionSet['Perm_Arn']
    print(f'Automated Role Entitlement start for the newly created Permission Set - {ps_name}')
    for group, group_arn in ad_group_dict.items():
        account_name =  "-".join(group.split("-")[0:-1])
        for account in all_account_list:
            if account['Name'] == account_name:
                account_id = account['ID']

        print(f'Entitling User group - {group} to Account - {account_name} with Permission Set - {ps_name}')
        attach_entitlement(sso_id, sso_client, account_id, group_arn, ps_arn, ps_name, group)
        entitle_count += 1

    print(f'{entitle_count} entitlement attempts.')

def create_acnt_entitlements(sso_id: str, sso_client, account_id: str, account_name: str, ad_group_dict: dict, sso_permission_sets: dict) -> None:
    entitle_count = 0
    print(f'Automated Role Entitlement start for the newly vended Account - {account_name}')
    for group, group_arn in ad_group_dict.items():
        ps_name = group.split("-")[-1]+"-role"
        if ps_name in sso_permission_sets.keys():
            ps_arn = sso_permission_sets[ps_name]
            print(f'Entitling User group - {group} to Account - {account_name} with Permission Set - {ps_name}')
            attach_entitlement(sso_id, sso_client, account_id, group_arn, ps_arn, ps_name, group)
            entitle_count += 1
        else:
            print(f'Permission Set - {ps_name} for the - User group - {group} NOT PRESENT in AWS IAM Identity center')
    print(f'{entitle_count} entitlement attempts.')

# Attach entitlement to target in account (group, user, etc) - this will provision as well
def attach_entitlement(sso_id: str, sso_client, account_id: str, principle: str, ps_arn: str, ps_name: str, group_name: str) -> None:
    response = sso_client.create_account_assignment(
        InstanceArn=sso_id,
        TargetId=account_id,
        TargetType='AWS_ACCOUNT',
        PermissionSetArn=ps_arn,
        PrincipalType='GROUP',
        PrincipalId=principle
    )

    # Wait for success message
    account_assigned = False
    max_attempts = 50
    attempts = 0
    while account_assigned != True:
        response2 = sso_client.describe_account_assignment_creation_status(InstanceArn=sso_id,AccountAssignmentCreationRequestId=response['AccountAssignmentCreationStatus']['RequestId'])
        if response2['AccountAssignmentCreationStatus']["Status"] == "SUCCEEDED":
            account_assigned = True
            print(f"Success: Attached Permission Set - {ps_name} to AWS Account - {account_id} for AD Group - {group_name}")
            break
        elif response2['AccountAssignmentCreationStatus']["Status"] == "FAILED":
            account_assigned = False
            print(f"ERROR: Unable to attach Permission Set - {ps_name} to AWS Account - {account_id} for AD Group - {group_name}")
            print(f"Response : {response2}")
            break
        else:
            time.sleep(5)
            attempts = attempts + 1
            if attempts > max_attempts:
                break

# This function should eb used for de-provisioining any SSO roles from the environment
def detach_entitlement(sso_client) -> None:
    pass