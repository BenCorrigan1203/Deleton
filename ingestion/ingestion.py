import os
import json

from confluent_kafka import Consumer
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import boto3

from ingestion_utils import decode_message, process_rider_info, process_ride_message, process_telemetry_message
from ingestion_sql import ADDRESS_SQL, RIDER_SQL, RIDE_SQL, METADATA_SQL, END_RIDE_SQL

def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(user = os.environ["DB_USER"],
            host = os.environ["DB_HOST"],
            database = os.environ["DB_NAME"],
            password = os.environ['DB_PASSWORD'],
            port = os.environ['DB_PORT'],
            options=f"-c search_path={os.environ['SCHEMA']}"
        )
        return conn
    except Exception as err:
        print(err)
        print("Error connecting to database.")

def add_address_to_database(rider_address: dict) -> int:
    """Adds the address of the rider to the database if it doesn't already
    exist, returning the address_id of the inputted entry"""
    with conn.cursor() as cur:
        cur.execute(ADDRESS_SQL, [rider_address['house_no'],
                                  rider_address['street_name'],
                                  rider_address['city'],
                                  rider_address['postcode'],
                                  rider_address['house_no'],
                                  rider_address['street_name'],
                                  rider_address['city'],
                                  rider_address['postcode']])
        address_id = cur.fetchall()[0][0]
        conn.commit()
    return address_id



def add_rider_data_to_database(rider_data: dict, address_id: int) -> None:
    """Adds the data on the rider to the database if it doesn't already exist"""
    with conn.cursor() as cur:
        cur.execute(RIDER_SQL, [rider_data['rider_id'],
                                rider_data['first_name'],
                                rider_data['last_name'],
                                rider_data['gender'],
                                address_id,
                                rider_data['date_of_birth'],
                                rider_data['email'],
                                rider_data['height_cm'],
                                rider_data['weight_kg'],
                                rider_data['account_creation_date']])
        conn.commit()


def add_ride_data_to_database(ride_data: dict) -> int:
    """Adds the data on the specific ride to the database, not adding the end time,
    which will be done in a different time and place, returns the ride_id"""
    with conn.cursor() as cur:
        cur.execute(RIDE_SQL, [ride_data['bike_serial'],
                               ride_data['rider_id'],
                               ride_data['start_time']])
        ride_id = cur.fetchall()[0][0]
        conn.commit()
    return ride_id


def add_metadata_to_database(metadata: list[list]) -> None:
    """Adds the ride metadata to the database. Given there are so many requests this is chunked
    into 10 entries at a time"""
    with conn.cursor() as cur:
        execute_values(cur, METADATA_SQL, metadata)
        conn.commit()


def add_ride_end_time_to_db(end_time: str, ride_id: int) -> None:
    """After the ride is over (which we can only really see occurs when a new ride starts)
    We update the database ride row with the end time"""
    with conn.cursor() as cur:
        cur.execute(END_RIDE_SQL, [end_time, ride_id])
        conn.commit()


def consume_messages(consumer: Consumer, topic: str) -> None:
    """ A function that constantly polls the topic with a timeout of 1s,
    gathering the data from the kafka stream as a dictionary before using other functions
    to sort and clean the data before sending it to our database.
    """
    consumer.subscribe([topic])
    running = True

    ride_id = -1
    rider_max_heart_rate = -1
    alert_sent = False
    last_log = ""
    last_log_info = {}

    logs_to_input = []
    print("Starting Consumer.")
    try:
        while running:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                raise Exception(message.error())
            
            message_dict = decode_message(message)

            if '[SYSTEM]' in message_dict:
                try:
                    rider_data = process_rider_info(message_dict)
                    rider_max_heart_rate = 220 - rider_data['rider_age']
                    alert_sent = False

                    address_id = add_address_to_database(rider_data['address_info'])
                    add_rider_data_to_database(rider_data['rider_info'], address_id)
                    ride_id = add_ride_data_to_database(rider_data['ride_info'])
                except:
                    print("Error adding Ride to db, skipping to next ride.")

            elif '[INFO]' in message_dict and "Ride" in message_dict:
                if ride_id == -1:
                    continue

                ride_info = process_ride_message(message_dict)
                last_log = 'ride'
                last_log_info = ride_info

            elif '[INFO]' in message_dict and 'Telemetry' in message_dict:
                if ride_id == -1:
                    continue

                telemetry_info = process_telemetry_message(message_dict)

                if telemetry_info['hrt'] > rider_max_heart_rate - 10 and alert_sent == False:
                    message = {"Subject": {"Data": "Heart Rate Alert"},
                                "Body": {"Text": {"Data": f"This is an automated alert from your Deleton tracker. At your current \
age, the maximum safe heart rate is {rider_max_heart_rate} bpm. You have reached \
{telemetry_info['hrt']}. Please exercise with caution and remain safe."}}}
                    ses.send_email(Source="trainee.mohammed.simjee@sigmalabs.co.uk", Destination=email_recipients, Message=message)
                    alert_sent = True

                if last_log == 'ride':
                    logs_to_input.append([
                        telemetry_info['hrt'],
                        telemetry_info['rpm'],
                        telemetry_info['power'],
                        last_log_info['duration'],
                        last_log_info['resistance'],
                        last_log_info['recording_time'],
                        ride_id
                    ])
            elif "beginning of main" in message_dict and ride_id != -1:
                try:
                    add_ride_end_time_to_db(last_log_info['recording_time'], ride_id)
                except:
                    print("Could not add end_time to the ride database.")
            else:
                continue

            if len(logs_to_input) > 9:
                try:
                    add_metadata_to_database(logs_to_input)
                    logs_to_input = []
                except:
                    print("Error adding metadata to db, Data will be stored until next input attempt.")

    except Exception as err:
        print(err)
        print("Error in Consumer, rebooting...")
        return consume_messages(consumer, os.environ['TOPIC'])
    finally: 
        consumer.close()
        print("Consumer Closing")



if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()

    kafka_config = {
        'bootstrap.servers':os.environ['BOOTSTRAP_SERVERS'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username':os.environ['SASL_USERNAME'],
        'sasl.password':os.environ['SASL_PASSWORD'],
        'group.id':os.environ['CONSUMER_GROUP'],
        'auto.offset.reset': 'latest'
    }

    session = boto3.Session(aws_access_key_id=os.environ["ACCESS_KEY"], aws_secret_access_key=os.environ["SECRET_KEY"])
    ses = session.client("ses")
    email_recipients = {"ToAddresses": ["trainee.ben.corrigan@sigmalabs.co.uk"], "CcAddresses": [], "BccAddresses": []}

    consumer = Consumer(kafka_config)

    consume_messages(consumer, os.environ['TOPIC'])