import os
import math
from datetime import datetime, date

import pandas as pd
import psycopg2
from sqlalchemy import URL, create_engine
from dotenv import load_dotenv
import plotly.express as px
import numpy as np
import pandas as pd


from sql_vars import CURRENT_RIDER_SQL, RIDE_DATA_SQL, HEART_RATE_SQL, POWER_SQL, RESISTANCE_SQL, RPM_SQL


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


def heart_rate_analysis(heart_rate: int, age: int) -> str:
    """Analyses the heart rate of a rider and returns how safe
    it is compared to their maximum safe heart rate for their age"""
    mhr = 220 - age
    if heart_rate < 40:
        return "Extremely Low"
    if heart_rate > mhr:
        return "Dangerously High"
    if heart_rate > (mhr - 20):
        return "High"
    else:
        return "Safe"


def get_current_rider_data(engine):
    """Queries the database for all of the most up to date data on the current rider"""
    rider_info = execute_sql_query(CURRENT_RIDER_SQL, engine)
    first_name = rider_info.iloc[0]['first_name']
    last_name = rider_info.iloc[0]['last_name']
    if rider_info.iloc[0]['gender'] == 'male':
        gender = f"\u2642 Male"
    else:
        gender = f"\u2640 Female"
    age = get_rider_age(rider_info.iloc[0]['date_of_birth'])

    ride_data = execute_sql_query(RIDE_DATA_SQL, engine)
    duration = round(ride_data.iloc[0]['duration'])
    heart_rate = round(ride_data.iloc[0]['heart_rate'])
    heart_safety = heart_rate_analysis(heart_rate, age)


    return {"name": f"{first_name} {last_name}", "gender": gender, "age": age,
            "duration": duration, "heart_rate": heart_rate, "heart_safety": heart_safety}


def heart_rate_status_colour(heart_safety: str):
    """Outputs a colour depending on the current heart safety status"""
    if heart_safety == "Extremely Low" or heart_safety == "Dangerously High":
        return "red"
    if heart_safety == "High":
        return "orange"
    return "green"
    

def heart_rate_graph(engine):
    """Create a ploty line graph, plotting heart rate against ride duration"""

    data = execute_sql_query(HEART_RATE_SQL, engine)
    # data = data[data['heart_rate'] != 0] # Not sure if I prefer with this or not
    graph = px.line(data_frame=data, x="duration", y="heart_rate",
                   labels={'duration': 'Ride Duration', 'heart_rate': 'Heart Rate (BPM)'})
    graph.update_layout(
        title = {
         'text': "Heart Rate",
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 25, 'color': 'black'}
        },
    )
    return graph


def resistance_graph(engine):
    """Create a ploty line graph, plotting resistance against ride duration"""
    data = execute_sql_query(RESISTANCE_SQL, engine)
    graph = px.line(data_frame=data, x="duration", y="resistance",
                   labels={'duration': 'Ride Duration', 'resistance': 'Resistance'})
    graph.update_layout(
        title = {
         'text': "Resistance",
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 25, 'color': 'black'}
        },
    )
    return graph


def power_graph(engine):
    """Create a ploty line graph, plotting power against ride duration"""

    data = execute_sql_query(POWER_SQL, engine)
    graph = px.line(data_frame=data, x="duration", y="power",
                   labels={'duration': 'Ride Duration', 'power': 'Power (W)'})
    graph.update_layout(
        title = {
         'text': "Power",
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 25, 'color': 'black'}
        },
    )
    return graph

def rpm_graph(engine):
    """Create a ploty line graph, plotting power against ride duration"""

    data = execute_sql_query(RPM_SQL, engine)
    graph = px.line(data_frame=data, x="duration", y="rpm",
                   labels={'duration': 'Ride Duration', 'rpm': 'RPM'})
    graph.update_layout(
        title = {
         'text': "RPM",
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 25, 'color': 'black'}
        },
    )
    return graph




def group_age_data(recent_rides_df)-> pd.DataFrame:
    bins = [10, 20, 30, 40, 50, 60, 70, 105]
    labels = ['10-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71+']
    age_groups = pd.cut(recent_rides_df['age'], bins=bins, labels=labels, right=True)
    age_group_count = recent_rides_df.groupby([age_groups])['start_time'].count().reset_index(name='count')
    return age_group_count


load_dotenv()

conn = get_db_connection()

recent_rides = execute_sql_query(RECENT_RIDES_SQL, conn)

recent_rides['date_of_birth'] = pd.to_datetime(recent_rides['date_of_birth'])

recent_rides['age'] = ((recent_rides["start_time"] - recent_rides['date_of_birth']).dt.days.astype(float)) * 0.00273973
recent_rides['age'] = recent_rides['age'].apply(lambda x: int(np.floor(x)))

recent_rides[""]

gender_grouped_rides = recent_rides.groupby(recent_rides["gender"]).count()

age_grouped_rides = group_age_data(recent_rides)

fig = px.bar(x=gender_grouped_rides.index, y=gender_grouped_rides["ride_id"])

fig2 = px.bar(age_grouped_rides, x="age", y="count")

# fig3 = px.line(recent_rides, x="end_time", y=["avg_power", "max_power"])

fig.show()

fig2.show()

# fig3.show()
