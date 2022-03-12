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
        print("DB connected in DataBase/Connector")
    except Exception as e:
        print(e)

        connection = None
    return connection

