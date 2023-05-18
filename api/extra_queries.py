# pylint: disable=unused-variable
from json import load, dumps
from datetime import datetime
import psycopg2
import psycopg2.extras
from dotenv import dotenv_values
import json

config = dotenv_values('.env')

'''This contains extra queries we could use for the API'''

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

def get_city():
    '''SQL query to get all cities.'''
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT city FROM historical.rider_address;"
        # param = (rider_ID,)
        cur.execute(query)

        results = cur.fetchall()
        cities = []
        for row in results:
            cities.append(row["city"])
        return cities
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_total_riders_for_city(city: str):
    '''SQL query to get total number of rides for a given city.'''

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
        # print("Error connecting to database.", err)
        print(err)

def get_leadboard():

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = """SELECT rider.rider_id, rider.first_name, rider.last_name, ride_info.ride_info_id,
                    EXTRACT( epoch FROM( historical.ride_info.end_time - historical.ride_info.start_time)) as time_length
                FROM historical.rider
                JOIN historical.ride_info on rider.rider_id = ride_info.rider_id 
                WHERE rider.rider_id = 4526
                ORDER BY time_length DESC;"""
    # query = "SELECT rider.rider_id FROM historical.rider;"
    
    cur.execute(query)
    data = cur.fetchall()
    for row in data:
        print(f"Rider_id: {row['rider_id']}, Name: {row['first_name']} {row['last_name']}, ride_info_id: {row['ride_info_id']}, duration: {row['time_length']} seconds")

if __name__== "__main__":

    print(get_city())
    print(get_total_riders_for_city("North Raymond"))