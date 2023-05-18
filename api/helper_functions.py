# pylint: disable=unused-variable
from datetime import datetime
import psycopg2
import psycopg2.extras
from dotenv import dotenv_values


config = dotenv_values('.env')

def get_db_connection():
    '''Establish a connect with the database'''
    try:
        # conn = psycopg2.connect("dbname=social_news user=abdirrahman host=localhost")
        conn = psycopg2.connect(
            user = config["DATABASE_USERNAME"],
            password = config["DATABASE_PASSWORD"],
            host = config["DATABASE_IP"],
            port = config["DATABASE_PORT"],
            database = config["DATABASE_NAME"]
            )
        print("Successful connection to the database")
        return conn
    except Exception as err:
        print("Error cannot connect to database.", err)

conn = get_db_connection()

def get_rider_ride_count(rider_id):
    '''SQL query to get number of rides for a given rider.'''

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT COUNT(*) FROM historical.ride_info WHERE rider_id = %s;"
        param = (rider_id,)
        cur.execute(query, param)


        results = cur.fetchall()

        return results
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_riders(rider_id: int):
    '''SQL query to get rides'''
# 4513-4530
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT rider.first_name, rider.last_name, rider.gender,\
                    rider.height_cm, rider.weight_kg,\
                    heart_rate.avg_heart_rate FROM\
                    historical.rider JOIN historical.ride_info ON\
                    rider.rider_id = ride_info.rider_id\
                    JOIN historical.heart_rate ON \
                    ride_info.heart_rate_id = heart_rate.heart_rate_id\
                    WHERE rider.rider_id = %s ;"
        param = (rider_id,)
        cur.execute(query, param)


        results = cur.fetchall()

        return results
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_rides(ride_id: int):
    '''SQL query to get riders information'''
# 107
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM historical.ride_info WHERE ride_info_id = %s"
        param = (ride_id,)
        cur.execute(query, param)


        results = cur.fetchall()

        return results

    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_all_riders_rides(rider_id: int):
    '''SQL query to get all rides for a rider with a specific ID' '''

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM historical.ride_info WHERE rider_id = %s"
        param = (rider_id,)
        cur.execute(query, param)


        results = cur.fetchall()

        return results

    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_daily_rides():
    '''SQL query to get rides of the date specified'''

    try:

        today = datetime.today().strftime('%d-%m-%Y')
        query_date = datetime.strptime(today,'%d-%m-%Y' )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM historical.ride_info WHERE DATE(end_time) = %s"
        param = (query_date,)
        cur.execute(query, param)


        results = cur.fetchall()

        return results
        # return today, query_date

    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_rides_by_date(date: str):
    '''SQL query to get rides of the date specified'''

    try:
        query_date = datetime.strptime(date,'%d-%m-%Y' )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM historical.ride_info WHERE DATE(end_time) = %s"
        param = (query_date,)
        cur.execute(query, param)

        results = cur.fetchall()

        return results
        # return query_date
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)


if __name__ == '__main__':
    # print(get_rides(107))
    # print(get_all_riders_rides(4513))
    # print("today",get_daily_rides())
    # print(get_rides_by_date("16-05-2023"))
    print(get_rider_ride_count(4513))
