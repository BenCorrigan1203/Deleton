import os
import json

from confluent_kafka import Consumer
from dotenv import load_dotenv
import psycopg2

from ingestion_utils import decode_message, process_rider_info, process_ride_message, process_telemetry_message

def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(user = os.environ["DB_USER"],
            host = os.environ["DB_HOST"],
            database = os.environ["DB_NAME"],
            password = os.environ['DB_PASSWORD'],
            port = os.environ['DB_PORT']
        )
        return conn
    except Exception as err:
        print(err)
        print("Error connecting to database.")

def add_rider_data_to_database(rider_data: dict) -> None:
    w



def consume_messages(consumer: Consumer, topic: str) -> None:
    """ A function that constantly polls the topic with a timeout of 1s,
    gathering the data from the kafka stream as a dictionary before using other functions
    to sort and clean the data before sending it to our database.
    """
    consumer.subscribe([topic])
    running = True

    try:
        while running:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                raise Exception(message.error())
            
            message_dict = decode_message(message)
            # print(message_dict)

            if '[SYSTEM]' in message_dict:
                rider_data = process_rider_info(message_dict)
                print(rider_data)
            elif '[INFO]' in message_dict and "Ride" in message_dict:
                print(process_ride_message(message_dict))
            elif '[INFO]' in message_dict and 'Telemetry' in message_dict:
                print(process_telemetry_message(message_dict))
            else:
                continue

    except Exception as err:
        print(err)
    finally: 
        consumer.close()


if __name__ == "__main__":
    load_dotenv()

    kafka_config = {
        'bootstrap.servers':os.environ['BOOTSTRAP_SERVERS'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username':os.environ['SASL_USERNAME'],
        'sasl.password':os.environ['SASL_PASSWORD'],
        'group.id':os.environ['CONSUMER_GROUP'],
        'auto.offset.reset': 'latest'
    }

    consumer = Consumer(kafka_config)

    consume_messages(consumer,os.environ['TOPIC'])