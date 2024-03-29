from datetime import datetime

from mysql.connector import Error

import logging

from Bot.Infrastructure.Chats.ChatRules import ChatRules

logging.basicConfig(filename="logs/db.logs", level=logging.INFO)
log = logging.getLogger("ex")


# todo SQL Injections Sequrity


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


def append_message(connection, chat_id: int, user_id: int, message: str, message_id: int, is_flood: int,
                   datetime: int, chat_name: str, user_name: str) -> str:
    command = "INSERT INTO messages(chat_id, user_id, message, message_id, datetime, is_deleted, chat_name, user_name) VALUES " \
              "(%s, %s, %s, %s, %s, 0, %s, %s)"
    values = (chat_id, user_id, message, message_id, datetime, chat_name, user_name)
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
            cursor.execute(select_query,
                           (chat_id,))  # todo сделать логгирование инцидентов в таблицы удаления пользователя,
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
            cursor.execute(select_query,
                           values)  # todo сделать логгирование инцидентов в таблицы удаления пользователя,
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


def get_chat_rules(connection, obscenity_model, offense_model, threat_model, chat_id) -> str:
    select_query = "SELECT on_obscenity, on_offense, on_threat, on_other_violation FROM chat_configs WHERE chat_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (chat_id,))
            result = cursor.fetchall()
            for row in result:
                return ChatRules(obscenity_model, offense_model, threat_model, on_obscenity=row[0],
                                 on_offense=row[1], on_threat=row[2], on_other_violation=row[3])
    except():
        return ChatRules(obscenity_model, offense_model, threat_model, on_obscenity="0,0,0",
                         on_offense="0,0,0", on_threat="0,0,0", on_other_violation="0,0,0")



def get_count_of_chat_rules(connection, chat_id) -> int:
    select_query = "SELECT COUNT(*) FROM chat_configs WHERE chat_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (chat_id,))
            result = cursor.fetchall()
            for row in result:
                return int(row[0])
    except():
        return 0

def create_chat_rules(connection, chat_id, chat_rules: dict):
    command = "INSERT INTO chat_configs(chat_id, on_obscenity, on_offense, on_other_violation, on_threat) VALUES " \
              "(%s, %s, %s, %s, %s)"
    values = (chat_id, chat_rules['obscenity'], chat_rules['offense'], chat_rules['other'], chat_rules['threat'])
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in chat rules create incident')
            return e
    pass


def update_chat_rules(connection, chat_id, chat_rules: dict) -> str:
    command = "UPDATE chat_configs SET on_obscenity = %s, on_offense = %s, on_other_violation = %s, " \
              "on_threat = %s  WHERE chat_id = %s"
    values = (chat_rules['obscenity'], chat_rules['offense'], chat_rules['other'], chat_rules['threat'], chat_id)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in chat rules update')
            return e


def get_chat_banned_sticker_pack_names(connection, chat_id) -> set:
    select_query = "SELECT * FROM banned_sticker_packs WHERE chat_id = %s"
    names = set()
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (chat_id, ))
            result = cursor.fetchall()
            for row in result:
                names.add(row[1])
        return names
    except():
        return names


def add_pack_to_banned_stickers(connection, chat_id, pack_name: str):
    command = "INSERT INTO banned_sticker_packs(chat_id, pack_name) VALUES (%s, %s)"
    values = (chat_id, pack_name)
    with connection.cursor() as cursor:
        try:
            cursor.execute(command, values)
            connection.commit()
            return 0
        except Error as e:
            log.exception(e, ' in chat add pack to banned stickers')
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
