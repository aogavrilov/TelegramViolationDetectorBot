import os

import numpy as np
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from Bot.Infrastructure.Chats.ChatRules import ChatRules
from Bot.Infrastructure.DataBase.Connector import database_connect
from Bot.Telegram.Connection import bot_connect
from Bot.Infrastructure.DataBase.commands import append_message, get_messages, add_chat, drop_chat, get_flood_status, \
    update_flood_status, get_chat_rules, get_count_of_chat_rules, update_chat_rules, create_chat_rules
from Bot.Detector.Flood.FloodDetector import FloodDetector
from Bot.Detector.NSFW.detection import check_message_to_nsfw
from Bot.Detector.Corrector import Corrector
from Bot.Detector.NSFW.model.bert.bert_classifier import BertClassifier
import torch

obscenity_model = BertClassifier(
        model_path='cointegrated/rubert-tiny',
        tokenizer_path='cointegrated/rubert-tiny',
        n_classes=2,
        model_save_path='obscenity_bert.pt',
)
obscenity_model.model = torch.load('Bot/Detector/NSFW/model/bert/obscenity_bert.pt', map_location=torch.device('cpu'))
threat_model = BertClassifier(
        model_path='cointegrated/rubert-tiny',
        tokenizer_path='cointegrated/rubert-tiny',
        n_classes=2,
        model_save_path='obscenity_bert.pt',
)
threat_model.model = torch.load('Bot/Detector/NSFW/model/bert/threat_bert.pt', map_location=torch.device('cpu'))
insult_model = BertClassifier(
        model_path='cointegrated/rubert-tiny',
        tokenizer_path='cointegrated/rubert-tiny',
        n_classes=2,
        model_save_path='obscenity_bert.pt',
)
insult_model.model = torch.load('Bot/Detector/NSFW/model/bert/insult_bert.pt', map_location=torch.device('cpu'))






import logging
try:
    os.mkdir("logs")
except Exception as e:
    print(e)
logging.basicConfig(filename="logs/main.logs", level=logging.INFO)
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

"""

"""


@dp.message_handler(content_types=types.ContentTypes.all())
async def message_read(message: types.Message):
    message_text = message.text

    if message.sticker is not None:
        message_text = '' + str(message.sticker.file_unique_id)
    if message.dice is not None:
        message_text = '' + str(message.dice.emoji)
    if (message_text == 'NULL') or (message_text is None):
        message_text = str('БезТекста')
    try:
        append_message(connection, message.chat.id, message.from_user.id, message_text, message.message_id, 0,
                       message.date.year + message.date.month * 12 + message.date.day * 31 + message.date.hour * 24 +
                       message.date.minute, message.chat.title, str(message.from_user.first_name) + ' ' +
                       str(message.from_user.last_name))
    except Exception as e:
        try:
            log.exception(e)
        except Exception as e:
            print(e)



    try:
        chat_rules = get_chat_rules(connection, obscenity_model, insult_model, threat_model, chat_id=message.chat.id)
        if chat_rules is None:
            chat_rules = ChatRules(obscenity_model, insult_model, threat_model, "0,0,0", "0,0,0", "0,0,0", "0,0,0")

    except Exception as e:
        try:
            log.exception(e)
        except Exception as e:
            print(e)
        chat_rules = ChatRules(obscenity_model, insult_model, threat_model, "0,0,0", "0,0,0", "0,0,0", "0,0,0")

    # Установка параметров бота
    if "@violation_detect_bot" in message_text.lower() and "просмотр настроек бота для чата" in message_text.lower():
        member = await dp.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status == "creator":
            await message.answer(chat_rules.show_settings())
    if "@violation_detect_bot" in message_text.lower() and "установить настройки для чата" in message_text.lower():
        member = await dp.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status == "creator":
            result_code = chat_rules.from_text(message_text)
            if result_code == 0:
                await message.answer("Отправьте пожалуйста настройки в формате, который будет отправлен сообщением ниже:")

            if get_count_of_chat_rules(connection, message.chat.id) == 1:
                update_chat_rules(connection, message.chat.id, chat_rules.get_str_dict())
            elif get_count_of_chat_rules(connection, message.chat.id) == 0:
                create_chat_rules(connection, message.chat.id, chat_rules.get_str_dict())
            await message.answer(chat_rules.show_settings())





    # Check on flood when reply message
    try:
        if message.reply_to_message is not None and message_text.lower() == "@violation_detect_bot":
            messages_texts, messages_ids = get_messages(connection, message.reply_to_message.from_user.id,
                                                        message.reply_to_message.chat.id, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_messages_to_flood_detect(
                messages_texts)  # todo check images for flood
            if is_messages_has_flood:
                corrector = Corrector(connection, dp.bot, message.chat.id)
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   mute_user=True,
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
    except Exception as e:
        try:
            log.exception(e)
        except Exception as e:
            print(e)


    # Check on NSFW
    try:
        if get_flood_status(connection, message.chat.id):
            messages_texts, messages_ids = get_messages(connection,
                                                        message.from_user.id,
                                                        message.chat.id,
                                                        20,
                                                        is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(
                messages_texts,
                message_text,
                similarity_coefficient=0.25)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                corrector = Corrector(connection, dp.bot, message.chat.id)
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   mute_user=True,
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
            else:
                reaction = chat_rules.check_violation(message_text)
                if reaction.sum() > 0:
                    corrector = Corrector(connection, dp.bot, message.chat.id)
                    await corrector.react_to_violation(user_id=message.from_user.id,
                                                       messages=[message.message_id],
                                                       mute_user=reaction[1],
                                                       delete_messages=reaction[0],
                                                       kick_user=reaction[2])
        else:
            messages_texts, messages_ids = get_messages(connection, message.from_user.id,
                                                        message.chat.id, 30, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(
                messages_texts,
                message_text,
                similarity_coefficient=0.75)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                corrector = Corrector(connection, dp.bot, message.chat.id)
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   delete_messages=True,
                                                   restrict_reason='Flood message')
                update_flood_status(connection, message.chat.id, 1)
            else:
                reaction = chat_rules.check_violation(message_text)
                if reaction.sum() > 0:
                    corrector = Corrector(connection, dp.bot, message.chat.id)
                    await corrector.react_to_violation(user_id=message.from_user.id,
                                                       messages=[message.message_id],
                                                       mute_user=reaction[1],
                                                       delete_messages=reaction[0],
                                                       kick_user=reaction[2])
    except Exception as e:
        try:
            log.exception(e)
        except Exception as e:
            print(e)




dp.register_message_handler(message_read, content_types=types.ContentTypes.all())

if __name__ == '__main__':
    try:
        connection = database_connect()
        if connection is None:
            log.error('Database didn''t connect')
            print('Database didn\'t connect, connection is None')
        else:
            log.info('Database connected')
            print('Database connected', connection)
    except Exception as e:
        log.error('Database didn''t connect')
        print('Database didn\'t connect', e)
    executor.start_polling(dp, skip_updates=True)
