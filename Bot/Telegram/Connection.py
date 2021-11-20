import logging

from aiogram import Bot, Dispatcher, executor, types
import configparser


def bot_connect() -> Dispatcher:
    config = configparser.ConfigParser()
    config.read("settings.ini")
    bot = Bot(token=config["TelegramBot"]["token"])
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher(bot)
    return dp
