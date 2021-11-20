from mysql.connector import Error
#todo SQL Injactions Sequrity

def show_databases(connection) -> []:
    with connection.cursor() as cursor:
        command = "SHOW DATABASES"
        try:
            databases = []
            cursor.execute(command)
            for db in cursor:
                databases.append(db)
            return databases
        except Error as e:
            print(e)
            return e


def create_database(connection, database_name: str) -> str:
    with connection.cursor() as cursor:
        command = "CREATE DATABASE " + database_name
        try:
            cursor.execute(command)
            return 0
        except Error as e:
            print(e)
            return e


def append_message(connection, chat_id: int, user_id: int, message: str, message_id: int, is_flood: int, datetime: int) -> str:
    command = "INSERT INTO messages(chat_id, user_id, message, message_id, is_flood, datetime, is_deleted) VALUES " \
              "(%s, %s, %s, %s, %s, %s, 0)"
    values = (chat_id, user_id, message, message_id, is_flood, datetime)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            print(e)
            return e


def get_messages(connection, user_id, chat_id, limit=10, is_deleted=0) -> ([], []):
    select_query = "SELECT message, message_id FROM messages WHERE user_id = " + str(user_id) + \
                          " AND chat_id = " + str(chat_id) +" AND is_deleted = " + str(is_deleted) + \
                   " ORDER BY id DESC LIMIT " + str(limit)
    messages = []
    ids = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            result = cursor.fetchall()
            for row in result:
                messages.append(row[0])
                ids.append(row[1])
        return messages, ids
    except():
        return messages, ids


def get_count_of_messages_on_interval(connection, chat_id, interval) -> int:
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


def get_flood_status(connection, chat_id) -> str:
    select_query = "SELECT is_flood FROM chats WHERE chat_id = " + str(chat_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query) #todo сделать логгирование инцидентов в таблицы удаления пользователя,
            # мута пользователя, кика пользователя с описанием причины, вызвавшей инцидент
            result = cursor.fetchall()
            for row in result:
                return int(row[0])
    except():
        return 0


def update_flood_status(connection, chat_id, status) -> str:
    select_query = "UPDATE chats SET is_flood = " + str(status) + " WHERE chat_id = " + str(chat_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query) #todo сделать логгирование инцидентов в таблицы удаления пользователя,
            connection.commit()
            return 0
    except Error as e:
        print(e)
        return e


def update_chat_average_messages(connection, chat_id, value) -> str:
    command = "UPDATE chats SET mean_messages_in_3_minutes = " + str(value) + " WHERE chat_id = " + str(chat_id)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command)
            connection.commit()
            return 0
        except Error as e:
            print(e)
            return e


def update_message_is_flood_status(connection, chat_id, message_id, is_flood) -> str:
    command = "UPDATE messages SET is_deleted = " + str(is_flood) + " WHERE chat_id = " + str(chat_id) + \
              " AND message_id = " + str(message_id)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command)
            connection.commit()
            return 0
        except Error as e:
            print(e)
            return e



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
"""
def drop_table(connection, table_name: str):
    command = "DROP TABLE " + table_name
    with connection.cursor() as cursor:
        cursor.execute(table_name)"""