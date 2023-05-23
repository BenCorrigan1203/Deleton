# This script will create the neccassary AWS resources and deploy the relevant docker images.
cd terraform

# Initialise Terraform
terraform init 

# Create the ECR repositories.  
terraform plan -target=aws_ecr_repository.live-dash -target=aws_ecr_repository.compress -target=aws_ecr_repository.compress -target=aws_ecr_repository.API
terraform apply -target=aws_ecr_repository.live-dash -target=aws_ecr_repository.compress -target=aws_ecr_repository.compress -target=aws_ecr_repository.API

# Create the RDS
terraform plan -target=aws_db_instance.deleton-rds
terraform apply -target=aws_db_instance.deleton-rds

# Login into AWS
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 605126261673.dkr.ecr.eu-west-2.amazonaws.com

cd ../api
# Dockerize the API
# Create docker image for the API
docker build -t c7-deleton-api .
# Tag docker image 
docker tag c7-deleton-api:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-api:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-api:latest

cd ../compress_data
# Dockerize the compression script
# Create docker image for the compression script
docker build -t c7-deleton-compression-script .
# Tag docker image 
docker tag c7-deleton-compression-script:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-compression-script:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-compression-script:latest

cd ../ingestion
# Dockerize the ingestion script
# Create docker image for the ingestion script
docker build -t c7-deleton-ingestion-script .
# Tag docker image ingestion script
docker tag c7-deleton-ingestion-script:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-ingestion-script:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-ingestion-script:latest

cd ../live_dashboard
# Dockerize the live dashbaord
# Create docker image for the live dashbaord
docker build -t c7-deleton-live-dashboard .
# Tag docker image 
docker tag c7-deleton-live-dashboard:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-live-dashboard:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-live-dashboard:latest

cd ../report_generation
# Dockerize the genearation script
# Create docker image for the genearation script
docker build -t c7-deleton-report-generation .
# Tag docker image 
docker tag c7-deleton-report-generation:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-report-generation:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deleton-report-generation:latest

cd ../terraform
# Create Lambda and Step functions, ECS cluster, Task Definition and Services with Load Balancers. 
terraform plan
terraform apply