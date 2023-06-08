# Lambda Source Codes 

This folder contains the lambda function with all the methods that conducts various tasks to achieve the automation of user group assignment to permission sets for accssing specific AWS accounts.

## `ps_entitle.py`
This python scripts contains the main method - *`def lambda_handler()`* of the lambda function. The code is executed from this method. 

  `def lambda_handler()`
  * This method has three logical blocks each represents one of the three events that triggers the lambda
  * With every invocation of the lambda fucntion only one of the three `if-else` blocks will be executed (based on which event trigerres the lambda)

  `def generate_group_dict()` 
  * This method is used to form a dictionary of User group names and their corresponding group IDs as the groups IDs are required for AWS IAM Identity Center to perform the permission assignment
  * This method calls another method - `craft_group_names()` (defined in `naming_convention_logic.py` script) to first form the User group names by passing the AWS account names and Permission Set names based on the event trigger
  * Finally this method check if the crafted User group is present in AWS IAM Identity Center and if yes then fetch the Group ID and ultimately pass to the main method - `lambda_handler()`

  `generate_sso_permission_set_dict()`
  * This method generates the a dictionary of all the Permission Sets that exists in AWS IAM Identity center instance
  * It returns the permission set information as a key value pair with key - permission set name and value - ARN of the permission set
  * These information are required for doing the permission assignment
  
## `account_logic.py`
This pyhton script contains only one method that is used for retrieving information about specific or all AWS accounts under the AWS organization

  `retrieve_account_information()`
  * This method is called by the main method for fetching AWS account information in case of a new User group creation event or a new Permission Set creation event
  * For a new User group creation event, this method is called to fetch the Account ID of the specific account name that is found in the new User group
  * For a new Permission Set event, this method is called to fetch all the existing AWS Account's IDs 

## `naming_convention_logic.py`
This python script contains only one method that is used to build User group names following the AWS Account name and Permission Set names

  `craft_group_names()`
  * This method is called by the main method for forming User group names by appending AWS account name and the <job_function> field of Permission Set name. 
  * For a new AWS Account creation event, this method is called to form User group names with the specific name of the newly created AWS account and appending the <job_function> of each of the baseline permission sets passed as an input paramater. 
  * For a new Permission Set event, this method is called to form User group names by appending the account name of each AWS Account (in the organization) with the specific <job_function> of the newly created permission set
  * The method returns a list of User group names which are then evaluated in the `generate_group_dict()` method for existence in the AWS IAM Identity Center instance

## `entitlement_logic.py`
This python script contains the method to perform a permission set assignment to a user group for accessing an AWS Account via IAM role. It also contains methods that call the permission entitlement method in a loop for bulk assignments depending on the trigerred event.  

  `attach_entitlement()`
  * This method performs the API call [`sso-admin.create_account_assignment()`] to AWS IAM Identity Center for assigning a permission set Arn to a User group ID for accessing a target Account ID with role-based federated access
  * This method checks for the assignment status and accordingly returns a response.
  
  `create_ps_entitlements()`
  * This method is called for performing bulk assignments in case of a new Permission Set creation event
  * For a new Permission Set, there is a possibility of assigning the new permission set to multiple User groups for accessing multiple AWS Accounts. Hence, this method is used to call the `attach_entitlement()` method in a loop to assign all the User groups found in the organization created for the new Permission Set
  
  `create_acnt_entitlements()`
   * This method is called for performing bulk assignments in case of a new AWS Account creation event
   * For a new AWS Account, a baseline set of roles are required to access the account. Hence, this method is used to call the `attach_entitlement()` method in a loop to assign all the User groups found in the organization created for the new AWS Account

  `detach_entitlement()`
  * An empty method provided for future enhancement of creating the de-provisioning of permission sets to User groups for specific AWS acocunts
