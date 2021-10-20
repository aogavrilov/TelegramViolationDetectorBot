from mysql.connector import Error


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


def get_count_of_messages_on_interval(connection, chat_id, interval):
    select_query = "SELECT COUNT(*) FROM messages WHERE chat_id = " + str(chat_id) + " AND datetime < " + \
                   str(interval[1]) + " AND datetime > " + str(interval[0])
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            result = cursor.fetchall()
            for row in result:
                return int(row[0])
    except():
        return 0


def add_chat(connection, chat_id, title, bot_status):
    command = "INSERT INTO chats(chat_id, chat_name, mean_messages_in_3_minutes, bot_status) VALUES (%s, %s, %s, %s)"
    values = (chat_id, title, 0, bot_status)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            print(e)
            return e


def drop_chat(connection, chat_id):
    command = "DELETE FROM chats WHERE chat_id = " + str(chat_id)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command)
            connection.commit()
            return 0
        except Error as e:
            print(e)
            return e


def get_chats(connection):
    select_query = "SELECT * FROM chats"
    chats = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            result = cursor.fetchall()
            print(result)
            for row in result:
                chats.append(row)
        return chats
    except():
        return chats

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