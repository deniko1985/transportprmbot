from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.constants import BUS, TRAMWAY, TAXI, GO_BACK, \
    LOCATION, LOCATION_STATION


async def go_to_location_state(
        message: types.Message,
        state: FSMContext
        ):
    message.text = LOCATION
    await state.update_data(LOCATION_STATE=message.text)
    location = await Data.get_station_by_location(message.location)
    if location == []:
        await message.answer(
            text='На расстоянии 500 м. остановок нет',
            reply_markup=types.ReplyKeyboardRemove()
            )
    else:
        longitude = str(location['location']['coordinates'][0])
        latitude = str(location['location']['coordinates'][1])
        stop_name = location['name']
        route_id = location['route_id']
        stop_id = location['stop_id']
        # id_db = location['_id']
        get_route_number = await Data.get_number_route(route_id)
        list_button_bus = []
        list_button_tramway = []
        list_button_taxi = []
        inline_kb_bus = InlineKeyboardMarkup(row_width=5)
        inline_kb_tramway = InlineKeyboardMarkup(row_width=5)
        inline_kb_taxi = InlineKeyboardMarkup(row_width=5)
        if get_route_number['Bus'] != []:
            for number in get_route_number['Bus']:
                inline_btn_bus = InlineKeyboardButton(
                    f'{number}',
                    callback_data=f'{stop_id}, {number}, {BUS}'
                    )
                list_button_bus.append(inline_btn_bus)
        if get_route_number['Tramway'] != []:
            for number in get_route_number['Tramway']:
                inline_btn_tramway = InlineKeyboardButton(
                    f'{number}',
                    callback_data=f'{stop_id}, {number}, {TRAMWAY}')
                list_button_tramway.append(inline_btn_tramway)
        if get_route_number['Taxi'] != []:
            for number_favourites in get_route_number['Taxi']:
                inline_btn_taxi = InlineKeyboardButton(
                    f'{number_favourites}',
                    callback_data=f'{stop_id}, {number}, {TAXI}'
                    )
                list_button_taxi.append(inline_btn_taxi)
        app_maps = types.WebAppInfo(
            url=f'https://app.deniko1985.ml/geo_station/{latitude,longitude}'
            )
        button_maps = types.KeyboardButton(LOCATION_STATION, web_app=app_maps)
        inline_kb_bus.add(*list_button_bus)
        inline_kb_tramway.add(*list_button_tramway)
        inline_kb_taxi.add(*list_button_taxi)
        await message.answer(
            f'Остановка рядом: {stop_name}',
            reply_markup=types.ReplyKeyboardRemove()
            )
        if get_route_number['Bus'] == []\
                and get_route_number['Tramway'] == []\
                and get_route_number['Taxi'] == []:
            await message.answer(text='Не нашлось ниодного маршрута!')
        if get_route_number['Bus'] != []:
            await message.answer(text=BUS, reply_markup=inline_kb_bus)
        if get_route_number['Tramway'] != []:
            await message.answer(text=TRAMWAY, reply_markup=inline_kb_tramway)
        if get_route_number['Taxi'] != []:
            await message.answer(text=TAXI, reply_markup=inline_kb_taxi)
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
        inline_kb.add(inline_back)
        inline_kb.add(button_maps, inline_back)
        await UserState.LOCATION_STATE.set()
        await message.answer(text='Или', reply_markup=inline_kb)
