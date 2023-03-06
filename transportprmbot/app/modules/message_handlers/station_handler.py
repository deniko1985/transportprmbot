from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.constants import GO_BACK, BACK


async def go_to_station_state(message: types.Message, state: FSMContext):
    await message.answer(
        'Выбери остановку', reply_markup=types.ReplyKeyboardRemove()
        )
    list_button = []
    user_data = await state.get_data()
    station_list = await Data.choice_station(user_data)
    for title_station in station_list:
        inline_button = InlineKeyboardButton(
            f'{title_station}',
            callback_data=f'{title_station[:32]}'
            )
        list_button.append(inline_button)
    inline_station_list = InlineKeyboardMarkup(row_width=3)
    inline_go_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_back = InlineKeyboardButton(BACK, callback_data=BACK)
    inline_station_list.add(*list_button)
    inline_station_list.add(inline_back, inline_go_back)
    await UserState.STATION_STATE.set()
    await message.answer(
        text=f"{user_data['TRANSPORT_STATE']} № {user_data['ROUTES_STATE']}",
        reply_markup=inline_station_list
        )
