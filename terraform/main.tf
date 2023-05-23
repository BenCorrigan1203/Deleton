# Creating Lambda and Step functions
# Creata lambda IAM policy
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# Creata lambda IAM role
resource "aws_iam_role" "lambda-role" {
  name_prefix = "iam-c7-deleton-for-lambda"
  #  = "iam-deleton-for-lambda"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [{
      "Action" : "sts:AssumeRole",
      "Principal" : {
        "Service" : "lambda.amazonaws.com"
      },
      "Effect" : "Allow"
    }]
  })
}

# Create compress lambda function
resource "aws_lambda_function" "c7-deleton-lambda-compress" {
  function_name = "c7-deleton-lambda-compress"
  role          = aws_iam_role.lambda-role.arn
  memory_size   = 3010
  timeout       = 120
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-compression-script:latest"
  package_type  = "Image"
  architectures = ["arm64"]

  environment {
    variables = {
      DB_USER     = "${var.DB_USER}"
      DB_PASSWORD = "${var.DB_PASSWORD}"
      DB_HOST     = aws_db_instance.deleton-rds.address
      DB_PORT     = aws_db_instance.deleton-rds.port

    }
  }
}

# Cloudwatch logging for the compress lambda function
resource "aws_cloudwatch_log_group" "c7-deleton-compress-function_log_group" {
  name              = "/aws/lambda${aws_lambda_function.c7-deleton-lambda-compress.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

# Logging IAM policy
resource "aws_iam_policy" "function_logging_policy" {
  name = "function-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}
# Logging policy attachment
resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.lambda-role.id
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

# Create daily generate lambda function
resource "aws_lambda_function" "c7-deleton-lambda-daily-generate" {
  function_name = "c7-deleton-lambda-daily-generate"
  role          = aws_iam_role.lambda-role.arn
  memory_size   = 3010
  timeout       = 120
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-report-generation:latest"
  package_type  = "Image"
  architectures = ["arm64"]

  environment {
    variables = {
      ACCESS_KEY  = "${var.ACCESS_KEY}"
      SECRET_KEY  = "${var.SECRET_KEY}"
      DB_USER     = "${var.DB_USER}"
      DB_NAME     = "${var.DB_NAME}"
      DB_PASSWORD = "${var.DB_PASSWORD}"
      DB_HOST     = aws_db_instance.deleton-rds.address
      DB_PORT     = aws_db_instance.deleton-rds.port
    }
  }
}

# Cloudwatch logging for the daily generate lambda function
resource "aws_cloudwatch_log_group" "c7-deleton-daily-generate-function_log_group" {
  name              = "/aws/lambda${aws_lambda_function.c7-deleton-lambda-daily-generate.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

# Create role 
resource "aws_iam_role" "step_function_execution_role" {
  name               = "step_function_execution_role"
  assume_role_policy = <<-EOF
  {
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": ["states.amazonaws.com", "events.amazonaws.com"]
        },
        "Effect": "Allow",
        "Sid": "StepFunctionAssumeRole"
      }
    ]
  }
  EOF
}

# Create role policy
resource "aws_iam_role_policy" "step_function_execution_role_policy" {
  name = "step_function_execution_role_policy"
  role = aws_iam_role.step_function_execution_role.id

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "states:StartExecution"
        ],
        "Resource": "${aws_sfn_state_machine.deleton_state_machine.arn}"
        
      }
    ]
  }
  EOF
}

# Create role and policy for step function to execute lambdas
resource "aws_iam_role" "step_function_role" {
  name               = "step_function_role"
  assume_role_policy = <<-EOF
  {
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "states.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": "StepFunctionAssumeRole"
      }
    ]
  }
  EOF
}

# Create role policy for step function
resource "aws_iam_role_policy" "step_function_policy" {
  name = "step_function_policy"
  role = aws_iam_role.step_function_role.id

  policy = <<-EOF
  {
    "Statement": [
      {
        "Action": [
          "lambda:InvokeFunction"
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:lambda:eu-west-2:605126261673:function:*"
      }
    ]
  }
  EOF
}

# Create step-function
resource "aws_sfn_state_machine" "deleton_state_machine" {
  name     = "deleton-state-machine"
  role_arn = aws_iam_role.step_function_role.arn

  definition = <<EOF
{
  "Comment": "State machine for the deleton group project",
  "StartAt": "Compress Data",
  "States": {
    "Compress Data": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.c7-deleton-lambda-compress.arn}",
      "Next": "Generate Report"
    },
    "Generate Report": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.c7-deleton-lambda-daily-generate.arn}",
      "End": true
    }
  }
}
EOF
}

# Create schedule for step function
resource "aws_cloudwatch_event_rule" "step_function_schedule" {
  name                = "deleton-daily-step-function"
  description         = "Run step function at 6 PM everyday"
  schedule_expression = "cron(0 17 * * ? *)"
}

# Create event target for step function
resource "aws_cloudwatch_event_target" "target" {
  rule     = aws_cloudwatch_event_rule.step_function_schedule.name
  arn      = aws_sfn_state_machine.deleton_state_machine.arn
  role_arn = aws_iam_role.step_function_execution_role.arn
}
