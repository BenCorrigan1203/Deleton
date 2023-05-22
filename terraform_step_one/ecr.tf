# Create ECR for live dashbaord
resource "aws_ecr_repository" "live-dash" {
  name                 = "c7-deleton-live-dashboard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create ECR for compression script
resource "aws_ecr_repository" "compress" {
  name                 = "c7-deleton-compression-script"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
# Create ECR for ingestion script
resource "aws_ecr_repository" "ingestion" {
  name                 = "c7-deleton-ingestion-script"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}


# Create ECR for report generation script
resource "aws_ecr_repository" "report" {
  name                 = "c7-deleton-report-generation"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create ECR for API
resource "aws_ecr_repository" "API" {
  name                 = "c7-deleton-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
