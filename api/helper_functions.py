# pylint: disable=unused-variable
import os
from datetime import datetime
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


def get_credentials():
    '''Retrive AWS credentials from local environment'''
    try:
        load_dotenv()
        config = os.environ
        return config
    except Exception as err:
        print("Error loading environment variables", err)

def get_db_connection():
    '''Establish a connect with the database'''
    config = get_credentials()
    try:
        conn = psycopg2.connect(
            user = config.get("DATABASE_USERNAME"),
            password = config.get("DATABASE_PASSWORD"),
            host = config.get("DATABASE_IP"),
            port = config.get("DATABASE_PORT"),
            database = config.get("DATABASE_NAME")
            )
        print("Successful connection to the database")
        return conn
    except Exception as err:
        print("Error cannot connect to database.", err)

conn = get_db_connection()

def get_rider_ride_count(rider_id) -> list[dict]:
    '''Get number of rides for a given rider.'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT COUNT(*) FROM historical.ride_info WHERE rider_id = %s;"""
        param = (rider_id,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def get_riders(rider_id: int) -> list[dict]:
    '''Get rides of specified rider using rider's ID'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT rider.first_name, rider.last_name, rider.gender,
                    rider.height_cm, rider.weight_kg,
                    heart_rate.avg_heart_rate FROM
                    historical.rider JOIN historical.ride_info ON
                    rider.rider_id = ride_info.rider_id
                    JOIN historical.heart_rate ON 
                    ride_info.heart_rate_id = heart_rate.heart_rate_id
                    WHERE rider.rider_id = %s ;"""
        param = (rider_id,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def get_rides(ride_id: int) -> list[dict]:
    '''Get information on rides'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT * FROM historical.ride_info WHERE ride_info_id = %s"""
        param = (ride_id,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def delete_rides(ride_id: int) -> None:
    '''Delete ride information using specified ride's ID'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """DELETE * FROM historical.ride_info WHERE ride_info_id = %s"""
        param = (ride_id,)
        cur.execute(query, param)
    except Exception as err:
        print("Error connecting to database.", err)

def get_all_riders_rides(rider_id: int) -> list[dict]:
    '''Get all rides for a rider with a specific ID' '''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT * FROM historical.ride_info WHERE rider_id = %s"""
        param = (rider_id,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def get_daily_rides() -> list[dict]:
    '''Get rides of the date specified'''
    try:
        today = datetime.today().strftime('%d-%m-%Y')
        query_date = datetime.strptime(today,'%d-%m-%Y' )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT * FROM daily.ride WHERE DATE(end_time) = %s"""
        param = (query_date,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def get_rides_by_date(date: str) -> list[dict]:
    '''Get rides of the date specified'''
    try:
        query_date = datetime.strptime(date,'%d-%m-%Y' )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT * FROM historical.ride_info WHERE DATE(end_time) = %s"""
        param = (query_date,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)

def get_leaderboard() -> list[dict]:
    '''Get ordered list of riders ride count'''
    query = """SELECT rider.rider_id, rider.first_name, rider.last_name,
                COUNT(ride_info.ride_info_id) AS count_rides
                FROM historical.rider
                JOIN historical.ride_info on rider.rider_id = ride_info.rider_id 
                GROUP BY historical.rider.rider_id, rider.first_name, rider.last_name
                ORDER BY count_rides DESC;"""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query)
    data = cur.fetchall()
    leaderboard = []
    position = 1
    for row in data:
        rider_id = row['rider_id']
        f_name = row['first_name']
        l_name = row['last_name']
        ride_count = row['count_rides']
        leaderboard.append({"Position": f"{position}",\
                             "Rider Id": f"{rider_id}",\
                                "Name": f"{f_name} {l_name}",\
                                      "Ride count": f"{ride_count}"})
        position += 1
    return leaderboard

def get_rider_durations(rider_id: int) -> list[dict]:
    '''Get duration of specified rider's rides'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT rider.rider_id, rider.first_name, rider.last_name, ride_info.ride_info_id,
                    EXTRACT( epoch FROM( historical.ride_info.end_time - historical.ride_info.start_time)) as time_length
                FROM historical.rider
                JOIN historical.ride_info on rider.rider_id = ride_info.rider_id 
                WHERE rider.rider_id = %s
                ORDER BY time_length DESC;"""
        param = (rider_id,)
        cur.execute(query, param)

        results = cur.fetchall()
        durations = []
        for row in results:
            durations.append({"Rider_id": f"{row['rider_id']}",\
                               "Name": f"{row['first_name']} {row['last_name']}",\
                                  "Duration": f"{row['time_length']} seconds"})

        return durations
    except Exception as err:
        print("Error connecting to database.", err)

def get_city() -> list[dict]:
    '''Get all current cities with rides.'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT city FROM historical.rider_address;"
        cur.execute(query)

        results = cur.fetchall()
        cities = []
        for row in results:
            cities.append(row["city"])
        return cities
    except Exception as err:
        print("Error connecting to database.", err)

def get_total_riders_for_city(city: str) -> list[dict]:
    '''Get total number of rides for a given city.'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """SELECT COUNT(*) AS total_riders FROM historical.rider
              JOIN historical.rider_address ON rider.address_id = rider_address.address_id
                WHERE rider_address.city = %s"""
        param = (city,)
        cur.execute(query, param)

        results = cur.fetchall()
        return results
    except Exception as err:
        print("Error connecting to database.", err)
