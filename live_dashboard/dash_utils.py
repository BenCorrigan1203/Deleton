import os
from datetime import datetime

import pandas as pd
import psycopg2
from sqlalchemy import URL, create_engine
from dotenv import load_dotenv


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




