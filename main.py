from aiogram import Bot, Dispatcher, executor, types
import configparser
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Telegram.Connection import bot_connect
from Bot.Infrastructure.DataBase.commands import append_message, get_messages, add_chat, drop_chat, get_flood_status, \
    update_flood_status
from Bot.Detector.Flood.detection import compare_messages_to_flood_detect, compare_message_to_flood_detect
from Bot.Detector.Flood.reaction import react_to_flood_message
from Bot.Detector.NSFW.detection import check_message_to_nsfw

dp = bot_connect()


@dp.message_handler(commands="test1")
async def cmd_test(message: types.Message):
    await message.reply("Test1")


@dp.my_chat_member_handler()
async def some_handler(my_chat_member: types.ChatMemberUpdated):
    if my_chat_member.new_chat_member.user.username == "violation_detect_bot":
        drop_chat(connection, my_chat_member.chat.id)
        if my_chat_member.new_chat_member.status == "member":
            add_chat(connection, my_chat_member.chat.id, my_chat_member.chat.title, 0)
        if my_chat_member.new_chat_member.status == "administrator":
            add_chat(connection, my_chat_member.chat.id, my_chat_member.chat.title, 1)
        if my_chat_member.new_chat_member.status == "left":
            pass
        else:
            add_chat(connection, my_chat_member.chat.id, my_chat_member.chat.title, 0)

    # todo check username when he join to chat, check user by spamlist


@dp.message_handler()
async def message_read(message: types.Message):
    try:
        if message.reply_to_message is not None and message.text.lower() == "@violation_detect_bot":
            messages, ids = get_messages(connection, message.reply_to_message.from_user.id,
                                         message.reply_to_message.chat.id, is_deleted=0)  # todo check for flood
            status, ids1 = compare_messages_to_flood_detect(dp, message.reply_to_message.chat.id, messages,
                                                            ids)  # todo check images for flood
            if status:
                for id1 in ids1:
                    await react_to_flood_message(connection, dp.bot, message.chat.id, ids[id1])


    except():
        pass
    try:
        if get_flood_status(connection, message.chat.id):
            messages, ids = get_messages(connection, message.from_user.id, message.chat.id, 20)
            status, ids1 = compare_message_to_flood_detect(dp, messages, message.text, percent=0.25)
            if status:
                for id1 in ids1:
                    await react_to_flood_message(connection, dp.bot, message.chat.id, ids[id1])
                await react_to_flood_message(connection, dp.bot, message.chat.id, message.message_id)
        else:
            messages, ids = get_messages(connection, message.from_user.id,
                                         message.chat.id, 30)
            status, ids1 = compare_message_to_flood_detect(dp, messages, message.text, percent=0.75)
            if status:
                for id1 in ids1:
                    await react_to_flood_message(connection, dp.bot, message.chat.id, ids[id1])
                await react_to_flood_message(connection, dp.bot, message.chat.id, message.message_id)
            update_flood_status(connection, message.chat.id, 1)
    except:
        pass
    if check_message_to_nsfw(message.text):
        await message.reply('NSFW!')
    try:
        append_message(connection, message.chat.id, message.from_user.id, message.text, message.message_id, 0,
                       message.date.year + message.date.month * 12 + message.date.day * 31 + message.date.hour * 24 +
                       message.date.minute)
    except:
        pass


if __name__ == '__main__':
    try:
        connection = database_connect()
    except:
        pass
    executor.start_polling(dp, skip_updates=True)
