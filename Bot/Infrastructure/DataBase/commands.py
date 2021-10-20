from mysql.connector import connect, Error
import configparser


def show_databases(connection) -> str:
    with connection.cursor() as cursor:
        command = "SHOW DATABASES"
        try:
            databases = []
            cursor.execute(command)
            for db in cursor:
                databases.append(db)
            return databases
        except Error as e:
            return e


def create_database(connection, database_name: str) -> str:
    with connection.cursor() as cursor:
        command = "CREATE DATABASE " + database_name
        try:
            cursor.execute(command)
            return 0
        except Error as e:
            return e

"""
    command = "insert into messages(chat_id, user_id, message, is_flood) values(%s,%s,%s,%s)"
    values = (message.chat.id, message.from_user.id, message.text, 0)
    with connection.cursor() as cursor:
        cursor.execute(command, values)
        connection.commit()
"""


def append_message(connection, chat_id: int, user_id: int, message: str, is_flood: int, datetime: int) -> str:
    command = "INSERT INTO messages(chat_id, user_id, message, is_flood, datetime) VALUES (%s, %s, %s, %s, %s)"
    values = (chat_id, user_id, message, is_flood, datetime)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            return e


def get_messages(connection, user_id, chat_id):
    select_query = "SELECT * FROM messages WHERE user_id = " + str(user_id) + \
                          " AND chat_id = " + str(chat_id) + " ORDER BY id DESC LIMIT 10"
    messages = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            result = cursor.fetchall()
            for row in result:
                messages.append(row[3])
        return messages
    except():
        return messages


"""
def create_table(connection, database_name: str, table_name: str) -> str:
    with connection.cursor() as cursor:
        command = ""
        try:
            cursor.execute(command)
            return 0
        except Error as e:
            return e
"""

def drop_table(connection, table_name: str):
    command = "DROP TABLE " + table_name
    with connection.cursor() as cursor:
        cursor.execute(table_name)