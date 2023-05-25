"""This script creates a report from historical data for C-suit"""
from typing import Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, engine, URL
import pandas as pd
import numpy as np
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

from xhtml2pdf import pisa
import base64

from report_utils import REPORT_HTML, HTML_STYLE


HISTORICAL_SCHEMA = "historical"
HTML_FILE = "report_graph.html"
DIR_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
PDF_FILE_PATH = "/tmp/daily_report.pdf"


def get_db_connection() -> engine:
    """Connect to an rds using sqlalchemy engines"""
    try:
        url_object = URL.create(
        "postgresql+psycopg2",
        username=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        port=os.environ['DB_PORT']
    )
        return create_engine\
            (url_object,connect_args={'options': f"-csearch_path={HISTORICAL_SCHEMA}"})
    except Exception as err:
        print(err)
        print("Error connecting to database.")


def get_rider_past_day(engine_connection: engine) -> str:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine_connection.connect()
    query = """SELECT start_time FROM ride_info
            WHERE ride_info.end_time >= now() - INTERVAL '24 hours';"""
    riders_day_df = pd.read_sql(query, conn)
    total_riders = riders_day_df["start_time"].count()
    print_line = f"Total number of riders in the last 24 hours: {total_riders}"
    conn.close()
    engine_connection.dispose()
    return print_line


def get_gender_rider_past_day(engine_connection: engine) -> go.Figure:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine_connection.connect()
    query = """SELECT ride_info.start_time, rider.gender FROM ride_info
               JOIN rider on ride_info.rider_id = rider.rider_id 
               WHERE ride_info.end_time >= now() - INTERVAL '24 hours'"""
    riders_day_gender_df = pd.read_sql(query, conn)
    gender_count = riders_day_gender_df.groupby('gender')['start_time'].count().reset_index(name='count')
    gender_fig = px.bar(gender_count, x = 'gender', y = 'count', title="Gender split between riders in the last 24 hours")
    colours = ['#333333', '#7FC37E']
    gender_fig.data[0].marker.color = [colours[i % len(colours)] for i in range(len(gender_fig.data[0].y))]
    gender_fig.update_layout(
    xaxis_title='Gender',
    yaxis_title='Count',
    title = {
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 20, 'color': 'black'}
        }
    )
    conn.close()
    engine_connection.dispose()
    return gender_fig


def get_age_rider_past_day(engine_connection: engine) -> go.Figure:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine_connection.connect()
    query = """SELECT ride_info.start_time, rider.date_of_birth, gender FROM ride_info
               JOIN rider on ride_info.rider_id = rider.rider_id 
               WHERE ride_info.end_time >= now() - INTERVAL '24 hours'"""
    riders_day_age_df = pd.read_sql(query, conn)

    riders_day_age_df['start_time'] = pd.to_datetime(riders_day_age_df['start_time'])
    riders_day_age_df['date_of_birth'] =\
        pd.to_datetime(riders_day_age_df['date_of_birth'])
    riders_day_age_df['age'] =\
        ((riders_day_age_df['start_time'] - riders_day_age_df['date_of_birth'])\
         .dt.days.astype(float)) * 0.00273973 #converts to normal number
    riders_day_age_df['age'] = riders_day_age_df['age'].apply(np.floor)
    total_riders_age = group_age_data(riders_day_age_df)

    age_fig = px.bar(total_riders_age, x = 'age', y = 'count', title="Age group split between riders in the last 24 hours",
color = 'gender', color_discrete_sequence = ['#333333', '#7FC37E'])
    age_fig.update_layout(
    xaxis_title='Age',
    yaxis_title='Count',
    title = {
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 20, 'color': 'black'}
        }
    )
    conn.close()
    engine_connection.dispose()
    return age_fig


def group_age_data(riders_day_gender_df) -> pd.DataFrame:
    """Creates bings for age group brackets"""
    bins = [10, 20, 30, 40, 50, 60, 70, 105]
    labels = ['10-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71+']
    age_groups = pd.cut(riders_day_gender_df['age'], bins=bins, labels=labels, right=True)
    age_group_count = riders_day_gender_df.groupby([age_groups, 'gender'])['start_time'].count().reset_index(name='count')
    return age_group_count


