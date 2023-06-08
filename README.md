# Automated Role Entitlements in AWS IAM Identity Center

This purpose of this solution is to help you automate user group assignment to permission sets in AWS IAM Identity Center for accessing any or all AWS accounts in your organization via federated access following principles of least privilege.

This repository contains the infrastcruture-as-code written in Terraform (CloudFormation version coming soon) that deploys all the AWS resources necessary for the role entitlement automation.

An APG guide is coming soon that explains details on role entitlements in AWS IAM Identity Center and how this automation of role entitlements can benefit an enterprise in scaling their access management infrasctruture. 
## Table of Contents
1. [Solution Overview](#solution-overview)
2. [Prerequisites](#prerequisites)
3. [Solution Architecture](#solution-architecture)
4. [AWS Resources required for the automation](#aws-resources-required-for-the-automation)
5. [Code Structure](#code-structure)
6. [Deployment Instructions](#deployment-instructions)
7. [Next Steps](#next-steps)
8. [Conclusion](#conclusion)

## Solution Overview
AWS IAM Identity Center (formally [AWS Single Sign-On](https://aws.amazon.com/iam/identity-center/)) gives you the ability to manage permissions and assignments for accessing your AWS Accounts. AWS IAM Identity Center gives you the power for centralized management of your AWS IAM Identity Center users, groups, and permission sets as well as assignment for the entire [AWS Organization that manages multiple accounts](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/core-concepts.html). In order to achieve federated role-based access of enterprise users to the AWS accounts through AWS IAM Identity Center, we need to follow two major steps:

* Create permission sets
* Assign access to the external Active Directory (AD) or Identity Provider (IdP) group users to the appropriate AWS Account using permission sets (see [Key AWS IAM Identity Center Concepts](https://docs.aws.amazon.com/singlesignon/latest/userguide/understanding-key-concepts.html) for reference).

This solution is intended to minimize the amount of work needed around AWS IAM Identity Center group and permission set entitlement process. By programmatically entitling user groups (of your enterprise's workforce directory) with their respective permission sets and its subsequent account assignment you can ensure you are rightfully entitling access with consistency and scale. Further, this will remove human intervention from the role entitlement process by using an event driven architecture.

The core of this user group to permission assignment automation is through naming conventions between User Groups, Permission Sets and AWS Accounts.

## Prerequisites
* AWS Organizations enabled with **All Features**
* AWS IAM Identity Center enabled (in the organization's management account)
* A standard naming convention of your:
    1. AWS Accounts
    2. Enterprise user groups (in your enterprise identity source)
    3. Permission sets in IAM Identity Center
* Use of AWS Control Tower Account Factory to generate managed accounts.

## Solution Architecture
In this solution we consider an external IdP is used in your organization for federated access of corporate users to the AWS environment

![Automation Architecture](/sso_automation_diag.png)

## AWS Resources created for the automation
Role entitlement in IAM Identity Center involves three components – a user group who needs access, a permission set that defines what type of access should be given to the user group and an AWS account that indicates where the user need access. The need for role entitlement occurs in the event of creation of any of these three components. 

The AWS resources created for this automation are:
•	One AWS Lambda function written in Python using Boto3 
•	Three Amazon EventBridge Event Rules to monitor three different events - when a new SSO Group, a new permission set or a new AWS account is created. Accordingly, it will trigger the Lambda function.

The automation resources are deployed using Terraform.

Considering all the possible resource creation events, this automation solution is trigerred based on the following events:
1. Event - `CreateGroup` API call, which is generated when a new user group is synced to AWS IAM Identity Center via SCIM protocol after the group is created on an enterprise's identity source
2. Event - `CreatePermissionSet` API call, which is generated when a new Permission Set is created in the AWS IAM Identity Center.
3. Event - `CreateManagedAccount` API call, which is generated when a new AWS Account is created in the Control Tower environment 
## Code Structure

The resources of this solution are only built in the Management Account of the Control Tower organization

### Standard Naming templates
Following least privilege access model, many organization prefer to have different levels of permissions for the same enterprise team for different working environment. A most common use-case - the security engineering team should have different types of security access in production accounts and development accounts.
  
1. Account_name | `<account name>` = `aws-< OU indicator>-<environment>-<account type / name with numerical counter>`
2. Permission set name = `<job function>-role`
3. User Group name = `<account name>-<job function>`

Keyword Details
- `OU indicator` - a keyword that indicates the organization unit (OU) to which the AWS account belongs
- `environment` - a keyword to indicate the whether this account belongs to a Dev / test / Prod environment 
- `account type` - a keyword that defines the functionalities of this account. If this account is to host networking resources or security resources and accordingly the indicator can be `network` or `security` or similar. 
- `name with numerical counter` - a keyword useful to add if in your enterprise you are creating more than one AWS account of the same category. For example in an enterprise, each AWS account host a business application then this keyword can be leveraged to call out the application name or a relevant keyword.
- `job function` - a keyword that defines the role taker's department or job category. For example, if the departmenmt is Networking team and they need a role for network adminsitration work then this indicator can be `NetworkAdmin`

> NOTE: **The common delimiter chosen for the standardised naming is `-`. Thus if you want to put any delimeter in the names of the above mentioned keywords then please use any special character BUT NOT `-` as this may confuse the automation logic that parses the resources names based on the common delimiter `-`.** For example if your job function is Security Enginner then you can define the keyword as `security_eng` OR `SecurityEng` or anything **but not `security-admin`**

All these above mentioned keywords are to provide you with a guidance for standard naming convention and is not restricted to these keywords only. Based on your enterprise requirements and AWS organization setup you can change these keywords for consuming this automated role entitlement solution.

### Scripts
* `iam.tf` - creates the IAM role and IAM policy assumed by the automation Lambda function to perform the role entitlement activities
* `lambda.tf` - creates the Lambda function that perfrom the role entitlement to user groups for accessing AWS accounts based on the trigerred events
* `cw.tf` - creates three EventBridge rules that monitors the organization environment and triggers the Lambda function for any of the three API events - **CreateGroup**, **CreateManagedAccount** and **CreatePermissionSet**
* `variables.tf` - defines any input paramaters to be passed to the automation code
* `terraform.tfvars` - this file is used to pass any value at run time to the input paramaters of the automation code
* `backend.tf` - this file is used to define the terraform provider and state file storage location
* `providers.tf` - this file defines the provider details that includes required Terraform version for AWS and the AWS account credential details. 

This folder contains one sub-folder [src/lambda/entitlement_automation](/src/lambda/entitlement_automation) which stores the Lambda function code - python scripts and its functionalities
## Deployment Instructions

> NOTE: This solution should be deployed only in the management account of your AWS organization.

**To deploy the resources directly from your local machine**, do the following:

### Prerequisites
Make sure you have the following installed on your local machine:
1. Terraform. [Refer here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) for installation details.
2. AWS CLI. [Refer here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for installation details.

### Steps
1. Download the code repository
2. Next 
```
cd automated-role-entitlements-in-iam-identity-center
```
3. Edit the `providers.tf` file to change the following and save the file:
    * **profile** - change the profile to the specifc credentials you use to access the management account of your AWS organization
    * **region** - change the region to the specific region where you have enabled AWS IAM Identity Center
4. Execute the following terraform commands on the cli
```
terraform init
terraform validate
terraform plan
terraform apply
```

You can also integrate this repository into your organization's CI'CD pipeline for automated deployment. For CI/CD deployment, you will change the `providers.tf` file with the profile used by the pipeline role to access your organization's management account.
## Next Steps

After successful deployment of the automation resources, you can now start creating new Permission Sets, User groups and AWS Accounts. The automation is trigerred on creation of any of the above three resources but the role entitlement will not occur if any of the three resources is missing or not yet created. The automation is built considering all exception scenarios hence incase one of the three resources is missing, the automation will wait and complete the role entitlement once the missing resourvce gets created.

As further next steps, you can stat scaling role entitlement process for your entire organization by integrating this solution through the CI/CD pipeline.
The CloudFormation version of the same solution is coming soon. Meanwhile feel free to contribute to this repository with your enhancements to the current solution.

## Conclusion
This solution shows how to automate AWS IAM Identity Center permission assignment to user groups using IaC - Terraform. You can integrate this solution in your CI/CD pipeline and have the automation triggered when the pipeline creates a new AWS Account or a new enterprise user group or a new Permission Set in your AWS environment.

