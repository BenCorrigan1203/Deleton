import boto3
from dotenv import dotenv_values

config = dotenv_values(".env")

session = boto3.Session(aws_access_key_id=config["ACCESS_KEY"], aws_secret_access_key=config["SECRET_KEY"])

ses = session.client("ses")

email_recipients = {"ToAddresses": ["trainee.mohammed.simjee@sigmalabs.co.uk"], "CcAddresses": [], "BccAddresses": []}

message = {"Subject": {"Data": "test"}, "Body": {"Text": {"Data": "hello"}}}

ses.send_email(Source="trainee.mohammed.simjee@sigmalabs.co.uk", Destination=email_recipients, Message=message)