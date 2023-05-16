from dotenv import load_dotenv
import psycopg2
import os

def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(user = os.environ["DB_USER"],
            host = os.environ["DB_HOST"],
            database = os.environ["DB_NAME"],
            password = os.environ['DB_PASSWORD'],
            port = os.environ['DB_PORT'],
            options=f"-c search_path={os.environ['SCHEMA']}"
        )
        return conn
    except Exception as err:
        print(err)
        print("Error connecting to database.")


def create_tables() -> None:
    """Creates tables in the connected database"""
    with conn.cursor() as cur:
        with open("create_db.sql", "r", encoding='utf-8') as sql:
            cur.execute(sql.read())
    conn.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
    create_tables()