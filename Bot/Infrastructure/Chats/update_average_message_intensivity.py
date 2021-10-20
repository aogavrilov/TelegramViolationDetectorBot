import sys
sys.path.insert(0, '/path/to/application/app/folder')
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Infrastructure.DataBase.commands import get_count_of_messages_on_interval, get_chats
from Bot.Telegram.Connection import bot_connect
import time


dp2 = bot_connect()

while True:
    database_connection = database_connect()
    print(get_chats(database_connection))
    database_connection.close()
    #print(get_count_of_messages_on_interval(database_connection, -685239380, [0, 10000]))
    time.sleep(180)  # Сон в 180 секунд
