import os
import math
from datetime import datetime, date

import pandas as pd
import psycopg2
from sqlalchemy import URL, create_engine
from dotenv import load_dotenv

import pandas as pd

from sql_vars import CURRENT_RIDER_SQL

def get_db_connection():
    """Connects to the database"""
    try:
        url_object = URL.create(
        "postgresql+psycopg2",
        username=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        port=os.environ['DB_PORT']
    )
        return create_engine(url_object, connect_args={'options': f"-csearch_path={os.environ['SCHEMA']}"})
    except Exception as err:
        print(err)
        print("Error connecting to database.")

load_dotenv()

conn = get_db_connection()

ride_df = pd.read_sql_table("ride", conn)

rider_df = pd.read_sql_table("rider", conn)

past_12_hours = datetime.fromtimestamp(datetime.now().timestamp() - (12 * 3600)).hour

recent_rides = ride_df[ride_df["start_time"].dt.hour > past_12_hours].dropna()

recent_rides["gender"] = recent_rides["rider_id"].apply(lambda x: rider_df["gender"].where(rider_df["rider_id"] == x).dropna().values[0])

print(recent_rides["gender"])

recent_rides["total_duration"] = recent_rides["start_time"].apply()

print(recent_rides[["start_time", "end_time"]])





def execute_sql_query(sql_query: str, engine):
    with engine.connect() as conn:
        return pd.read_sql(sql_query, conn)


def get_rider_age(rider_dob: str) -> int:
    """Finds the age of the rider at the start of their ride"""
    return math.floor((date.today() - rider_dob).days/365.25)


def get_current_rider_name(engine):
    df = execute_sql_query(CURRENT_RIDER_SQL, engine)
    first_name = df.iloc[0]['first_name']
    last_name = df.iloc[0]['last_name']
    if df.iloc[0]['gender'] == 'male':
        gender = f"\u2642 Male"
    else:
        gender = f"\u2640 Female"
    age = get_rider_age(df.iloc[0]['date_of_birth'])

    return {"name": f"{first_name} {last_name}", "gender": gender, "age": age}