def get_avg_reading_riders_past_day(engine_connection: engine) -> Tuple[go.Figure,]:
    """Use an sqlalchemy engine to connect to an rds and read data from rds."""
    conn = engine_connection.connect()
    query = """SELECT ride_info.start_time, heart_rate.avg_heart_rate, power_w.avg_power
               FROM ride_info
               JOIN heart_rate on ride_info.heart_rate_id = heart_rate.heart_rate_id
               JOIN power_w on ride_info.power_id = power_w.power_id
               WHERE ride_info.end_time >= now() - INTERVAL '24 hours'"""
    riders_day_reading_df = pd.read_sql(query, conn)
    heart_fig = px.scatter(riders_day_reading_df, x="start_time", y="avg_heart_rate", color="avg_heart_rate", title="Average heart rate per user in the past day",
                           color_continuous_scale='algae', labels={"avg_heart_rate": "AVG Heart Rate"})
    heart_fig.update_layout(
    xaxis_title ="Time",
    yaxis_title ="Heart rate",
    title = {
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 20, 'color': 'black'}
        },
    legend_title="AVG Heart Rate"
    )

    power_fig = px.scatter(riders_day_reading_df, x="start_time", y="avg_power", color="avg_power", title="Average power per user in the past day",
                           color_continuous_scale='algae', labels={"avg_power": "AVG Power"})
    power_fig.update_layout(
    xaxis_title ="Time",
    yaxis_title ="Power",
    title = {
         'x':0.5,
         'xanchor': "center",
         'font': {'size': 20, 'color': 'black'}
        },
        legend_title="AVG Power Output"
    )
    conn.close()
    engine_connection.dispose()
    return heart_fig, power_fig


def generate_source_html(figures: list, html_layout: str, html_style: str, title_message: str) -> str:
    """Generates the html for the pdf as a string, formatting the images into
    html format along the way"""
    template = ('<img src="data:image/png;base64,{image}">')
    images = [base64.b64encode(figure.to_image()).decode('utf-8') for figure in figures]
    gender_graph, age_graph, hrt_graph, power_graph = [template.format(image=image) for image in images]
    return html_layout.format(style=html_style, print_line=title_message,
                              gender_graph=gender_graph, age_graph=age_graph,
                              hrt_graph=hrt_graph, power_graph=power_graph,
                              file_path=DIR_FILE_PATH)


def convert_html_to_pdf(source_html: str, output_filename: str) -> str:
    """Writes the html code to a pdf file"""
    result_file = open(output_filename, "w+b")
    pisa_status = pisa.CreatePDF(
            source_html,
            dest=result_file)
    result_file.close()
    return pisa_status.err


def email_send() -> None:
    """sends email using ses"""
    region = "eu-west-2"
    sws_user = os.environ["ACCESS_KEY"]
    sws_key = os.environ["SECRET_KEY"]
    subject = 'Sending email with Attachment '
    body = "Dear Sir/Madam,\
    \n\nPlease find our daily report file attached in the form of a PDF File.\
    \n\nKind regards,\n\nDeloton Team"
    client = boto3.client(service_name = 'ses', region_name = region,\
                          aws_access_key_id = sws_user, aws_secret_access_key = sws_key)

    message = MIMEMultipart()
    message['Subject'] = subject

    body_html = f"<pre>{body}</pre>"
    part = MIMEText(body_html, 'html')
    message.attach(part)

    with open(PDF_FILE_PATH, 'r', encoding="latin-1") as file:
        part = MIMEApplication(file.read(), 'pdf')
        part.add_header("Content-Disposition",
                            "attachment",
                            filename=os.path.basename(PDF_FILE_PATH))
    message.attach(part)
    try:
        result = client.send_raw_email(Source = "trainee.dani.rahulan@sigmalabs.co.uk",\
                                       Destinations = ["trainee.ben.corrigan@sigmalabs.co.uk"],\
                                        RawMessage = {'Data': message.as_string(),})
        print( {'message': 'error','status' : 'fail'}\
              if 'ErrorResponse' in result \
              else {'message': 'mail sent successfully', 'status' : 'success'})
    except ClientError as e:
        print ({'message': e.response['Error']['Message'],'status' : 'fail'})



def handler(event, context):
    print("Starting the stuff")
    load_dotenv()
    db_engine = get_db_connection()

    print_line = get_rider_past_day(db_engine)
    gender_fig = get_gender_rider_past_day(db_engine)
    age_fig = get_age_rider_past_day(db_engine)
    heart_fig, power_fig = get_avg_reading_riders_past_day(db_engine)


    report_html = generate_source_html([gender_fig, age_fig, heart_fig, power_fig]\
                                       ,REPORT_HTML, HTML_STYLE, print_line)
    convert_html_to_pdf(report_html, PDF_FILE_PATH)
    print("sending email")
    email_send()
