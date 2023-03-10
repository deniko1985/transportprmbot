from aiogram import types
from aiogram.dispatcher import FSMContext as FSM

from app.modules.db import db
from app import favourites
from app.modules.message_handlers.main_handler import go_to_main_state
from app.modules.message_handlers.help_handler import go_to_help_state
from app.modules.message_handlers.routes_handler import go_to_routes_state
from app.modules.message_handlers.station_handler import go_to_station_state
from app.modules.message_handlers.timetable_handler import go_to_timetable_state, go_to_timetable
from app.modules.message_handlers import favourites_handler
from app.modules.message_handlers.transport_handler import go_to_transport_state
from app.modules.message_handlers.direction_handler import go_to_direction_state
from app.modules.message_handlers.location_handler import go_to_location_state
from app.constants import GO_BACK, BACK, YES, BUS, TRAMWAY, TAXI, \
    FAVOURITES, HELP, LOCATION, DELETE, HOME


async def state_message_start(message: types.Message, state: FSM):
    await go_to_main_state(message, state)


async def main_state_message_handler(message: types.Message, state: FSM):
    await favourites.add_user(message.from_user.id, message.chat.id)
    if message.text == HELP:
        await go_to_help_state(message, state)
    if message.text == FAVOURITES:
        await favourites_handler.go_to_favourites_state(message, state)
    if message.text in [BUS, TRAMWAY, TAXI]:
        await go_to_transport_state(message, state)
    if message.text == LOCATION:
        await main_state_location_message_handler(message, state)


async def help_state_message_handler(message: types.Message, state: FSM):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    else:
        await message.answer('Попробуй еще раз.')
        return


async def favourites_state_message_handler(call: types.CallbackQuery, state: FSM):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    elif call.data == DELETE:
        await favourites_handler.go_to_delete_type_favourites(call.message, state)
    else:
        await go_to_routes_state(call, state)


async def delete_type_favourites_message_handler(message: types.Message, state: FSM):
    await state.update_data(DELETE_TYPE_FAVOURITES_STATE=message.text)
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    else:
        await favourites_handler.go_to_delete_route_favourites(message, state)


async def delete_route_favourites_message_handler(message: types.Message, state: FSM):
    await state.update_data(DELETE_ROUTE_FAVOURITES_STATE=message.text)
    user_data = await state.get_data()
    res = await favourites.delete_favorites_routes(
            message.from_user.id,
            user_data
        )
    message.text = res
    await favourites_handler.go_to_delete_favourites(message, state)


async def delete_favourites_message_handler(message: types.Message, state: FSM):
    await state.update_data(DELETE_FAVOURITES_STATE=message.text)
    if message.text == YES:
        await favourites_handler.go_to_delete_type_favourites(message, state)
    else:
        await go_to_main_state(message, state)


async def main_state_location_message_handler(message: types.Message, state: FSM):
    if message.location:
        await go_to_location_state(message, state)


async def location_state_message_handler(call: types.CallbackQuery, state: FSM):
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
            g_data = await db.get_calldata(user_data)
            transport_type = user_data[-1]
            stop_name = g_data
            stop_id = user_data[0]
            route_number = user_data[1]
        get_direction_location = await db.get_direction_for_location(
                transport_type,
                stop_id,
                route_number
            )
        await state.update_data(
                TRANSPORT_STATE=transport_type,
                ROUTES_STATE=route_number,
                DIRECTION_STATE=get_direction_location,
                STATION_STATE=stop_name
            )
        await go_to_timetable_state(call, state)


async def transport_state_message_handler(call: types.CallbackQuery, state: FSM):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    else:
        await go_to_routes_state(call, state)


async def routes_state_message_handler(message: types.Message, state: FSM):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    elif message.text == BACK:
        user_data = await state.get_data()
        if user_data.get('FAVOURITES_STATE'):
            message.text = user_data['FAVOURITES_STATE']
            await favourites_handler.go_to_favourites_state(message, state)
        else:
            message.text = user_data['TRANSPORT_STATE']
            await go_to_transport_state(message, state)
    else:
        await go_to_direction_state(message, state)


async def direction_state_message_handler(message: types.Message, state: FSM):
    if message.text == GO_BACK:
        await go_to_main_state(message, state)
    else:
        await state.update_data(DIRECTION_STATE=message.text)
        await go_to_station_state(message, state)


async def station_state_message_handler(call: types.CallbackQuery, state: FSM):
    if call.data == GO_BACK:
        await go_to_main_state(call.message, state)
    elif call.data == BACK:
        await go_to_direction_state(call.message, state)
    else:
        await state.update_data(STATION_STATE=call.data)
        await go_to_timetable(call, state)


async def timetable_state_message_handler(call: types.CallbackQuery, state: FSM):
    await state.update_data(FULL_TIMETABLE_STATE=call.data)
    await go_to_timetable_state(call, state)


async def full_timetable_state_message_handler(call: types.CallbackQuery, state: FSM):
    if call.data == YES:
        user_data = await state.get_data()
        add_route = await favourites.add_routes(
                call.from_user.id,
                user_data['TRANSPORT_STATE'],
                user_data['ROUTES_STATE']
            )
        await call.message.answer(text=f'{add_route}')
        await go_to_main_state(call.message, state)
    elif call.data == HOME:
        await go_to_main_state(call.message, state)
    else:
        await go_to_main_state(call.message, state)
