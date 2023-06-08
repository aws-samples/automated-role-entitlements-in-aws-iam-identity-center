import time
import sys
import json
import os

import boto3

# Querying Organizations here for every account and then looping until finding the right one is inefficient
# However, if as part of your Account Vending Pipeline you store account metadata into a database of some sort
# here is where you will change to functionality to return what you need through whatever method you can
def retrieve_account_information(org_client, account_name: str, purpose:str):
    response = org_client.list_accounts()

    accounts = response['Accounts']

    while 'NextToken' in response and response['NextToken']:
        response = org_client.list_accounts(
            NextToken=response['NextToken']
        )
        accounts.extend(response['Accounts'])

    if purpose == "for_group_event":
        for account in accounts:
            if account['Name'] == account_name:
                return account['Id']
        print(f'The account_name - {account_name} retrieved from User group name is not found in organizations.ListAccounts')
        exit()
    elif purpose == "for_ps_event":
        account_list = []
        account_dict = {}
        for account in accounts:
            account_dict['Name'] = account['Name']
            account_dict['ID'] = account['Id']
            account_list.append(account_dict.copy())
        return account_list