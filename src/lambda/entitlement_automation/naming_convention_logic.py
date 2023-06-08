import time
import sys
import json
import os
import ast

import boto3

# This module is responsible for handling the naming convention you chose.
# Account_name = aws-<parent OU indicator>-<OU indicator>-<account type / name with numerical counter>
# Permission set template = <job function>-role
# Group_template = ct_env-<account name>-<job function>
# ct_env = DevCT or ProdCT (depending on the Control Tower evnvironment for which the groups are created)

def craft_group_names(account_name: str, all_account_list: list, psnames_list: list) -> list:   
    crafted_groups = []

    if account_name:
        for perm in psnames_list:
            group_acnt = account_name + "-" + perm.split("-")[0]
            crafted_groups.append(group_acnt)
    elif all_account_list and len(psnames_list) == 1:
        for account in all_account_list:
            group_acnt = account['Name'] + "-" + psnames_list[0].split("-")[0]
            crafted_groups.append(group_acnt)

    return crafted_groups