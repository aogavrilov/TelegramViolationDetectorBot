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

