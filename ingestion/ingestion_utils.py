"""Utility file for the kafka stream ingestion file to pull from,
mainly composed of functions to processed/clean messages"""
import re
import math
import json
from datetime import datetime

from confluent_kafka import Message

SYSTEM_SPLIT = " mendoza v9: [SYSTEM] data = "
RIDE_SPLIT = " mendoza v9: [INFO]: Ride - "
TELEMETRY_SPLIT = " mendoza v9: [INFO]: Telemetry - "
KEY_VALUE_MATCHING = r"(\w+)\s*=\s*([\w.]+)"

def decode_message(consumed_message: Message) -> dict:
    """decodes the Message objects received by polling the kafka stream using
    confluent kafka, returning a dictionary"""
    return json.loads(consumed_message.value().decode('utf-8'))['log'].replace("\n","")


def epoch_to_timestamp(epoch: int) -> datetime:
    """Converts the time based on the epoch to a human readable date"""
    return datetime.fromtimestamp(epoch/1000).strftime("%Y-%m-%d")


def process_rider_address(unformatted_address: str) -> dict:
    """Formats the address string into its components. Some liberties were taken here
    by assuming the data came in one of two formats which seems consistent. Either
    {house number} {street name}, {city/town}, {postcode} or 
    {house number/flat + number}, {street name}, {city/town}, {postcode}"""
    split_address = unformatted_address.split(",")
    if len(split_address) == 4:
        formatted_address = {
            "house_no": split_address[0],
            "street_name": split_address[1],
            "city": split_address[2],
            "postcode": split_address[3]
        }
    elif len(split_address) == 3:
        pattern = r"(\d+)\s*(.*)"
        split_house_no = re.match(pattern, split_address[0])
        formatted_address = {
            "house_no": split_house_no.group(1),
            "street_name": split_house_no.group(2),
            "city": split_address[1],
            "postcode": split_address[2]
        }
    else:
        print("Invalid address format")
        return {}
    return formatted_address


def process_rider_name(fullname: str):
    """Splits the riders full name into first and last name.
    The data can contain titles such as Mr. or Miss. which are filtered out here"""
    split_name = fullname.split()
    if len(split_name) == 2:
        return {"first_name": split_name[0], 'last_name': split_name[1]}
    if len(split_name) == 3:
        return {"first_name": split_name[1], 'last_name': split_name[2]}


def get_rider_age(rider_dob: str, ride_start_time: str) -> int:
    """Finds the age of the rider at the start of their ride"""
    start_date = datetime.strptime(ride_start_time, "%Y-%m-%d %H:%M:%S.%f").date()
    dob_date = datetime.fromtimestamp(rider_dob/1000).date()
    return math.floor((start_date - dob_date).days/365.25)

def process_rider_info(decoded_system_message: dict) -> dict:
    """Processes the message received from the kafka stream if the message
    contains [SYSTEM] in it, indicating it is rider data"""
    personal_info = json.loads(decoded_system_message.split(SYSTEM_SPLIT, 1)[1])
    start_time = decoded_system_message.split(SYSTEM_SPLIT, 1)[0]


    address = process_rider_address(personal_info['address'])
    split_name = process_rider_name(personal_info['name'])

    rider_info = {
        'rider_id': personal_info['user_id'],
        'first_name': split_name['first_name'],
        'last_name': split_name['last_name'],
        'gender': personal_info['gender'],
        'date_of_birth': epoch_to_timestamp(personal_info['date_of_birth']),
        'email': personal_info['email_address'],
        'height_cm': personal_info['height_cm'],
        'weight_kg': personal_info['weight_kg'],
        'account_creation_date': epoch_to_timestamp(personal_info['account_create_date'])
    }

    ride_info = {
        'bike_serial': personal_info['bike_serial'],
        'rider_id': personal_info['user_id'],
        'start_time': start_time
    }

    rider_age = get_rider_age(personal_info['date_of_birth'], start_time)

    return {"rider_info": rider_info, "address_info": address,
            "ride_info": ride_info, "rider_age": rider_age}


def create_dict_from_string(message: str) -> dict:
    """Takes the message strings and converts them into dictionaries for ease of use"""
    data_dict = {}
    for match in re.findall(KEY_VALUE_MATCHING, message):
        key = match[0]
        if match[1].isdigit():
            value = int(match[1])
        else:
            value = round(float(match[1]), 2)
        data_dict[key] = value
    return data_dict


def process_ride_message(decoded_ride_message: dict):
    """Processes the message received from the kafka stream is the message is a
    RIDE message, returning the duration, resistance and recording time"""
    relevant_info = decoded_ride_message.split(RIDE_SPLIT, 1)
    recording_time = relevant_info[0]
    ride_data_string = relevant_info[1]

    ride_data = create_dict_from_string(ride_data_string)

    ride_data['recording_time'] = recording_time
    return ride_data


def process_telemetry_message(decoded_ride_message: dict):
    """Processes the message received from the kafka stream is the message is a
    TELEMETRY message, returning the heart_rate, rpm and power"""
    relevant_info = decoded_ride_message.split(TELEMETRY_SPLIT, 1)
    recording_time = relevant_info[0]
    telemetry_data_string = relevant_info[1]

    telemetry_data = create_dict_from_string(telemetry_data_string)
    telemetry_data['recording_time'] = recording_time
    return telemetry_data
