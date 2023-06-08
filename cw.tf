##################################################
# NEW AWS IAM Identity Center GROUP CREATE EVENT #
##################################################

# EventBridge Rule and Target
resource "aws_cloudwatch_event_rule" "new_user_group" {
  name          = "sso-new-user-group"
  description   = "Event Rule to trigger the role entitlement lambda when a new User Group from external Identity Source has synced."
  event_pattern = <<PATTERN
    {
      "detail": {
        "eventSource": [
          "sso-directory.amazonaws.com"
        ],
        "eventName": [
          "CreateGroup"
        ]
      }
    }
    PATTERN
}

resource "aws_cloudwatch_event_target" "ps_entitle_new_user_group" {
  rule      = aws_cloudwatch_event_rule.new_user_group.name
  target_id = "ps_entitle"
  arn       = aws_lambda_function.sso_automation_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_group_event" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sso_automation_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.new_user_group.arn
  depends_on    = [aws_lambda_function.sso_automation_lambda, aws_cloudwatch_event_rule.new_user_group]
}

############################
# NEW ACCOUNT CREATE EVENT #
############################

resource "aws_cloudwatch_event_rule" "new_account_event" {
  name          = "sso-new-account-event"
  description   = "Event Rules to trigger the role entitlement lambda when a new managed account has been vended under Organization through Control Tower"
  event_pattern = <<EOF
{
  "detail": {
    "serviceEventDetails": {
      "createManagedAccountStatus": {
        "state": [
          "SUCCEEDED"
        ]
      }
    },
    "eventName": [
      "CreateManagedAccount"
    ]
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "ps_entitle_new_account_event" {
  rule      = aws_cloudwatch_event_rule.new_account_event.name
  target_id = "ps_entitle"
  arn       = aws_lambda_function.sso_automation_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_account_event" {
  statement_id  = "AllowExecutionFromCloudWatchAccountVend"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sso_automation_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.new_account_event.arn
  depends_on    = [aws_lambda_function.sso_automation_lambda, aws_cloudwatch_event_rule.new_account_event]
}

###################################
# NEW PERMISSION SET CREATE EVENT #
###################################

resource "aws_cloudwatch_event_rule" "new_permissiont_set" {
  name          = "sso-new-permission-set"
  description   = "Event Rule to trigger the role entitlement lambda when a new Permission Set is created in AWS IAM Identity Center of management account."
  event_pattern = <<PATTERN
    {
      "detail": {
        "eventSource": [
          "sso.amazonaws.com"
        ],
        "eventName": [
          "CreatePermissionSet"
        ]
      }
    }
    PATTERN
}

resource "aws_cloudwatch_event_target" "ps_entitle_new_permission_set" {
  rule      = aws_cloudwatch_event_rule.new_permissiont_set.name
  target_id = "ps_entitle"
  arn       = aws_lambda_function.sso_automation_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_ps_event" {
  statement_id  = "AllowExecutionFromCloudWatchPS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sso_automation_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.new_permissiont_set.arn
  depends_on    = [aws_lambda_function.sso_automation_lambda, aws_cloudwatch_event_rule.new_permissiont_set]
}
