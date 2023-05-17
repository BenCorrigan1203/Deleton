import os
import math
from datetime import datetime, date

import pandas as pd
import psycopg2
from sqlalchemy import URL, create_engine
from dotenv import load_dotenv
import plotly.express as px

import pandas as pd

from sql_vars import CURRENT_RIDER_SQL, RECENT_RIDES_SQL

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


load_dotenv()

conn = get_db_connection()

recent_rides = execute_sql_query(RECENT_RIDES_SQL, conn)

gender_grouped_rides = recent_rides.groupby(recent_rides["gender"]).count()

fig = px.bar(x=gender_grouped_rides.index, y=gender_grouped_rides["ride_id"])

fig.show()

