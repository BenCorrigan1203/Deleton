![plot](./report_generation/deleton.png)

# Deleton 🚴‍♀️🚴‍♂️🚴

Repository for SigmaLabsXYZ Deleton project. This Repo allows the construction of a architecture which collects raw Deleton kafka bike data to be processed for streams of outputs.

- [Files](#)📁
- [Installation](#)⬇️
- [Architecture](#)🏛️
- [Usage](#)📊

## Files

### Ingestion

### This folder contains files related to the ingestion for our pipeline, which gathers data from the kafka.

- ingestion.py : This file allows us to consume and sort the kafka data, which is then sent to the database for short term storage
- ingestion_utils.py : This file can be considered as a helper function for the ingestion.py in order to split the raw data
- ingestion_sql.py : This file holds type definitions with the SQL commands, to reduce the cluttering of the code.
- requirements.txt : This file contains a list of the required Python packages to run the scripts in this folder.

### Terraform

### This folder contains the files related to the creation of all of our AWS services, including RDS. Lambda functions and ECRs.

- ecr.tf : This file contains the the terraform resource creation for the ECR for each part of the architecture.
- ecs.tf : This file contains the ECS dependable resources such as the clusters, task definitions and event bridge.
- lambda.tf : This file contains the resource creation for the lambdas, which will host our python scripts on the cloud. This includes the IAM policy
- rds.tf : This file contains the resource creation for the RDS database using the referenced security groups and VPC subnets.
- setup.tf : This file contain resource parameters other services would use like the VPC, VPC subnets and security groups.
- variables.tf : This file contains variables which are referenced throughout each terraform file, such as database name and port.

### Compress_data

### This folder contains the files required to transfer the data from the AWS RDS daily schema to the historical schema

- compress_data.py : This file extracts all rider information exceeding the past 24 hours from the daily schema, formats it, and uploads the data to the historical schema. Additionally, it deletes data in the daily historical schema that is older than 12 hours.
- compress_sql.py : This file contains all the SQL commands for the compress_data.py, to allow easier code consumption.
- requirements.txt : This file contains a list of the required Python packages to run the scripts in this folder.

### Report_generation

### This folder contains the files which create the documentation for the C-suite, attached to an email.

- report.py : This file uses the daily schema and extracts several graphs and information from the last 24 hours to form a PDF, which is then sent in an email.
- report_utils.py : This file contains "helper" functions for the report.py to help make the report.py easier to consume.
- deleton.png : This is a image of the Deleton logo used in the PDF.
- requirements.txt : This file contains a list of the required Python packages to run the scripts in this folder.

### Live_dashboard

### This folder contains the files which create the dashboard using flask, for the riders.

- dash_utils.py : This file contains the python scripts to contact the database and form the figures needed in the dashboard.
- sql_vars.py : This file contains the SQL commands used in the dash_utils.py to allow that file to be easier to consume.
- app.py : this file contains the dash template used by each page, which holds the navigation bar and references to the pages.
- pages
  - current_ride.py : This file contains the plotly graphs of the current heart rate, resistance and power graphs.
  - recent_rides.py : This file contains the plotly graphs of the recent rides and shows the gender split and age groups.

### Database_reset

### This folder contains the files which create the dashboard using flask, for the riders.

- database_reset.py : This file drops all the tables and then creates the tables in both schemas.
- reset.sql : This file has all the SQL commands needed to drop and create

🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️

## Installation

To run this repo you will need to do the steps below.

NOTE. For the installation process you should have terraform installed, alongside any of it's dependencies.

1.  Within the terraform directory, "terraform_step_one", you would need to run the commands below to create the ecr:

    `terraform init`

    `terraform apply`

2.  We now need to dockerize the lambda functions which we have written to be pushed to AWS ecr. Therefore, we need to the Ingestion, compress_data, report_generation, live_dashboard and database_reset folders and run the following commandsThis can be done with the commands below.

    push dockerized images to ecr then
    terraform apply again
