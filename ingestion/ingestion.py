import os
import json

from confluent_kafka import Consumer
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection
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


def add_address_to_database(conn: connection, rider_address: dict) -> int:
    """Adds the address of the rider to the database if it doesn't already
    exist, returning the address_id of the inputted entry"""
    print(rider_address)
    try:
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
    except Exception as err:
        print(err)
        print(err, "Could not add rider address to the database.")
    finally:
        conn.commit()
    return address_id


def add_rider_data_to_database(conn: connection, rider_data: dict, address_id: int) -> None:
    """Adds the data on the rider to the database if it doesn't already exist"""
    try:
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
    except Exception as err:
        print(err, "Could not add new rider to the database.")
    finally:
        conn.commit()


def add_ride_data_to_database(conn: connection, ride_data: dict) -> int:
    """Adds the data on the specific ride to the database, not adding the end time,
    which will be done in a different time and place, returns the ride_id"""
    try:
        with conn.cursor() as cur:
            cur.execute(RIDE_SQL, [ride_data['bike_serial'],
                                ride_data['rider_id'],
                                ride_data['start_time']])
            ride_id = cur.fetchall()[0][0]
    except Exception as err:
        print(err, "Could not add new ride to the database.")
    finally:
        conn.commit()
    return ride_id



def add_metadata_to_database(conn: connection, metadata: list[list]) -> None:
    """Adds the ride metadata to the database. Given there are so many requests this is chunked
    into 10 entries at a time"""
    try:
        with conn.cursor() as cur:
            cur.execute(METADATA_SQL, metadata)
    except Exception as err:
        print(err, "Could not add metadata to the database.")
    finally:
        conn.commit()

def add_ride_end_time_to_db(conn: connection, end_time: str, ride_id: int) -> None:
    """After the ride is over (which we can only really see occurs when a new ride starts)
    We update the database ride row with the end time"""
    try:
        with conn.cursor() as cur:
            cur.execute(END_RIDE_SQL, [end_time, ride_id])
    except Exception as err:
        print(err, "Could not add end_time to the ride database.")
    finally:
        conn.commit()


def assess_heart_rate(current_heart_rate: int, max_heart_rate: int, alert_sent_status: bool) -> bool:
    """Assesses the current heart_rate of te rider and sends an alert to them via email if their
    heart rate is too high"""
    if current_heart_rate > max_heart_rate - 10 and alert_sent_status == False:
        message = {"Subject": {"Data": "Heart Rate Alert"},
                    "Body": {"Text": {"Data": f"This is an automated alert from your Deleton tracker. At your current \
age, the maximum safe heart rate is {max_heart_rate} bpm. You have reached \
{current_heart_rate}. Please exercise with caution and remain safe."}}}
        ses.send_email(Source="trainee.mohammed.simjee@sigmalabs.co.uk", Destination=email_recipients, Message=message)
        return True
            

def process_message(conn: connection, message: str, ride_id: int, last_log: str, last_log_info: dict,
                    max_heart_rate: int, current_ride_alert_status: bool) -> dict:
    """Processes the messages differently depending on the key words found in the message
    string, returning a consistent dictionary of information that is to be passed into the next
    message processing"""
    if '[SYSTEM]' in message:
        print("new rider")
        rider_data = process_rider_info(message)
        rider_max_heart_rate = 220 - rider_data['rider_age']

        address_id = add_address_to_database(conn, rider_data['address_info'])
        add_rider_data_to_database(conn, rider_data['rider_info'], address_id)
        ride_id = add_ride_data_to_database(conn, rider_data['ride_info'])
        return {"current_ride_id": ride_id, "last_log": "system", "last_log_info": rider_data,
                "max_heart_rate": rider_max_heart_rate, "alert_status": False}

    elif '[INFO]' in message and "Ride" in message and ride_id != -1:
        ride_info = process_ride_message(message)
        return {"current_ride_id": ride_id, "last_log": "ride", "last_log_info": ride_info,
                "max_heart_rate": max_heart_rate, "alert_status": current_ride_alert_status}
    
    elif '[INFO]' in message and 'Telemetry' in message and ride_id != -1:
        telemetry_info = process_telemetry_message(message)
        alert_sent = assess_heart_rate(telemetry_info['hrt'], max_heart_rate, current_ride_alert_status) 
        try:
            if last_log == 'ride':
                log_to_input = [
                    telemetry_info['hrt'],
                    telemetry_info['rpm'],
                    telemetry_info['power'],
                    last_log_info['duration'],
                    last_log_info['resistance'],
                    last_log_info['recording_time'],
                    ride_id
                ]
        except KeyError as err:
            print("Log missing a key, skipping to next data entry", err)
            return None
        
        add_metadata_to_database(conn, log_to_input)
        return {"current_ride_id": ride_id, "last_log": "telemetry", "last_log_info": telemetry_info,
                "max_heart_rate": max_heart_rate, "alert_status": alert_sent}
    
    elif "beginning of main" in message and ride_id != -1:
        add_ride_end_time_to_db(conn, last_log_info['recording_time'], ride_id)
        return {"current_ride_id": -1, "last_log": "ending", "last_log_info": None,
                "max_heart_rate": max_heart_rate, "alert_status": current_ride_alert_status}
    return None



def consume_messages(conn: connection, consumer: Consumer, topic: str) -> None:
    """ A function that constantly polls the topic with a timeout of 1s,
    gathering the data from the kafka stream as a dictionary before using other functions
    to sort and clean the data before sending it to our database. Data on the previous message
    sent is stored due to the format of the messages from the kafka stream
    """
    consumer.subscribe([topic])
    ride_id = -1
    alert_sent_status = False
    last_log = ""
    last_log_info = {}
    max_heart_rate = -1
    print("Starting Consumer...")
    try:
        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                raise Exception(message.error())
            decoded_message = decode_message(message)
            processed_data = process_message(conn, decoded_message, ride_id, last_log, last_log_info,
                                             max_heart_rate, alert_sent_status)

            if processed_data:
                ride_id = processed_data['current_ride_id']
                alert_sent_status = processed_data['alert_status']
                last_log = processed_data['last_log']
                last_log_info = processed_data['last_log_info']
                max_heart_rate = processed_data['max_heart_rate']
    except Exception as err:
        print(err)
        print("Error in Consumer, rebooting...")
        return consume_messages(conn, consumer, os.environ['TOPIC'])
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
    ses = session.client("ses", region_name='eu-west-2')
    email_recipients = {"ToAddresses": ["trainee.ben.corrigan@sigmalabs.co.uk"], "CcAddresses": [], "BccAddresses": []}

    consumer = Consumer(kafka_config)

    consume_messages(conn, consumer, os.environ['TOPIC'])