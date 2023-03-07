from aiogram import types
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.favourites import Favourites
from app.modules.message_handlers.main_handler import go_to_main_state
from app.modules.message_handlers.help_handler import go_to_help_state
from app.modules.message_handlers.routes_handler import go_to_routes_state
from app.modules.message_handlers.station_handler import go_to_station_state
from app.modules.message_handlers.timetable_handler \
    import go_to_timetable_state, go_to_timetable_choice
from app.modules.message_handlers.favourites_handler \
    import go_to_favourites_state
from app.modules.message_handlers.transport_handler \
    import go_to_transport_state
from app.modules.message_handlers.direction_handler \
    import go_to_direction_state
from app.modules.message_handlers.location_handler \
    import go_to_location_state
from app.constants import GO_BACK, BACK, YES, NO, BUS, TRAMWAY, TAXI, \
    FAVOURITES, HELP, LOCATION


async def state_message_start(message: types.Message, state: FSMContext):
    await go_to_main_state(message, state)


async def main_state_message_handler(
        message: types.Message,
        state: FSMContext
        ):
    await Favourites.check_user(message.from_user.id, message.chat.id)
    if message.text == HELP:
        await go_to_help_state(message, state)
    if message.text == FAVOURITES:
        await go_to_favourites_state(message, state)
    if message.text in [BUS, TRAMWAY, TAXI]:
        await go_to_transport_state(message, state)
    if message.text == LOCATION:
        await main_state_location_message_handler(message, state)


async def help_state_message_handler(
        message: types.Message,
        state: FSMContext
        ):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    else:
        await message.answer('Попробуй еще раз.')
        return


async def favourites_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    else:
        await go_to_routes_state(call, state)


async def main_state_location_message_handler(
        message: types.Message,
        state: FSMContext
        ):
    if message.location:
        await go_to_location_state(message, state)


async def location_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    else:
        user_data = call.data.split(', ')
        if len(user_data) == 4:
            transport_type = user_data[0]
            stop_name = user_data[1]
            stop_id = user_data[2]
            route_number = user_data[3]
        else:
            g_data = await Data.get_calldata(user_data)
            transport_type = user_data[-1]
            stop_name = g_data
            stop_id = user_data[0]
            route_number = user_data[1]
        get_direction_location = await Data.get_direction_for_location(
            transport_type, stop_id, route_number
            )
        await state.update_data(
            TRANSPORT_STATE=transport_type,
            ROUTES_STATE=route_number,
            DIRECTION_STATE=get_direction_location,
            STATION_STATE=stop_name
            )
        await go_to_timetable_state(call, state)


async def transport_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    else:
        await go_to_routes_state(call, state)


async def routes_state_message_handler(
        message: types.Message, state: FSMContext
        ):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    elif message.text == BACK:
        user_data = await state.get_data()
        if user_data.get('FAVOURITES_STATE'):
            message.text = user_data['FAVOURITES_STATE']
            await go_to_favourites_state(message, state)
        else:
            message.text = user_data['TRANSPORT_STATE']
            await go_to_transport_state(message, state)
    else:
        await go_to_direction_state(message, state)


async def direction_state_message_handler(
        message: types.Message, state: FSMContext
        ):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    elif message.text == BACK:
        await go_to_routes_state(message, state)
    else:
        await state.update_data(DIRECTION_STATE=message.text)
        await go_to_station_state(message, state)


async def station_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    elif call.data == BACK:
        await go_to_direction_state(call.message, state)
    else:
        await state.update_data(STATION_STATE=call.data)
        await go_to_timetable_choice(call, state)


async def choise_timetable_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    await state.update_data(CHOICE_TIMETABLE_STATE=call.data)
    await go_to_timetable_state(call, state)


async def timetable_state_message_handler(
        call: types.CallbackQuery, state: FSMContext
        ):
    await state.update_data(TIMETABLE_STATE=call.data)
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    elif call.data == NO:
        await go_to_main_state(call.message, state)
    elif call.data == YES:
        user_data = await state.get_data()
        add_user = await Favourites.add_favourites(
            call.from_user.id, user_data
            )
        await call.message.answer(text=f'{add_user}')
        await go_to_main_state(call.message, state)
