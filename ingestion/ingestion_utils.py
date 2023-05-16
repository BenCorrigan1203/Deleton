import re
import json
from datetime import datetime

from confluent_kafka import Message

SYSTEM_SPLIT = " mendoza v9: [SYSTEM] data = "

def decode_message(consumed_message: Message) -> dict:
    return json.loads(consumed_message.value().decode('utf-8'))['log'].replace("\n","")


def epoch_to_timestamp(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch/1000).strftime("%Y-%m-%d")


def process_rider_address(unformatted_address: str) -> dict:
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
    split_name = fullname.split()
    if len(split_name) == 2:
        return {"first_name": split_name[0], 'last_name': split_name[1]}
    if len(split_name) == 3:
        return {"first_name": split_name[1], 'last_name': split_name[2]}


def process_rider_info(decoded_system_message: dict) -> list:
    personal_info = json.loads(decoded_system_message.split(SYSTEM_SPLIT, 1)[1])

    address = process_rider_address(personal_info['address'])
    split_name = process_rider_name(personal_info['name'])

    rider_info = {
        'user_id': personal_info['user_id'],
        'first_name': split_name['first_name'],
        'last_name': split_name['last_name'],
        'date_of_birth': epoch_to_timestamp(personal_info['date_of_birth']),
        'email': personal_info['email_address'],
        'height_cm': personal_info['height_cm'],
        'weight_kg': personal_info['weight_kg'],
        'account_creation_date': epoch_to_timestamp(personal_info['account_create_date'])
    }

    return {"rider_info": rider_info, "address_info": address}