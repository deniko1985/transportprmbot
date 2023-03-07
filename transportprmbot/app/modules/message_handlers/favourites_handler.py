from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.user_state import UserState
from app.favourites import Favourites
from app.constants import BUS, TRAMWAY, TAXI, GO_BACK


async def go_to_favourites_state(
        message: types.Message,
        state: FSMContext
        ):
    await state.update_data(FAVOURITES_STATE=message.text)
    await message.answer(
        'Избранное:',
        reply_markup=types.ReplyKeyboardRemove()
        )
    list_button_favourites_bus = []
    list_button_favourites_tramway = []
    list_button_favourites_taxi = []
    # user_data = await state.get_data()
    user_favourites = await Favourites.choice_favourites(message.from_user.id)
    inline_kb_favourites_bus = InlineKeyboardMarkup(row_width=5)
    inline_kb_favourites_tramway = InlineKeyboardMarkup(row_width=5)
    inline_kb_favourites_taxi = InlineKeyboardMarkup(row_width=5)
    bus_favourites = user_favourites[0]
    tram_favourites = user_favourites[1]
    taxi_favourites = user_favourites[2]
    if bus_favourites[1] != []:
        for number_favourites in bus_favourites[1]:
            inline_btn_favourites_bus = InlineKeyboardButton(
                f'{number_favourites}',
                callback_data=f'{bus_favourites[0]}, {number_favourites}'
                )
            list_button_favourites_bus.append(inline_btn_favourites_bus)
    if tram_favourites[1] != []:
        for number_favourites in tram_favourites[1]:
            inline_btn_favourites_tramway = InlineKeyboardButton(
                f'{number_favourites}',
                callback_data=f'{tram_favourites[0]}, {number_favourites}'
                )
            list_button_favourites_tramway.append(
                inline_btn_favourites_tramway
                )
    if taxi_favourites[1] != []:
        for number_favourites in taxi_favourites[1]:
            inline_btn_favourites_taxi = InlineKeyboardButton(
                f'{number_favourites}',
                callback_data=f'{taxi_favourites[0]}, {number_favourites}'
                )
            list_button_favourites_taxi.append(inline_btn_favourites_taxi)
    inline_kb_favourites_bus.add(*list_button_favourites_bus)
    inline_kb_favourites_tramway.add(*list_button_favourites_tramway)
    inline_kb_favourites_taxi.add(*list_button_favourites_taxi)
    await UserState.next()
    if bus_favourites[1] == []\
            and tram_favourites[1] == []\
            and taxi_favourites[1] == []:
        await message.answer(text='У вас не добавлено ни одного маршрута!')
    if bus_favourites[1] != []:
        await message.answer(
            text=BUS, reply_markup=inline_kb_favourites_bus
            )
    if tram_favourites[1] != []:
        await message.answer(
            text=TRAMWAY, reply_markup=inline_kb_favourites_tramway
            )
    if taxi_favourites[1] != []:
        await message.answer(
            text=TAXI, reply_markup=inline_kb_favourites_taxi
            )
    inline_kb_favourites = InlineKeyboardMarkup(row_width=1)
    inline_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_kb_favourites.add(inline_back)
    await UserState.FAVOURITES_STATE.set()
    await message.answer(text='Или', reply_markup=inline_kb_favourites)
