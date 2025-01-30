import mysql.connector
from decouple import config

def get_connection():
    try:
        return mysql.connector.connect(host=config('MYSQL_HOST'),
                                       database=config('MYSQL_BD'),
                                       port=config('MYSQL_PORT'),
                                       user=config('MYSQL_USER'),
                                       password=config('MYSQL_PASSWORD'))
    except Exception as e:
        print(e)
