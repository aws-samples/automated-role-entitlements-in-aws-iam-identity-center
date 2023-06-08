##################################
# SSO AUTOMATION LAMBDA CREATION #
##################################

data "archive_file" "sso_automation_archive" {
  type        = "zip"
  source_dir  = "${path.module}/src/lambda/entitlement_automation/"
  output_path = "${path.module}/src/lambda/entitlement_automation_archive/entitlement_automation.zip"
}

# Deploy the sso assignment automation lambda
resource "aws_lambda_function" "sso_automation_lambda" {
  function_name    = "sso-assignment-automation-lambda"
  description      = "Lambda for sso role entitlement automation. This lambda is triggered by one of two potential events and will entitle groups with permission sets to an account based on naming convention."
  role             = aws_iam_role.lambda_role.arn
  memory_size      = 512
  runtime          = "python3.9"
  timeout          = 300
  handler          = "ps_entitle.lambda_handler"
  filename         = "${path.module}/src/lambda/entitlement_automation_archive/entitlement_automation.zip"
  source_code_hash = data.archive_file.sso_automation_archive.output_base64sha256
  environment {
    variables = {
      new_acnt_perms = jsonencode(var.new_acnt_perms)
    }
  }
}