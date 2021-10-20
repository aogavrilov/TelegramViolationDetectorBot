from aiogram import Bot, Dispatcher, executor, types
import configparser
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Telegram.Connection import bot_connect
from Bot.Infrastructure.DataBase.commands import append_message, get_messages

dp = bot_connect()


@dp.message_handler(commands="test1")
async def cmd_test(message: types.Message):
    await message.reply("Test1")


@dp.message_handler()
async def message_read(message: types.Message):
    print(message.date.year * 12 + message.date.month * 31 + message.date.day * 24 + message.date.minute)
    try:
        if message.reply_to_message is not None and message.reply_to_message.text.lower() == "@violation_detect_bot":
            messages = get_messages(connection, message.reply_to_message.from_user.id, message.reply_to_message.chat.id)
            print(message.reply_to_message.text.lower(), messages)
    except():
        pass

    append_message(connection, message.chat.id, message.from_user.id, message.text, 0,
                   message.date.year * 12 + message.date.month * 31 + message.date.day * 24 + message.date.minute)


if __name__ == '__main__':
    connection = database_connect()
    executor.start_polling(dp, skip_updates=True)
