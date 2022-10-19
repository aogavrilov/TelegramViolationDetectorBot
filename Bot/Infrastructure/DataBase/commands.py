from datetime import datetime

from mysql.connector import Error

import logging

logging.basicConfig(filename="logs/db.log", level=logging.INFO)
log = logging.getLogger("ex")
#todo SQL Injections Sequrity


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
            log.exception(e, ' in show_databases')
            return e


def create_database(connection, database_name: str) -> str:
    with connection.cursor() as cursor:
        command = "CREATE DATABASE " + database_name
        try:
            cursor.execute(command)
            return 0
        except Error as e:
            log.exception(e, ' in create_database')
            return e


def append_message(connection, chat_id: int, user_id: int, message: str, message_id: int, is_flood: int, datetime: int) -> str:

    command = "INSERT INTO messages(chat_id, user_id, message, message_id, datetime, is_deleted) VALUES " \
              "(%s, %s, %s, %s, %s, 0)"
    values = (chat_id, user_id, message, message_id, datetime)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in append_message')
            return e



def get_messages(connection, user_id, chat_id, limit=10, is_deleted=0) -> ([], []):
    select_query = "SELECT message, message_id FROM messages WHERE user_id = %s AND chat_id = %s AND is_deleted = %s " \
                   "ORDER BY id DESC LIMIT %s"
    values = (user_id, chat_id, is_deleted, limit)
    messages = []
    ids = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, values)
            result = cursor.fetchall()
            for row in result:
                messages.append(row[0])
                ids.append(row[1])
        return messages, ids
    except():
        return messages, ids


def get_nsfw_messages(connection, chat_id=None, limit=100):
    if chat_id is None:
        select_query = "SELECT message, message_id FROM messages AS msgs INNER JOIN incidents AS incdnts ON " \
                       "msgs.message_id = incdnts.incident_values ORDER BY message_id DESC LIMIT = %s "
        values = (limit)
    else:
        select_query = "SELECT message, message_id FROM messages AS msgs INNER JOIN incidents AS incdnts ON " \
                       "msgs.message_id = incdnts.incident_values where incdnts.chat_id = %s ORDER BY " \
                       "message_id DESC LIMIT = %s "
        values = (chat_id, limit)
    messages = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, values)
            result = cursor.fetchall()
            for row in result:
                messages.append(row)
        return messages
    except():
        return messages


def get_count_of_messages_on_interval(connection, chat_id, interval) -> int:
    select_query = "SELECT COUNT(*) FROM messages WHERE chat_id = %s AND datetime < %s AND datetime > %s"
    values = (chat_id, interval[1], interval[0])
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, values)
            result = cursor.fetchall()
            for row in result:
                return int(row[0])
    except():
        return 0


def get_flood_status(connection, chat_id) -> str:
    select_query = "SELECT is_flood FROM chats WHERE chat_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (chat_id,)) #todo сделать логгирование инцидентов в таблицы удаления пользователя,
            # мута пользователя, кика пользователя с описанием причины, вызвавшей инцидент
            result = cursor.fetchall()
            for row in result:
                return int(row[0])
    except():
        return 0


def update_flood_status(connection, chat_id, status) -> str:
    select_query = "UPDATE chats SET is_flood = %s WHERE chat_id = %s"
    values = (status, chat_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, values) #todo сделать логгирование инцидентов в таблицы удаления пользователя,
            connection.commit()
            return 0
    except Error as e:
        log.exception(e, ' in update_flood_status')
        return e


def update_chat_average_messages(connection, chat_id, value) -> str:
    command = "UPDATE chats SET mean_messages_in_3_minutes = %s WHERE chat_id = %s"
    values = (value, chat_id)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in update_chat_average_messages')
            return e


def update_message_is_deleted_status(connection, chat_id, message_id, is_deleted) -> str:
    command = "UPDATE messages SET is_deleted = %s WHERE chat_id = %s AND message_id = %s"
    values = (str(is_deleted), str(chat_id), str(message_id))
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in update_message_is_deleted_status')
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
            log.exception(e, ' in add chat')
            return e


def drop_chat(connection, chat_id):
    command = "DELETE FROM chats WHERE chat_id = %s"
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, (chat_id,))
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in drop_chat')
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


def write_incident(connection, chat_id, user_id, applied_action, incident_type, incident_proofs):
    command = "INSERT INTO incidents(chat_id, user_id, action, incident_type, incident_values, datetime) VALUES " \
              "(%s, %s, %s, %s, %s, %s)"
    now = datetime.now()
    values = (chat_id, user_id, applied_action, incident_type, incident_proofs, str(now))
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in write incident')
            return e
    pass


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