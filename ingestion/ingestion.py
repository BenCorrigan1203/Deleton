
import os
from confluent_kafka import Consumer
import json
from dotenv import load_dotenv

from ingestion_utils import decode_message, process_rider_info

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
                process_rider_info(message_dict)
                print('\n')
            elif '[INFO]' in message_dict and "Ride" in message_dict:
                continue
                print(message_dict.split('[INFO]: ', 1)[1])
            elif '[INFO]' in message_dict and 'Telemetry' in message_dict:
                continue
                print(message_dict.split('[INFO]: ', 1)[1])
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
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(kafka_config)

    consume_messages(consumer,os.environ['TOPIC'])