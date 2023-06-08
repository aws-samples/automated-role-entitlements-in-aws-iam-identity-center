#####################################################################
# This file is used to pass any runtime variable values to the code #
#####################################################################

new_acnt_perms = [
  "FullAdmin-role",     #applicable only for Cloud Infrastructure team to assume in All AWS Accounts in case of operational emergency
  "ReadOnly-role",      #applicable to all enterprise users who wants to view resources in any AWS Accounts under the enterprise's AWS organization
  "SecurityAdmin-role", #applicable only for InfoSec Team to assume in any AWS Account under the organization for managing any security specific tasks (that cannot be done via pipeline)
  "SecurityAudit-role", #applicable only for External / Internal Auditors to assume in any of the AWS Accounts
  "SecurityIREng-role"  #applicable only for Incident response team to assume in case of any security events in any of the AWS Accounts
]