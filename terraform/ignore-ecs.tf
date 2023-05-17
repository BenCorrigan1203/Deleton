# # # Create an ECS cluster for the live dashboard
# # resource "aws_ecs_cluster" "c7-deleton-live-dash-ecs" {
# #   name = "c7-deleton-live-dash-ecs"


# # }

# # # Create an ECS cluster for the API
# # resource "aws_ecs_cluster" "c7-deleton-api-ecs" {
# #   name = "c7-deleton-api-ecs"

# # }
# # # Create an ECS cluster for the ingestion script
# # resource "aws_ecs_cluster" "c7-deleton-ingestion-ecs" {
# #   name = "c7-deleton-ingestion-ecs"

# # }

# # Create a task definition 
# resource "aws_ecs_task_definition" "task-definition" {
#   family                   = "task-definition"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   execution_role_arn       = aws_iam_role.task_execution.arn
#   cpu                      = 1024
#   memory                   = 2048

#   container_definitions = <<TASK_DEFINITION
# [
#   {
#     "name": "iis",
#     "image": "mcr.microsoft.com/windows/servercore/iis",
#     "cpu": 1024,
#     "memory": 2048,
#     "essential": true
#   }
# ]
# TASK_DEFINITION

#   runtime_platform {
#     operating_system_family = "WINDOWS_SERVER_2019_CORE"
#     cpu_architecture        = "X86_64"
#   }

# }

# # Create an IAM role for task
# resource "aws_iam_role" "task_execution" {
#   name = "task-excution_role"

#   assume_role_policy = <<POLICY
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Action": "sts:AssumeRole",
#       "Principal": {
#         "Service": "ecs-tasks.amazon.com"
#       },
#       "Effect": "Allow",
#       "Sid": ""
#     }
#   ]
# }
# POLICY
# }

# # Policy for the task role

# resource "aws_iam_policy_attachment" "task_execution_policy_attachment" {
#   name       = "task_execution_policy_attachment"
#   roles      = [aws_iam_role.task_execution.name]
#   policy_arn = aws_iam_role.task_execution.arn

# }

# # Create a ECS Service
# resource "aws_ecs_service" "task-service" {
#   name            = "task-service"
#   cluster         = aws_ecs_cluster.c7-deleton-api-ecs.id
#   task_definition = aws_ecs_task_definition.task-definition.arn
#   desired_count   = 1

# }
