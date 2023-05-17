import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, engine
import pandas as pd
import numpy as np
import boto3
from dotenv import load_dotenv, dotenv_values
import os
from typing import Tuple


DAILY_SCHEMA = "daily"
HISTORICAL_SCHEMA = "historical"
HTML_FILE = "report_graph.html"

def get_db_connection(config: dict) -> engine:
    """Connect to an rds using sqlalchemy engines"""
    db_uri = f'postgresql+psycopg2://{config["DATABASE_USERNAME"]}:{config["DATABASE_PASSWORD"]}@{config["DATABASE_IP"]}:{config["DATABASE_PORT"]}/{config["DATABASE_NAME"]}'
    engine = create_engine(db_uri)
    return engine


def get_rider_past_day(engine: engine) -> str:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine.connect()
    query = """SELECT start_time FROM ride_info WHERE DATEDIFF('hour', start_time, now()) <= 24;"""
    riders_day_df = pd.read_sql_table(query, conn, schema=HISTORICAL_SCHEMA)
    total_riders = riders_day_df["start_time"].count()
    print_line = f"Total number of riders in the last 24 hours: {total_riders}"
    conn.close()
    engine.dispose()
    return print_line

def get_gender_rider_past_day(engine: engine) -> go.Figure:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine.connect()
    query = """SELECT ride_info.start_time, rider.gender FROM ride_info
               JOIN rider on ride_info.rider_id = rider.rider_id 
               WHERE DATEDIFF('hour', start_time, now()) <= 24;"""
    riders_day_gender_df = pd.read_sql_table(query, conn, schema=HISTORICAL_SCHEMA)
    gender_count = riders_day_gender_df.groupby('gender')['start_time'].count().reset_index(name='count')
    gender_fig = px.bar(gender_count, x = 'gender', y = 'count', title="Gender split between riders in the last 24 hours")
    gender_fig.update_layout(
    xaxis_title='Gender',
    yaxis_title='Count'
    )
    conn.close()
    engine.dispose()
    return gender_fig

def get_age_rider_past_day(engine: engine) -> go.Figure:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine.connect()
    query = """SELECT ride_info.start_time, rider.dob FROM ride_info
               JOIN rider on ride_info.rider_id = rider.rider_id 
               WHERE DATEDIFF('hour', start_time, now()) <= 24;"""
    riders_day_age_df = pd.read_sql_table(query, conn, schema=HISTORICAL_SCHEMA)

    riders_day_age_df['start_time'] = pd.to_datetime(riders_day_age_df['start_time'])
    riders_day_age_df['dob'] = pd.to_datetime(riders_day_age_df['dob'])
    riders_day_age_df['age'] = ((riders_day_age_df['start_time'] - riders_day_age_df['dob']).dt.days.astype(float)) * 0.00273973 #converts to normal number
    riders_day_age_df['age'] = riders_day_age_df['age'].apply(np.floor)
    total_riders_age = group_age_data(riders_day_age_df)
    age_fig = px.bar(total_riders_age, x = 'age', y = 'count', title="Age group split between riders in the last 24 hours")
    age_fig.update_layout(
    xaxis_title='Age',
    yaxis_title='Count'
    )
    conn.close()
    engine.dispose()
    return age_fig

def group_age_data(riders_day_gender_df)-> pd.DataFrame:
    bins = [10, 20, 30, 40, 50, 60, 70, 105]
    labels = ['10-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71+']
    age_groups = pd.cut(riders_day_gender_df['age'], bins=bins, labels=labels, right=True)
    age_group_count = riders_day_gender_df.groupby([age_groups])['start_time'].count().reset_index(name='count')
    return age_group_count


def get_avg_reading_riders_past_day(engine: engine) -> Tuple[go.Figure,]:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine.connect()
    query = """SELECT ride_info.start_time, heart_rate.avg_heart_rate, power_w.avg_power FROM ride_info
               JOIN heart_rate on ride_info.heart_rate_id = heart_rate.heart_rate_id
               JOIN power_w on ride_info.power_id = power_w.power_id
               WHERE DATEDIFF('hour', start_time, now()) <= 24;"""
    riders_day_reading_df = pd.read_sql_table(query, conn, schema=HISTORICAL_SCHEMA)
    heart_fig = px.scatter(riders_day_reading_df, x="start_time", y="avg_heart_rate", color="avg_heart_rate", title="Average heart rate in the past day")
    heart_fig.update_layout(
    xaxis_title ="Time",
    yaxis_title ="Heart rate"
    )
    power_fig = px.scatter(riders_day_reading_df, x="start_time", y="avg_power", color="avg_power", title="Average power in the past day")
    power_fig.update_layout(
    xaxis_title ="Time",
    yaxis_title ="Power"
    )
    conn.close()
    engine.dispose()
    return heart_fig, power_fig


def html_write(total: str, gender: px, age: px, heart: px, power: px):
    """Writes the data into html"""
    with open(HTML_FILE, 'a') as f:
        f.write(f'<html>\n<head>\n<title>Daily Report</title>\n<link rel="stylesheet" href="./style.css">\n</head>\n<body>\n<div class="heading">\n<h1>Daily report</h1>\n<p1>{total}</p1>\n</div>\n<div class="container" >')
        f.write(gender.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(age.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(heart.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(power.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("\n</body>\n</html>")

def email_send():
    config = dotenv_values("./../.env")
    session = boto3.Session(aws_access_key_id=config["ACCESS_KEY"], aws_secret_access_key=config["SECRET_KEY"])
    ses = session.client("ses")
    email_recipients = {"ToAddresses": ["trainee.mohammed.simjee@sigmalabs.co.uk"], "CcAddresses": [], "BccAddresses": []}
    with open ('report_graph.html') as file:
        html_content = file_read()
    message = {"Subject": {"Data": "test"}, "Body": {"Html": {"Data": html_content}}}
    ses.send_email(Source="trainee.danishan.rahulan@sigmalabs.co.uk", Destination=email_recipients, Message=message)

if __name__ == "__main__": 
    load_dotenv()
    engine = get_db_connection(os.environ)
    total_riders = get_age_rider_past_day(engine)
    gender_fig = get_gender_rider_past_day(engine)
    age_fig = get_age_rider_past_day(engine)
    heart_fig, power_fig = get_avg_reading_riders_past_day(engine)
    html_write(total_riders, gender_fig, age_fig, heart_fig)
