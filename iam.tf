############################
# IAM Resources for Lambda #
############################
resource "aws_iam_role" "lambda_role" {
  name               = "sso-assignment-lambda-role"
  description        = "Role assigned to sso-assignment-lambda for interacting with IAM Identity Center and Organizations"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_permissions_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_managed_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "sso-assignment-lambda-policy"
  description = "Policy assigned to sso-assignment-lambda-role to give permissions for interacting with IAM Identity center and Organizations"
  policy      = data.aws_iam_policy_document.lambda_permissions.json
}

data "aws_iam_policy_document" "lambda_role_trust_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid    = "IdentityReadpermissions"
    effect = "Allow"
    actions = [
      "sso:ListPermissionSets",
      "sso:DescribeAccountAssignmentCreationStatus",
      "sso:DescribePermissionSet",
      "sso:ListInstances",
      "iam:GetSAMLProvider",
      "organizations:ListTagsForResource",
      "organizations:ListAccounts",
      "identitystore:ListGroups"
    ]
    resources = [
      "*",
    ]
  }
  statement {
    sid    = "IdentityCenterWritepermissions"
    effect = "Allow"
    actions = [
      "sso:CreateAccountAssignment"
    ]
    resources = [
      "*",
    ]
  }

}
