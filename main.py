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

dp = bot_connect()
detector = FloodDetector()


class SetPunishmentSettings(StatesGroup):
    waiting_for_writing_chat_id = State()
    waiting_for_add_triggers = State()
    waiting_for_set_punishments = State()


@dp.message_handler(commands="start")
async def start_dialog(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton("About"))
    poll_keyboard.add(types.KeyboardButton("Punishment settings"))
    poll_keyboard.add(types.KeyboardButton("Incidents logs"))
    poll_keyboard.add(types.KeyboardButton("Cancel"))
    await message.answer("Select action", reply_markup=poll_keyboard)


@dp.message_handler()
async def echo(message: types.Message):
    if message.text == "About":
        await message.answer("This bot can help you moderate your channel with Russian messages.\n "
                             "You need to make bot administrator for detecting NSFW and react on it.\n"
                             "If you make him administrator than you also need set punishment settings\n"
                             "You can view all applied actions in Incidents logs\n"
                             "If you don't make him administrator he will collect incidents to logs and "
                             "it can helps him to become better."
                             "\n\nДанный бот упрощает модерирование канала.\n"
                             "На текущий момент поддерживаются такие функции, как детектирование оскорблений/угроз/мата"
                             " в сообщении, фильтрация фото на предмет непристойности, детекция флуда.\n"
                             "- Для того, чтобы бот мог модерировать канал, необходимо сделать его администратором и "
                             "выставить настройки реакций на каждый из видов нарушений\n"
                             "- Все инциденты и примененные наказания записываются и могут быть показаны по кнопке "
                             "''Incidents logs''\n"
                             "- Если вы оставите бота без прав администрирования, то бот не будет модерировать канал, "
                             "но это поможет боту улучшать качество классификации"


                             )
    elif message.text == "Punishment settings":
        await message.answer("На текущий момент поддерживаются функции детекции:\n 1. Оскорблений\n 2. Угроз\n "
                             "3. Непристойностей\n 4. Флуда сообщениями")
        await message.answer("Введите список необходимых функций детекции в формате ''<Номер функции>. <True/False> "
                             "<Переход на новую строку>'', где True означает необходимость включения данного "
                             "классификатора, а False обозначает "
                             "отсутствие необходимости.\n Пример приведен ниже:")
        await message.answer("1. True\n2. True\n3. False\n4. True")
        await message.answer("В приведенном выше примере включена поддержка детекции оскорблений, угроз и флуда, "
                             "но выключена модерация непристойностей")

    elif (message.text == "Style Transfer"):
        pass

    elif (message.text == "Отмена"):
        tmp = types.ReplyKeyboardRemove()
        await message.answer(
            "Спасибо, что воспользовались нашим приложением. Вы всегда можете ввести /start и продолжить развлекаться.",
            reply_markup=tmp)

    else:
        await message.answer("Данная команда неизвестна. Введите /start для отображения меню.")
        print(message.text)






























































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
        corrector = Corrector(connection, dp.bot, message.chat.id)
        if message.reply_to_message is not None and message.text.lower() == "@violation_detect_bot":
            messages_texts, messages_ids = get_messages(connection, message.reply_to_message.from_user.id,
                                                        message.reply_to_message.chat.id, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_messages_to_flood_detect(
                messages_texts)  # todo check images for flood
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   delete_messages=True, restrict_reason='Flood message')
    except Exception as e:
        print(e)
    try:
        if get_flood_status(connection, message.chat.id):
            messages_texts, messages_ids = get_messages(connection, message.from_user.id, message.chat.id, 20, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(messages_texts,
                                                                                                      message.text,
                                                                                                      similarity_coefficient=0.25)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   delete_messages=True, restrict_reason='Flood message')
        else:
            messages_texts, messages_ids = get_messages(connection, message.from_user.id,
                                         message.chat.id, 30, is_deleted=0)
            is_messages_has_flood, messages_with_flood_ids = detector.compare_message_to_flood_detect(messages_texts,
                                                                                                      message.text,
                                                                                                      similarity_coefficient=0.75)
            messages_ids.insert(0, message.message_id)
            if is_messages_has_flood:
                await corrector.react_to_violation(messages=np.array(messages_ids)[messages_with_flood_ids],
                                                   delete_messages=True, restrict_reason='Flood message')
            update_flood_status(connection, message.chat.id, 1)
    except Exception as e:
        print(e)
    if check_message_to_nsfw(message.text):
        await message.reply('NSFW!')
    try:
        append_message(connection, message.chat.id, message.from_user.id, message.text, message.message_id, 0,
                       message.date.year + message.date.month * 12 + message.date.day * 31 + message.date.hour * 24 +
                       message.date.minute)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        connection = database_connect()
        print('Database connected')
    except:
        print('Database didn''t connect')
    executor.start_polling(dp, skip_updates=True)
