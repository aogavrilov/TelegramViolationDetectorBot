import mysql
from mysql.connector import connect, Error
import configparser


def database_connect() -> mysql.connector:
    try:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        connection = connect(host=config["Database"]["host"],
                    user=config["Database"]["user"],
                    password=config["Database"]["password"],
                    database=config["Database"]["db_name"])
    except:
        connection = None
    return connection
"""    try:
        with connect(
                host=config["Database"]["host"],
                user=config["Database"]["user"],
                password=config["Database"]["password"],
                database=config["Database"]["db_name"],
        ) as connection:
            print(connection)
            return connection
    except Error as e:
        print(e)"""

