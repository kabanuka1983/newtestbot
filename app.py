from aiogram import executor

from data.config import BOT_TOKEN
from utils.database import create_db
from aiogram.types import BotCommand, BotCommandScopeDefault

WEBHOOK_HOST = 'https://different-nanni-oaser7bf.koyeb.app'
WEBHOOK_URL = f'{WEBHOOK_HOST}/{BOT_TOKEN}'

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8000


async def set_default_commands(dp):
    return await dp.bot.set_my_commands(
        commands=[
            BotCommand('info', 'посмотреть баланс'),
            BotCommand('menu', 'Меню')
        ],
        scope=BotCommandScopeDefault()
    )


async def on_startup(dp):
    await dp.bot.set_webhook(WEBHOOK_URL)
    await create_db()
    await set_default_commands(dp)
    # message = create_file()
    # await bot.send_message(chat_id=ADMIN_ID, text=message)


async def shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.delete_webhook()


if __name__ == '__main__':
    from handlers import dp

    executor.start_webhook(
        dispatcher=dp,
        webhook_path=f'/{BOT_TOKEN}',
        on_startup=on_startup,
        on_shutdown=shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )

