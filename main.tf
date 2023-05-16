terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

# Configure AWS provider
provider "aws" {
  shared_credentials_files = ["~/.aws/credentials"]
  region                   = var.region
}

# Use existing VPC
data "aws_vpc" "c7-vpc" {
  id = "vpc-010fd888c94cf5102"
}

# Use existing subnet
data "aws_db_subnet_group" "c7-subnets" {
  name = "c7-db-subnet-group"
}

# Use existing security group
data "aws_security_group" "c7-remote-access" {
  name   = "c7-remote-access"
  vpc_id = data.aws_vpc.c7-vpc.id
  id     = "sg-01745c9fa38b8ed68"
}


# Create an ECS cluster for the live dashboard
resource "aws_ecs_cluster" "c7-deleton-live-dash-ecs" {
  name = "c7-deleton-live-dash-ecs"


}

# Create an ECS cluster for the API
resource "aws_ecs_cluster" "c7-deleton-api-ecs" {
  name = "c7-deleton-api-ecs"

}
# Create an ECS cluster for the ingestion script
resource "aws_ecs_cluster" "c7-deleton-ingestion-ecs" {
  name = "c7-deleton-ingestion-ecs"

}


# Sets up a free-tier postgres RDS w/ password
resource "aws_db_instance" "deleton-rds" {
  identifier             = "deleton-rds"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  username               = "postgres"
  password               = var.db_password
  publicly_accessible    = true
  skip_final_snapshot    = true
  db_subnet_group_name   = "c7-public-db-subnet-group"
  vpc_security_group_ids = ["sg-01745c9fa38b8ed68"]
  provisioner "local-exec" {

    command = "psql -h ${aws_db_instance.deleton-rds.address} -p 5432 -U \"postgres\" -d \"postgres\" -f \"create_db.sql\""

    environment = {
      PGPASSWORD = "${var.db_password}"
    }
  }
}

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
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-aaa-ecr-daily:latest"
  package_type  = "Image"
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_USER     = "${var.username}"
      DB_PASSWORD = "${var.db_password}"
      DB_HOST     = aws_db_instance.deleton-rds.address
      DB_PORT     = aws_db_instance.deleton-rds.port

    }
  }

}

# Create compress schedule for lambda function 
resource "aws_cloudwatch_event_rule" "c7-schedule-lambda-compress" {
  name                = "c7-schedule-lambda-compress"
  schedule_expression = "rate(1 day)"

}
# Create compress schedule target for lambda function 
resource "aws_cloudwatch_event_target" "c7-schedule-target-compress" {
  rule = aws_cloudwatch_event_rule.c7-schedule-lambda-compress.name
  arn  = aws_lambda_function.c7-deleton-lambda-compress.arn
}

# Create compress trigger prevention
resource "aws_lambda_permission" "allow_compress_event_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c7-deleton-lambda-compress.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.c7-schedule-lambda-compress.arn
}

# Cloudwatch logging for the compress lambda function
resource "aws_cloudwatch_log_group" "c7-deleton-compress-function_log_group" {
  name              = "/aws/lambda${aws_lambda_function.c7-deleton-lambda-compress.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

#  Logging IAM policy
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
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-aaa-ecr-daily:latest"
  package_type  = "Image"
  architectures = ["x86_64"]

  environment {
    variables = {
      ACCESS_KEY  = "${var.access_key}"
      SECRET_KEY  = "${var.secret_key}"
      DB_USER     = "${var.username}"
      DB_NAME     = "${var.username}"
      DB_PASSWORD = "${var.db_password}"
      DB_HOST     = aws_db_instance.deleton-rds.address
      DB_PORT     = aws_db_instance.deleton-rds.port
    }
  }
}


# Create daily generate schedule for lambda function 
resource "aws_cloudwatch_event_rule" "c7-schedule-lambda-daily-generate" {
  name                = "c7-schedule-lambda-daily-generate"
  schedule_expression = "rate(1 day)"

}

# Create daily-generate schedule target for lambda function 
resource "aws_cloudwatch_event_target" "c7-schedule-target-daily-generate" {
  rule = aws_cloudwatch_event_rule.c7-schedule-lambda-daily-generate.name
  arn  = aws_lambda_function.c7-deleton-lambda-daily-generate.arn
}

# Create daily-generate trigger prevention
resource "aws_lambda_permission" "allow_daily-generate_event_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c7-deleton-lambda-daily-generate.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.c7-schedule-lambda-daily-generate.arn
}

# Cloudwatch logging for the daily generate lambda function
resource "aws_cloudwatch_log_group" "c7-deleton-daily-generate-function_log_group" {
  name              = "/aws/lambda${aws_lambda_function.c7-deleton-lambda-daily-generate.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
