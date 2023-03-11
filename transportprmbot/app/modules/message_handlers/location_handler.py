from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext as FSM

from app.modules.db import db
from app.user_state import UserState
from app.constants import BUS, TRAMWAY, TAXI, GO_BACK, \
    LOCATION, LOCATION_STATION


async def go_to_location_state(message: types.Message, state: FSM):
    message.text = LOCATION
    await state.update_data(LOCATION_STATE=message.text)
    locations = await db.get_station_by_location(message.location)
    if locations == []:
        await message.answer(
                text='На расстоянии 500 м. остановок нет',
                reply_markup=types.ReplyKeyboardRemove()
            )
    else:
        longitude = str(locations['location']['coordinates'][0])
        latitude = str(locations['location']['coordinates'][1])
        stop_name = locations['name']
        route_id = locations['route_id']
        stop_id = locations['stop_id']
        await message.answer(
                f'Остановка рядом: {stop_name}',
                reply_markup=types.ReplyKeyboardRemove()
            )
        route_numbers = await db.get_number_route(route_id)
        bus_buttons = []
        tramway_buttons = []
        taxi_buttons = []
        inline_kb_bus = InlineKeyboardMarkup(row_width=5)
        inline_kb_tramway = InlineKeyboardMarkup(row_width=5)
        inline_kb_taxi = InlineKeyboardMarkup(row_width=5)
        if route_numbers['Bus'] == []\
                and route_numbers['Tramway'] == []\
                and route_numbers['Taxi'] == []:
            await message.answer(text='Не нашлось ниодного маршрута!')
        if route_numbers['Bus'] != []:
            for number in route_numbers['Bus']:
                inline_btn_bus = InlineKeyboardButton(
                        f'{number}',
                        callback_data=f'{stop_id}, {number}, {BUS}'
                    )
                bus_buttons.append(inline_btn_bus)
            inline_kb_bus.add(*bus_buttons)
            await message.answer(text=BUS, reply_markup=inline_kb_bus)
        if route_numbers['Tramway'] != []:
            for number in route_numbers['Tramway']:
                inline_btn_tramway = InlineKeyboardButton(
                        f'{number}',
                        callback_data=f'{stop_id}, {number}, {TRAMWAY}'
                    )
                tramway_buttons.append(inline_btn_tramway)
            inline_kb_tramway.add(*tramway_buttons)
            await message.answer(text=TRAMWAY, reply_markup=inline_kb_tramway)
        if route_numbers['Taxi'] != []:
            for number_favourites in route_numbers['Taxi']:
                inline_btn_taxi = InlineKeyboardButton(
                        f'{number_favourites}',
                        callback_data=f'{stop_id}, {number}, {TAXI}'
                    )
                taxi_buttons.append(inline_btn_taxi)
            inline_kb_taxi.add(*taxi_buttons)
            await message.answer(text=TAXI, reply_markup=inline_kb_taxi)
        app_maps = types.WebAppInfo(
                url=f'https://maps.deniko1985.ml/geo_station/{latitude,longitude}'
            )
        button_maps = types.KeyboardButton(LOCATION_STATION, web_app=app_maps)
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
        inline_kb.add(inline_back)
        inline_kb.add(button_maps, inline_back)
        await UserState.LOCATION_STATE.set()
        await message.answer(text='Или', reply_markup=inline_kb)
