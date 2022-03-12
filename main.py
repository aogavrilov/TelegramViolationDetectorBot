import os

import numpy as np
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Telegram.Connection import bot_connect
from Bot.Infrastructure.DataBase.commands import append_message, get_messages, add_chat, drop_chat, get_flood_status, \
    update_flood_status
from Bot.Detector.Flood.FloodDetector import FloodDetector
from Bot.Detector.NSFW.detection import check_message_to_nsfw
from Bot.Detector.Corrector import Corrector
import logging
try:
    os.mkdir("logs")
except Exception as e:
    print(e)
logging.basicConfig(filename="logs/main.log", level=logging.INFO)
log = logging.getLogger("ex")

dp = bot_connect()
detector = FloodDetector()


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
        append_message(connection, message.chat.id, message.from_user.id, message.text, message.message_id, 0,
                       message.date.year + message.date.month * 12 + message.date.day * 31 + message.date.hour * 24 +
                       message.date.minute)
        corrector = Corrector(connection, dp.bot, message.chat.id)
    except Exception as e:
        log.exception(e)
    try:

        if message.reply_to_message is not None and message.text.lower() == "@violation_detect_bot":
            messages_texts, messages_ids = get_messages(connection, message.reply_to_message.from_user.id,
                                                        message.reply_to_message.chat.id, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_messages_to_flood_detect(
                messages_texts)  # todo check images for flood
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   mute_user=True,
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
    except Exception as e:
        log.exception(e)
    try:
        if get_flood_status(connection, message.chat.id):
            messages_texts, messages_ids = get_messages(connection,
                                                        message.from_user.id,
                                                        message.chat.id,
                                                        20,
                                                        is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(
                messages_texts,
                message.text,
                similarity_coefficient=0.25)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   mute_user=True,
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
        else:
            messages_texts, messages_ids = get_messages(connection, message.from_user.id,
                                                        message.chat.id, 30, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(
                messages_texts,
                message.text,
                similarity_coefficient=0.75)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
                update_flood_status(connection, message.chat.id, 1)
    except Exception as e:
        log.exception(e)
    if check_message_to_nsfw(message.text):
        await corrector.react_to_violation(user_id=message.from_user.id,
                                           messages=[message.message_id],
                                           mute_user=True,
                                           delete_messages=True)
        #await message.reply('NSFW!')



if __name__ == '__main__':
    try:

        connection = database_connect()
        log.info('Database connected')
    except:
        log.error('Database didn''t connect')
    executor.start_polling(dp, skip_updates=True)
