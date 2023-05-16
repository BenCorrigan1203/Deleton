provider "aws" {
    shared_credentials_files = ["~/.aws/credentials"]
    region = "${var.region}"
}

# Sets up multiple AWS ECR repositories w/ option to delete even if there is an image in them.

resource "aws_ecr_repository" "deleton-ingestion-ecr" {
  name = "deleton-ingestion-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
  force_delete = true
}

resource "aws_ecr_repository" "deleton-compression-ecr" {
  name = "deleton-compression-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
  force_delete = true
}

resource "aws_ecr_repository" "deleton-report-ecr" {
  name = "deleton-report-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
  force_delete = true
}

resource "aws_ecr_repository" "deleton-dash-ecr" {
  name = "deleton-dash-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
  force_delete = true
}

resource "aws_ecr_repository" "deleton-api-ecr" {
  name = "deleton-api-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }
  force_delete = true
}

