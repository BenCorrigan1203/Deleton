from dotenv import load_dotenv
from s3fs import S3FileSystem
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, engine
import pandas as pd


DAILY_SCHEMA = "daily"
HISTORICAL_SCHEMA = "historical"
USER_TABLE = ""
ADDRESS_TABLE = ""
RIDE_TABLE = ""
RIDEMETA_TABLE = ""

def get_db_connection(daily: bool, config: dict=os.environ):
    """establishes connection to database"""
    schema = DAILY_SCHEMA if daily else HISTORICAL_SCHEMA
    try:
        connection = psycopg2.connect(user = config["DATABASE_USERNAME"], \
                                      password = config["DATABASE_PASSWORD"],\
                                      host = config["DATABASE_IP"], \
                                      port = config["DATABASE_PORT"], \
                                      database = "", \
                                      options=f"-c search_path={schema}") 
        return connection
    except Exception as err:
        print("Error connecting to database.")
        print(err)

def get_24_hours(config: dict) -> pd.DataFrame:
    "connect and extract 24 hour data from schema, RDS"
    conn = get_db_connection(daily=True)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """SELECT *
                FROM ride_metadata
                JOIN ride ON ride.ride_id = ride_metadata.ride_id
                JOIN user ON user.user_id = ride.user_id
                JOIN address ON address.address_id = user.address_id
                WHERE DATEDIFF(hour, ride_metadata.recording_taken, now()) <= 24"""
    cur.execute(query)
    data_date = cur.fetchall()
    cur.close()
    conn.close()


def delete_12_hours(config: dict) -> pd.DataFrame:
    "connect and extract 24 hour data from schema, RDS"
    conn = get_db_connection(daily=True)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """DELETE FROM ride_metadata
                WHERE DATEDIFF(hour, ride_metadata.recording_taken, now()) > 12"""
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

def merge_all_df(user_day_df: pd.DataFrame, address_day_df: pd.DataFrame, ride_day_df: pd.DataFrame, ridemeta_day_df: pd.DataFrame) -> pd.DataFrame:
   merged_df = pd.merge(user_day_df, address_day_df, on=address)

if __name__ == "__main__": 
    config = load_dotenv()
    data_24 = get_24_hours(config)
    delete_12_hours(config)
    merged_df = merge_all_df(user_day_df, address_day_df, ride_day_df, ridemeta_day_df)
