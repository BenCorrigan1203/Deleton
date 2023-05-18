# Create an ECS cluster for the API
resource "aws_ecs_cluster" "c7-deleton-ecs-cluster" {
  name = "c7-deleton-ecs-cluster"
}
# Create an ECS task execution role
resource "aws_iam_role" "c7-deleton-ecs_task_execution_role" {
  name = "c7-deleton-ecs_task_execution_role"

  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "ecs-tasks.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}
# Create ECS task role
resource "aws_iam_role" "c7-deleton-ecs_task_role" {
  name = "c7-deleton-ecs_task_role"

  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "ecs-tasks.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

# Attach a policy to ECS task execution role 
resource "aws_iam_role_policy_attachment" "c7-deleton-ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.c7-deleton-ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create the ingestion script task definition
resource "aws_ecs_task_definition" "c7-deleton-ingestion-task-definition" {
  family                   = "c7-deleton-ingestion-task-definition"
  task_role_arn            = aws_iam_role.c7-deleton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deleton-ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  requires_compatibilities = ["FARGATE"]

  runtime_platform {
    cpu_architecture = "ARM64"
  }

  container_definitions = <<DEFINITION
  [
    {
      "name": "project-container",
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-ingestion-script:latest",
      "environment": [
        {"name": "ACCESS_KEY", "value":   "${var.ACCESS_KEY}"},
        {"name": "SECRET_KEY", "value":   "${var.SECRET_KEY}"},
        {"name": "DB_PASSWORD", "value":  "${var.DB_PASSWORD}"},
        {"name": "DB_USER", "value":       "${var.DB_USER}"},
        {"name": "DB_NAME", "value":      "${var.DB_NAME}"},
        {"name": "DB_PORT", "value":       "${var.DB_PORT}"},
        {"name": "DB_HOST", "value":     "${var.DB_HOST}"},
        {"name": "SCHEMA", "value":      "${var.SCHEMA}"},
        {"name": "CONSUMER_GROUP","value":"${var.CONSUMER_GROUP}"},
        {"name": "TOPIC", "value":         "${var.TOPIC}"},
        {"name": "BOOTSTRAP_SERVERS","value": "${var.BOOTSTRAP_SERVERS}"},
        {"name": "SASL_USERNAME", "value": "${var.SASL_USERNAME}"},
        {"name": "SASL_PASSWORD", "value": "${var.SASL_PASSWORD}"}
      ]

    }
  ]
  DEFINITION
}

# Create a ECS Service for the ingestion script
resource "aws_ecs_service" "c7-deleton-ingestion-task-service" {
  name            = "c7-deleton-ingestion-task-service"
  cluster         = aws_ecs_cluster.c7-deleton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deleton-ingestion-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]
  }

}

# Create the API task definition
resource "aws_ecs_task_definition" "c7-deleton-api-task-definition" {
  family                   = "c7-deleton-api-task-definition"
  task_role_arn            = aws_iam_role.c7-deleton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deleton-ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  requires_compatibilities = ["FARGATE"]

  runtime_platform {
    cpu_architecture = "ARM64"
  }

  container_definitions = <<DEFINITION
  [
    {
      "name": "project-container",
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-ingestion-script:latest",
      "environment": [
        {"name": "ACCESS_KEY", "value":   "${var.ACCESS_KEY}"},
        {"name": "SECRET_KEY", "value":   "${var.SECRET_KEY}"},
        {"name": "DB_PASSWORD", "value":  "${var.DB_PASSWORD}"},
        {"name": "DB_USER", "value":       "${var.DB_USER}"},
        {"name": "DB_NAME", "value":      "${var.DB_NAME}"},
        {"name": "DB_PORT", "value":       "${var.DB_PORT}"},
        {"name": "DB_HOST", "value":     "${var.DB_HOST}"},
        {"name": "SCHEMA", "value":      "${var.SCHEMA}"},
        {"name": "CONSUMER_GROUP","value":"${var.CONSUMER_GROUP}"},
        {"name": "TOPIC", "value":         "${var.TOPIC}"},
        {"name": "BOOTSTRAP_SERVERS","value": "${var.BOOTSTRAP_SERVERS}"},
        {"name": "SASL_USERNAME", "value": "${var.SASL_USERNAME}"},
        {"name": "SASL_PASSWORD", "value": "${var.SASL_PASSWORD}"}
      ]

    }
  ]
  DEFINITION
}

# Create a ECS Service for the API script
resource "aws_ecs_service" "c7-deleton-api-task-service" {
  name            = "c7-deleton-api-task-service"
  cluster         = aws_ecs_cluster.c7-deleton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deleton-api-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]
  }

}

# Create the live dashboard task definition
resource "aws_ecs_task_definition" "c7-deleton-live-dash-task-definition" {
  family                   = "c7-deleton-live-dash-task-definition"
  task_role_arn            = aws_iam_role.c7-deleton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deleton-ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  requires_compatibilities = ["FARGATE"]

  runtime_platform {
    cpu_architecture = "ARM64"
  }

  container_definitions = <<DEFINITION
  [
    {
      "name": "project-container",
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-ingestion-script:latest",
      "environment": [
        {"name": "ACCESS_KEY", "value":   "${var.ACCESS_KEY}"},
        {"name": "SECRET_KEY", "value":   "${var.SECRET_KEY}"},
        {"name": "DB_PASSWORD", "value":  "${var.DB_PASSWORD}"},
        {"name": "DB_USER", "value":       "${var.DB_USER}"},
        {"name": "DB_NAME", "value":      "${var.DB_NAME}"},
        {"name": "DB_PORT", "value":       "${var.DB_PORT}"},
        {"name": "DB_HOST", "value":     "${var.DB_HOST}"},
        {"name": "SCHEMA", "value":      "${var.SCHEMA}"},
        {"name": "CONSUMER_GROUP","value":"${var.CONSUMER_GROUP}"},
        {"name": "TOPIC", "value":         "${var.TOPIC}"},
        {"name": "BOOTSTRAP_SERVERS","value": "${var.BOOTSTRAP_SERVERS}"},
        {"name": "SASL_USERNAME", "value": "${var.SASL_USERNAME}"},
        {"name": "SASL_PASSWORD", "value": "${var.SASL_PASSWORD}"}
      ]

    }
  ]
  DEFINITION
}

# Create a ECS Service for the live dashboard 
resource "aws_ecs_service" "c7-deleton-live-dash-task-service" {
  name            = "c7-deleton-api-task-service"
  cluster         = aws_ecs_cluster.c7-deleton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deleton-live-dash-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]
  }

}
