from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.mongo import MongoStorage


from config import TOKEN
from app.user_state import UserState
from app.modules.message_handlers import state_handler


bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MongoStorage(
    host='mongodb_transportprmbot',
    port=27017,
    db_name='aiogram_fsm'
    ))

# webhook settings
WEBHOOK_HOST = 'https://transportprmbot.deniko1985.ml'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 3001


def register_handlers_message_handler(dp: Dispatcher):
    dp.register_message_handler(
        state_handler.state_message_start,
        commands='start', state='*'
        )
    dp.register_message_handler(
        state_handler.main_state_message_handler,
        state=UserState.MAIN_STATE
        )
    dp.register_message_handler(
        state_handler.main_state_location_message_handler,
        content_types='location',
        state=UserState.MAIN_STATE
        )
    dp.register_message_handler(
        state_handler.help_state_message_handler,
        state=UserState.HELP_STATE
        )
    dp.register_callback_query_handler(
        state_handler.location_state_message_handler,
        state=UserState.LOCATION_STATE
        )
    dp.register_callback_query_handler(
        state_handler.favourites_state_message_handler,
        state=UserState.FAVOURITES_STATE
        )
    dp.register_message_handler(
        state_handler.delete_type_favourites_message_handler,
        state=UserState.DELETE_TYPE_FAVOURITES_STATE
        )
    dp.register_message_handler(
        state_handler.delete_route_favourites_message_handler,
        state=UserState.DELETE_ROUTE_FAVOURITES_STATE
        )
    dp.register_message_handler(
        state_handler.delete_favourites_message_handler,
        state=UserState.DELETE_FAVOURITES_STATE
        )
    dp.register_callback_query_handler(
        state_handler.transport_state_message_handler,
        state=UserState.TRANSPORT_STATE
        )
    dp.register_message_handler(
        state_handler.routes_state_message_handler,
        state=UserState.ROUTES_STATE
        )
    dp.register_message_handler(
        state_handler.direction_state_message_handler,
        state=UserState.DIRECTION_STATE
        )
    dp.register_callback_query_handler(
        state_handler.station_state_message_handler,
        state=UserState.STATION_STATE
        )
    dp.register_callback_query_handler(
        state_handler.timetable_state_message_handler,
        state=UserState.TIMETABLE_STATE
        )
    dp.register_callback_query_handler(
        state_handler.full_timetable_state_message_handler,
        state=UserState.FULL_TIMETABLE_STATE
        )


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start
    register_handlers_message_handler(dp)


async def on_shutdown(dp):
    # logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
#    await dp.storage.close()
#    await dp.storage.wait_closed()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,)
