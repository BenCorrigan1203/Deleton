![plot](./report_generation/deloton.png)

# Deloton 🚴‍♀️🚴‍♂️🚴

Repository for SigmaLabsXYZ Deloton project. This Repo allows the construction of a architecture which collects raw Deloton kafka bike data to be processed for streams of outputs for visualisation.

Project contributors:
Abdirrahman Mohamed, Ben Corrigan, Danishan Rahulan, Zaakir Simjee

- [Usage](#usage--outputs-)📊
- [Architecture](#architecture-%EF%B8%8F)🏛️
- [Files](#files-)📁
- [Installation](#installation-%EF%B8%8F)⬇️

🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴

#

## Usage / Outputs 📊

### API

To view and access riders' information using our RESTful API, access the API via the link obtained from the load balancer with the authentication needed for deleting a ride. Below are the endpoints where you can access different information:

- Get Ride information via ride id

  - Use the extension "/ride/{ride_id}/", where "ride_id" is replaced with the ID of the ride you're inquiring about. If valid, you will receive the ride's start time, end time, rider ID, and bike serial.

- Get Riders information via rider id

  - Use the extension "/rider/{rider_id}/", where "rider_id" is replaced with the ID of the rider you're inquiring about. If valid, you will receive the rider's ID, name, gender, address, date of birth, email, height, weight, and account creation date.

- Delete a ride via ride id

  - Use the extension "/ride/{id}/", where "id" is replaced with the ride ID you're trying to delete. NOTE: Authentication is required to delete the ride.

- Get Rides duration via ride id

  - Use the extension "/rider/{rider_id}/duration/", where "rider_id" is replaced with the ID of the ride you're inquiring about. If valid and the ride has ended, you will receive the ride's duration.

- Get daily rides completed today

  - Use the extension "/daily/". This will allow you to see all the rides that are currently occurring or have been completed today.

- Get leaderboard of which rider has completed the most rides

  - Use the extension "/leaderboard/". This will show a leaderboard of all the riders in order of who has completed the most rides.

- Get rides in a specific city

  - Use the extension "/city/{city}/", where "city" is replaced with the name of the city you're inquiring about. If valid, you will receive all the rides that have taken place or are occurring in that city.

##

### Dashboard

##

To view realtime dashboard for riders at a glance using the link provided from the loadbalancer

#### Current ride

<p align="center">
<img src="https://i.ibb.co/ZBrw5RF/Screenshot-2023-05-25-at-13-58-09.png" alt="Tableau example" width="738">
</p>
  - From entering rider id, you will be able to see you details, including current heart rate, cumulative power and, average power and resistance.
  
##
##

#### Recent rides

<p align="center">
<img src="https://i.ibb.co/M1C0n5r/Screenshot-2023-05-25-at-13-59-55.png" alt="Tableau example" width="738">
</p>
  - You will be able to see two graphs which show all the rides in a bar chart, where one is split via age bracket and other is split via gender.

### Tableau

To view the live tableau dashboard, please login to our tableau server

<p align="center">
  <img src="https://i.ibb.co/KNWBRXm/tableau-dashboard.png" alt="Tableau example" width="738">
</p>

- Above image shows leaderboard of riders which can be filtered on longest individual ride, highest power output and longest cumulative ride time by a rider.

##

##

### Daily report

<p align="center">
  <img src="https://i.ibb.co/jVsSR1Y/Screenshot-2023-05-25-at-14-02-22.png" alt="Daily report example" width="738">
</p>

- Above is an example of the daily report sent via email to the C-suite executives each day. The report includes the total number of riders and four graphs. Graph 1 displays the riders of the past day split by gender, Graph 2 shows the riders of the past day split by age brackets, Graph 3 illustrates the average heart rates of riders throughout the day, and the final graph exhibits the average power of riders during the day.

🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴

#

## Architecture 🏛️

### Diagram illustrating the projects architecture

##

##

![plot](./Readme/architecture-diagram.png)

##

##

### Extract

##

1. Kafka

- This section provides the input raw data from the bikes, which needs to be cleaned for the rest of the pipeline.

2. Ingestion script

- This section contains the Python script that connects to Kafka for live data. The data is then extracted and cleaned. The script runs continuously on an ECS to upload the clean data to our RDS.

### Load

##

3. RDS, database

- This section of the pipeline is where we load the data that has been cleaned and verified. The initial data from the ingestion script is loaded into our daily schema in the database. Additionally, there is a historical schema for data older than 12 hours.

### Transform

##

4. Step-function

##

4.1. Compress data script

- This section retrieves the data from the daily schema of the RDS. Using a Lambda script, we compress the data and then push it to the historical schema.

##

4.2. Report generation script

- This section takes the data from the historical schema and generates a PDF of key graphs for the C-suit executives.

### Output

##

1. Alerts

- This section is connected to the ingestion script where, using AWS services, we can send email notifications for any heart readings beyond the normal boundaries.

2. API

- This section retrieves data from both the daily and historical schema to present key information about riders and their rides. Users will be able to access this information through the API, which is hosted on a load balancer using AWS services.

3. Daily report

- This section takes the PDF from the report generation script and produces an email with the PDF attached.

4. Tableau

- This section provides some analyses for Data Analysts, key information on historical rides which have taken place.

![Biking](https://media.tenor.com/bTDIPxWB1kMAAAAi/moving-man.gif)![Biking](https://media.tenor.com/bTDIPxWB1kMAAAAi/moving-man.gif)![Biking](https://media.tenor.com/bTDIPxWB1kMAAAAi/moving-man.gif)ZOOM

#

## Files 📁

### Ingestion

#### This folder contains files related to the ingestion for our pipeline, which gathers data from the kafka.

##

- `ingestion.py` : This file enables us to consume and sort the Kafka data, which is then sent to the database for short-term storage.

- `ingestion_utils.py` : This file can be considered a helper function for ingestion.py as it assists in splitting the raw data.

- `ingestion_sql.py` : This file contains type definitions along with SQL commands to reduce code cluttering.

- `Dockerfile` : This file allows us to containerize this folder to be than run on any machine with only its dependencies.

- `test_ingestion.py` : This file contains pytest scripts to tests aspects of the ingestion.py, to make sure it is functioning.

- `requirements.txt` : This file contains a list of the required Python packages to run the scripts in this folder.

### Terraform

#### This folder contains the files related to the creation of all of our AWS services, including RDS. Lambda functions and ECRs.

##

- `ecr.tf` : This file contains the the terraform resource creation for the ECR for each part of the architecture.

- `ecs.tf` : This file contains the ECS dependable resources such as the clusters, task definitions and event bridge.

- `main.tf` : This file includes the resource creation for the Lambdas and Step Function, which will host our Python scripts on the cloud. It also encompasses the IAM policy required for these resources.

- `rds.tf` : This file contains the resource creation for the RDS database using the referenced security groups and VPC subnets.

- `setup.tf` : This file contain resource parameters other services would use like the VPC, VPC subnets and security groups.

- `variables.tf` : This file contains variables which are referenced throughout each terraform file, such as database name and port.

- `create_db.sql` : This file contains the sql script to create the database and the tables in each schema.

### Compress_data

#### This folder contains the files required to transfer the data from the AWS RDS daily schema to the historical schema

##

- `compress_data.py` : This file extracts all rider information from the past 24 hours from the daily schema, formats the data, and uploads it to the historical schema. Furthermore, it deletes data in the daily and historical schemas that is older than 12 hours.

- `compress_sql.py` : This file contains all the SQL commands for the compress_data.py, to allow easier code consumption.

- `Dockerfile` : This file allows us to containerize this folder to be than run on any machine with only its dependencies.

- `requirements.txt` : This file contains a list of the required Python packages to run the scripts in this folder.

### Report_generation

#### This folder contains the files which create the documentation for the C-suite, attached to an email.

##

- `report.py` : This file utilizes the daily schema to extract various graphs and information from the last 24 hours. It compiles this data into a PDF format, which is subsequently sent in an email.

- `report_utils.py` : This file contains "helper" functions for the report.py to help make the report.py easier to consume.

- `Dockerfile` : This file allows us to containerize this folder to be than run on any machine with only its dependencies.

- `deloton.png` : This is a image of the Deloton logo used in the PDF.

- `requirements.txt` : This file contains a list of the required Python packages to run the scripts in this folder.

### Live_dashboard

#### This folder contains the files which create the dashboard using flask, for the riders.

##

- `dash_utils.py` : This file contains the python scripts to contact the database and form the figures needed in the dashboard.

- `sql_vars.py` : This file contains the SQL commands used in the dash_utils.py to allow that file to be easier to consume.

- `app.py `: this file contains the dash template used by each page, which holds the navigation bar and references to the pages.

- pages

  - `current_ride.py `: This file contains the plotly graphs of the current heart rate, resistance and power graphs.

  - `recent_rides.py` : This file contains the plotly graphs of the recent rides and shows the gender split and age groups.

- `Dockerfile` : This file allows us to containerize this folder to be than run on any machine with only its dependencies.

- `requirements.txt` : This file contains a list of the required Python packages to run the scripts in this folder.

### API

#### This folder contains the files which create the restful API to access rider information.

##

- `app.py` : This file contains all the functions for each end point accessible through the api.

- `helper_function.py` : This file has functions used by the `app.py` for set-up and to allow the `app.py` to be more consumable.

- `Dockerfile` : This file allows us to containerize this folder to be than run on any machine with only its dependencies.

- `requirements.txt` : This file contains a list of the required Python packages to run the scripts in this folder.

🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴

#

## Installation ⬇️

To run this repo you will need to do the steps below.

NOTE: Before proceeding with the installation process, please ensure that you have Terraform installed on your system. Additionally, make sure to add the necessary environment variables in the /terraform/variables.tf file and adjust the deloton.sh script with the appropriate Docker terminal lines for your AWS account name. You may also need to install any additional dependencies required for Terraform.

- run `deloton.sh` in terminal

- once complete you should receive the terminal line below

##

`Apply complete! Resources: 37 added, 0 changed, 0 destroyed.`

##

🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️🚴🚵‍♀️🚴🏿‍♀️🚴🏽🚵‍♂️🚴🏻🚵🏿‍♀️🚴‍♀️🚴‍♂️

#
