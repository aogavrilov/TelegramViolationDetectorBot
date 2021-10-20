from aiogram import Bot, Dispatcher, executor, types
import configparser
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Telegram.Connection import bot_connect
from Bot.Infrastructure.DataBase.commands import append_message, get_messages, add_chat, drop_chat

dp = bot_connect()


@dp.message_handler(commands="test1")
async def cmd_test(message: types.Message):
    await message.reply("Test1")


@dp.my_chat_member_handler()
async def some_handler(my_chat_member: types.ChatMemberUpdated):
    if my_chat_member.new_chat_member.user.username == "violation_detect_bot":
        if my_chat_member.new_chat_member.status == "member":
            add_chat(connection, my_chat_member.chat.id, my_chat_member.chat.title, 0)
        if my_chat_member.new_chat_member.status == "administrator":
            drop_chat(connection, my_chat_member.chat.id)
            add_chat(connection, my_chat_member.chat.id, my_chat_member.chat.title, 1)
        if my_chat_member.new_chat_member.status == "left":
            drop_chat(connection, my_chat_member.chat.id)

    # todo check username when he join to chat, check user by spamlist



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
