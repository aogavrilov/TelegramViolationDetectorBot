from mysql.connector import connect, Error
import configparser


def database_connect():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    connection = connect(host=config["Database"]["host"],
                user=config["Database"]["user"],
                password=config["Database"]["password"],
                database=config["Database"]["db_name"])
    return connection