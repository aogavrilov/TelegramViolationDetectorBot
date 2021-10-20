from mysql.connector import connect, Error
import configparser


def send_command(connection, command):
    with connection.cursor() as cursor:
        try:
            cursor.execute(command)
            return 0
        except Error as e:
            return e
