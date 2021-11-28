import sys

sys.path.insert(0, '/path/to/application/app/folder')
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Infrastructure.DataBase.commands import get_count_of_messages_on_interval, get_chats, \
    update_chat_average_messages, update_flood_status
from Bot.Telegram.Connection import bot_connect
import time
from datetime import datetime

EMA_CONST = 0.99

dp2 = bot_connect()

while True:
    database_connection = database_connect()  # todo сделать несколько периодов времени, поскольку активность в 12 дня и в 1 час ночи отличаются
    now = datetime.now()
    curr_time = now.year + now.month * 12 + now.day * 31 + now.hour * 24 + now.minute
    for chat in get_chats(database_connection):
        chat_id = chat[3]
        database_mean_messages_in_3_minutes = chat[4]
        current_mean_messages_in_3_minutes = get_count_of_messages_on_interval(database_connection, chat_id,
                                                                               [curr_time - 3, curr_time])
        current_value = database_mean_messages_in_3_minutes * EMA_CONST + (1 - EMA_CONST) \
                        * current_mean_messages_in_3_minutes
        update_chat_average_messages(database_connection, chat_id, current_value)
        update_flood_status(database_connection, chat_id, 0)
    database_connection.close()
    time.sleep(180)  # Сон в 180 секунд
