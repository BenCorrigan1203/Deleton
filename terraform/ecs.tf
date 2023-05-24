# Create an ECS cluster for the API
resource "aws_ecs_cluster" "c7-deloton-ecs-cluster" {
  name = "c7-deloton-ecs-cluster"
  depends_on = [
    aws_db_instance.deloton-rds
  ]
}
# Create an ECS task execution role
resource "aws_iam_role" "c7-deloton-ecs_task_execution_role" {
  name = "c7-deloton-ecs_task_execution_role"

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
resource "aws_iam_role" "c7-deloton-ecs_task_role" {
  name = "c7-deloton-ecs_task_role"

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
resource "aws_iam_role_policy_attachment" "c7-deloton-ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.c7-deloton-ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create the ingestion script task definition
resource "aws_ecs_task_definition" "c7-deloton-ingestion-task-definition" {
  family                   = "c7-deloton-ingestion-task-definition"
  task_role_arn            = aws_iam_role.c7-deloton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deloton-ecs_task_execution_role.arn
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
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-ingestion-script:latest",
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "eu-west-2",
          "awslogs-group": "${aws_cloudwatch_log_group.c7-deloton-ingestion-watchgroup.name}",
          "awslogs-stream-prefix": "c7-deloton-container"
        }},
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
resource "aws_ecs_service" "c7-deloton-ingestion-task-service" {
  name            = "c7-deloton-ingestion-task-service"
  cluster         = aws_ecs_cluster.c7-deloton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deloton-ingestion-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]
  }
  # service_connect_configuration {
  #   namespace = aws_service_discovery_http_namespace.c7-deloton-ecs-service-namespace.name
  #   enabled   = true
  #   log_configuration {

  #     log_driver = "awslogs"
  #     options = {
  #       "awslogs-group" : "${aws_cloudwatch_log_group.c7-deloton-ingestion-watchgroup.name}",
  #       "awslogs-region" : "eu-west-2",
  #       "awslogs-stream-prefix" : "ecs"

  #     }
  #   }
  # }

}
resource "aws_service_discovery_http_namespace" "c7-deloton-ecs-service-namespace" {
  name        = "c7-deloton-ecs-service-namespace"
  description = "example"
}

resource "aws_cloudwatch_log_group" "c7-deloton-ingestion-watchgroup" {
  name              = "c7-deloton-ingestion-watchgroup"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "c7-deloton-api-watchgroup" {
  name              = "c7-deloton-api-watchgroup"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}


# Create the API task definition
resource "aws_ecs_task_definition" "c7-deloton-api-task-definition" {
  family                   = "c7-deloton-api-task-definition"
  task_role_arn            = aws_iam_role.c7-deloton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deloton-ecs_task_execution_role.arn
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
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-api:latest",
      "portMappings": [
      {
        "containerPort": 8080,
        "protocol": "tcp"
      }
    ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "eu-west-2",
          "awslogs-group": "${aws_cloudwatch_log_group.c7-deloton-api-watchgroup.name}",
          "awslogs-stream-prefix": "c7-deloton-container"
        }},
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
resource "aws_ecs_service" "c7-deloton-api-task-service" {
  name            = "c7-deloton-api-task-service"
  cluster         = aws_ecs_cluster.c7-deloton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deloton-api-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]

  }
  load_balancer {
    target_group_arn = aws_lb_target_group.c7-deloton-api-lb-target-group.arn
    container_name   = "project-container"
    container_port   = 8080
  }

}

# Create cloudwatch log group
resource "aws_cloudwatch_log_group" "c7-deloton-live-dash-watchgroup" {
  name              = "c7-deloton-live-dash-watchgroup"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

# Create a cloudwatch log stream for the api
resource "aws_cloudwatch_log_stream" "c7-deloton-api-cloudwatch-logstream" {
  name           = "c7-deloton-api-cloudwatch-logstream"
  log_group_name = aws_cloudwatch_log_group.c7-deloton-api-watchgroup.name
}
# Create a cloudwatch log stream for the ingestion
resource "aws_cloudwatch_log_stream" "c7-deloton-ingestion-cloudwatch-logstream" {
  name           = "c7-deloton-ingestion-cloudwatch-logstream"
  log_group_name = aws_cloudwatch_log_group.c7-deloton-ingestion-watchgroup.name
}
# Create a cloudwatch log stream for the live dash
resource "aws_cloudwatch_log_stream" "c7-deloton-live-dash-cloudwatch-logstream" {
  name           = "c7-deloton-live-dash-cloudwatch-logstream"
  log_group_name = aws_cloudwatch_log_group.c7-deloton-live-dash-watchgroup.name
}

# Create the live dashboard task definition
resource "aws_ecs_task_definition" "c7-deloton-live-dash-task-definition" {
  family                   = "c7-deloton-live-dash-task-definition"
  task_role_arn            = aws_iam_role.c7-deloton-ecs_task_role.arn
  execution_role_arn       = aws_iam_role.c7-deloton-ecs_task_execution_role.arn
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
      "image": "605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-live-dashboard:latest",
      "portMappings": [
      {
        "containerPort": 8080,
        "protocol": "tcp"
      }
    ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "eu-west-2",
          "awslogs-group": "${aws_cloudwatch_log_group.c7-deloton-live-dash-watchgroup.name}",
          "awslogs-stream-prefix": "c7-deloton-container"
        }},
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
resource "aws_ecs_service" "c7-deloton-live-dash-task-service" {
  name            = "c7-deloton-live-dash-task-service"
  cluster         = aws_ecs_cluster.c7-deloton-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c7-deloton-live-dash-task-definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    assign_public_ip = true
    subnets          = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
    security_groups  = ["sg-01745c9fa38b8ed68"]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.c7-deloton-live-dash-lb-target-group.arn
    container_name   = "project-container"
    container_port   = 8080
  }
}


# Create a Load Balancer for API
resource "aws_lb" "c7-deloton-api-lb" {
  name               = "c7-deloton-api-lb"
  load_balancer_type = "application"
  subnets            = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
  security_groups    = ["sg-01745c9fa38b8ed68"]
}
# Create Load Balancer target group for the API
resource "aws_lb_target_group" "c7-deloton-api-lb-target-group" {
  name        = "c7-deloton-api-lb-target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.c7-vpc.id
}
# Create Load Balancer listener for the API
resource "aws_lb_listener" "c7-deloton-api-lb-listener" {
  load_balancer_arn = aws_lb.c7-deloton-api-lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.c7-deloton-api-lb-target-group.arn
    type             = "forward"
  }
}


# Create a Load Balancer for Live dashboard
resource "aws_lb" "c7-deloton-live-dash-lb" {
  name               = "c7-deloton-live-dash-lb"
  load_balancer_type = "application"
  subnets            = ["subnet-0bd43551b596597e1", "subnet-0b265a90c0cadfb99", "subnet-07f982f51c870f9d1"]
  security_groups    = ["sg-01745c9fa38b8ed68"]
}
# Create Load Balancer target group for Live dashboard
resource "aws_lb_target_group" "c7-deloton-live-dash-lb-target-group" {
  name        = "c7-deloton-livedash-target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.c7-vpc.id
}

# Create Load Balancer listener for the Live dashboard
resource "aws_lb_listener" "c7-deloton-live-dash-lb-listener" {
  load_balancer_arn = aws_lb.c7-deloton-live-dash-lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.c7-deloton-live-dash-lb-target-group.arn
    type             = "forward"
  }
}
