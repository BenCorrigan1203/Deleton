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
    '''SQL query to get cities.'''

    try:
        rider_ID = 'Walshtown'
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT city FROM historical.rider_address;"
        # param = (rider_ID,)
        cur.execute(query)


        results = cur.fetchall()
        return results
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

def get_total_riders_for_city():
    '''SQL query to get total number of rides for a given city.'''

    try:
        rider_ID = 'Walshtown'
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT COUNT(*) AS total_riders FROM historical.rider\
              JOIN historical.rider_address ON rider.address_id = rider_address.address_id\
                WHERE rider_address.city = %s;"
        param = (rider_ID,)
        cur.execute(query, param)


        results = cur.fetchall()
            
        return results
    except Exception as err:
        # print("Error connecting to database.", err)
        print(err)

if __name__== "__main__":

    print(get_city())