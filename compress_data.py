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
                                      database = "") 
        return connection
    except Exception as err:
        print("Error connecting to database.")
        print(err)

def insert_24_hours(config: dict) -> pd.DataFrame:
    "connect and extract 24 hour data from schema and insert to historical schema"
    conn = get_db_connection(daily=True)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    user_query = f""" INSERT INTO {HISTORICAL_SCHEMA}.user
                      SELECT * FROM {DAILY_SCHEMA}.user
                      WHERE user_id IN(
                      SELECT user_id FROM {DAILY_SCHEMA}.ride
                      JOIN {DAILY_SCHEMA}.ride_metadata ON ride.ride_id = ride_metadata.ride_id
                        WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                      );"""
    cur.execute(user_query)

    user_address_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.user_address
                             SELECT * FROM {DAILY_SCHEMA}.user_address
                             WHERE address_id IN(
                             SELECT address_id FROM {DAILY_SCHEMA}.user
                                WHERE user_id IN(
                                SELECT user_id FROM {DAILY_SCHEMA}.ride
                                JOIN {DAILY_SCHEMA}.ride_metadata ON ride.ride_id = ride_metadata.ride_id
                                    WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                                    )
                            );"""
    cur.execute(user_address_query)

    rpm_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.rpm (avg_rpm, max_rpm, min_rpm)
                    SELECT
                        AVG(ride_metadata.rpm),
                        MAX(ride_metadata.rpm),
                        MIN(ride_metadata.rpm)
                    FROM {DAILY_SCHEMA}.ride_metadata
                    WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                    GROUP BY ride_metadata.ride_id
                    RETURNING rpm_id, ride_id;"""
    cur.execute(rpm_query)
    rpm_row = cur.fetchall()
    rpm_id = rpm_row['rpm_id']
    ride_id = rpm_row['ride_id']

    resistance_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.resistance (avg_resistance, max_resistance, min_resistance)
                    SELECT
                        AVG(ride_metadata.resistance),
                        MAX(ride_metadata.resistance),
                        MIN(ride_metadata.resistance)
                    FROM {DAILY_SCHEMA}.ride_metadata
                    WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                    GROUP BY ride_metadata.ride_id
                    RETURNING resistance_id;"""
    cur.execute(resistance_query)
    resistance_id = cur.fetchone()[0]

    power_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.power (avg_power, max_power, min_power)
                    SELECT
                        AVG(ride_metadata.power),
                        MAX(ride_metadata.power),
                        MIN(ride_metadata.power)
                    FROM {DAILY_SCHEMA}.ride_metadata
                    WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                    GROUP BY ride_metadata.ride_id
                    RETURNING power_id;"""
    cur.execute(power_query)
    power_id = cur.fetchone()[0]

    heart_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.heart_rate (avg_heart_rate, max_heart_rate, min_heart_rate)
                    SELECT
                        AVG(ride_metadata.heart_rate),
                        MAX(ride_metadata.heart_rate),
                        MIN(ride_metadata.heart_rate)
                    FROM {DAILY_SCHEMA}.ride_metadata
                    WHERE DATEDIFF('hour', ride_metadata.recording_taken, now()) <= 24
                    GROUP BY ride_metadata.ride_id
                    RETURNING heart_rate_id;"""
    cur.execute(heart_query)
    heart_id = cur.fetchone()[0]

    ride_data_query = f"""SELECT start_time, end_time, rider_id, bike_serial FROM ride WHERE ride_id = %s"""
    cur.execute(ride_data_query, (ride_id,))
    ride_data = cur.fetchall()
    start_time = ride_data["start_time"]
    end_time = ride_data["end_time"]
    rider_id = ride_data["rider_id"]
    bike_serial = ride_data["bike_serial"]
    
    ride_info_query = f"""INSERT INTO {HISTORICAL_SCHEMA}.ride_info 
                          (start_time, end_time, rider_id, bike_serial, heart_rate_id, resistance_id, power_id, rpm_id)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""
    cur.execute(ride_info_query, (start_time, end_time, rider_id, bike_serial, heart_id, resistance_id, power_id,rpm_id,))
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
