from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from typing import List, Tuple
import os
from compress_sql import ADDRESS_SQL, RIDER_SQL, METADATA_SQL, RESISTANCE_SQL, POWER_SQL, HEART_SQL, RPM_SQL, RIDE_SQL, RIDE_INFO_SQL, DELETE_META_SQL, DELETE_RIDE_SQL


def get_db_connection(config: dict=os.environ) -> connection:
    """establishes connection to database"""
    try:
        connection = psycopg2.connect(user = config["DB_USER"], \
                                      host = config["DB_HOST"], \
                                      database = config["DB_NAME"],\
                                      password = config["DB_PASSWORD"],\
                                      port = config["DB_PORT"])
        return connection
    except Exception as err:
        print("Error connecting to database.")
        print(err)


def insert_rider_and_address(conn: connection):
    "connect and extract 24 hour data from schema and insert to historical schema"
    cur = conn.cursor(cursor_factory=RealDictCursor)
    """Copying across rider_address to historical schema"""
    cur.execute(ADDRESS_SQL)
    
    """Copying across rider table to historical schema"""
    cur.execute(RIDER_SQL)
    conn.commit()
    cur.close()

def get_metadata(conn: connection):
    """extracting all metadata readings"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(METADATA_SQL)
    meta_data = cur.fetchall()
    conn.commit()
    cur.close()
    return meta_data

    
def insert_resis_power_rpm_heart(conn: connection, meta_data: list[dict]) -> Tuple[List[int],List[int],List[int],List[int]]:
    """Inserting all readings in appropriate tables"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    resistance_id = []
    power_id = []
    heart_id = []
    rpm_id = []
    for i in range(len(meta_data)):
        """Inserting resistance readings and returning id"""
        cur.execute(RESISTANCE_SQL, (meta_data[i]["resistance_avg"],meta_data[i]["resistance_max"],meta_data[i]["resistance_min"],meta_data[i]["resistance_avg"],meta_data[i]["resistance_max"],meta_data[i]["resistance_min"],))
        resistance_id.append(cur.fetchone()['resistance_id'])

        """Inserting power readings and returning id"""
        cur.execute(POWER_SQL, (meta_data[i]["power_avg"],meta_data[i]["power_max"],meta_data[i]["power_min"],meta_data[i]["power_avg"],meta_data[i]["power_max"],meta_data[i]["power_min"],))
        power_id.append(cur.fetchone()['power_id'])

        """Inserting heart readings and returning id"""
        cur.execute(HEART_SQL, (meta_data[i]["heart_avg"],meta_data[i]["heart_max"],meta_data[i]["heart_min"],meta_data[i]["heart_avg"],meta_data[i]["heart_max"],meta_data[i]["heart_min"],))
        heart_id.append(cur.fetchone()['heart_rate_id'])


        "Inserting rpm readings and returning id"
        cur.execute(RPM_SQL, (meta_data[i]["rpm_avg"],meta_data[i]["rpm_max"],meta_data[i]["rpm_min"],meta_data[i]["rpm_avg"],meta_data[i]["rpm_max"],meta_data[i]["rpm_min"],))
        rpm_id.append(cur.fetchone()['rpm_id'])
    conn.commit()
    cur.close()
    return heart_id, resistance_id, power_id, rpm_id


def insert_ride_info(conn: connection, meta_data: list[dict], heart_id: list, resistance_id: list, power_id: list, rpm_id: list):
    """gathering and inserting ride_info data"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    ride_id = []
    for i in range(len(meta_data)):
        """Gather ride details"""
        cur.execute(RIDE_SQL, (meta_data[i]['ride_id'],))
        ride_data = cur.fetchall()
        """Insert ride_info data"""
        cur.execute(RIDE_INFO_SQL, (ride_data[0]['start_time'], ride_data[0]['end_time'], ride_data[0]['rider_id'], ride_data[0]['bike_serial'], heart_id[i], resistance_id[i], power_id[i] ,rpm_id[i],))
    conn.commit()
    cur.close()


def delete_12_hours(conn: connection):
    "Delete last 12 hour rides and metadata in daily schema"
    cur = conn.cursor(cursor_factory=RealDictCursor)
    """delete last 12 hours of data from ride_metadata"""
    cur.execute(DELETE_META_SQL)

    """delete last 12 hours of data from ride"""
    cur.execute(DELETE_RIDE_SQL)
    conn.commit()
    cur.close()

if __name__ == "__main__": 
    load_dotenv()
    conn = get_db_connection(os.environ)
    insert_rider_and_address(conn)
    meta_data = get_metadata(conn)
    heart_id, resistance_id, power_id, rpm_id = insert_resis_power_rpm_heart(conn, meta_data)
    insert_ride_info(conn, meta_data, heart_id, resistance_id, power_id, rpm_id)
    delete_12_hours(conn)
    conn.close()
