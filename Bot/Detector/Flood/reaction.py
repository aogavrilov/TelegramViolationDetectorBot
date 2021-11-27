from Bot.Infrastructure.DataBase.commands import update_message_is_flood_status


async def react_to_flood_message(connection, bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
        update_message_is_flood_status(connection, chat_id, message_id, 1)
    except Exception as e:
        print(e)
