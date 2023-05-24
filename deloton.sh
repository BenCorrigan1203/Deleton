# This script will create the neccassary AWS resources and deploy the relevant docker images.
cd terraform

# Destroy all running resources 
terraform destroy -auto-approve
# Initialise Terraform
terraform init 

# Create the ECR repositories.  
terraform plan -target=aws_ecr_repository.live-dash -target=aws_ecr_repository.compress -target=aws_ecr_repository.report -target=aws_ecr_repository.API -target=aws_ecr_repository.ingestion
terraform apply -target=aws_ecr_repository.live-dash -target=aws_ecr_repository.compress -target=aws_ecr_repository.report -target=aws_ecr_repository.API -target=aws_ecr_repository.ingestion -auto-approve

# Create the RDS
terraform plan -target=aws_db_instance.deloton-rds
terraform apply -target=aws_db_instance.deloton-rds -auto-approve

# Login into AWS
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 605126261673.dkr.ecr.eu-west-2.amazonaws.com

cd ../api
# Dockerize the API
# Create docker image for the API
docker build -t c7-deloton-api .
# Tag docker image 
docker tag c7-deloton-api:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-api:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-api:latest

cd ../compress_data
# Dockerize the compression script
# Create docker image for the compression script
docker build -t c7-deloton-compression-script .
# Tag docker image 
docker tag c7-deloton-compression-script:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-compression-script:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-compression-script:latest

cd ../ingestion
# Dockerize the ingestion script
# Create docker image for the ingestion script
docker build -t c7-deloton-ingestion-script .
# Tag docker image ingestion script
docker tag c7-deloton-ingestion-script:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-ingestion-script:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-ingestion-script:latest

cd ../live_dashboard
# Dockerize the live dashbaord
# Create docker image for the live dashbaord
docker build -t c7-deloton-live-dashboard .
# Tag docker image 
docker tag c7-deloton-live-dashboard:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-live-dashboard:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-live-dashboard:latest

cd ../report_generation
# Dockerize the genearation script
# Create docker image for the genearation script
docker build -t c7-deloton-report-generation .
# Tag docker image 
docker tag c7-deloton-report-generation:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-report-generation:latest
# Deploy docker image to the ECR
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/c7-deloton-report-generation:latest

cd ../terraform
# Create Lambda and Step functions, ECS cluster, Task Definition and Services with Load Balancers. 
terraform plan
terraform apply -auto-approve