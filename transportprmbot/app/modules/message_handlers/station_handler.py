from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db import db
from app.user_state import UserState
from app.constants import GO_BACK, BACK


async def go_to_station_state(message: types.Message, state: FSMContext):
    await message.answer(
        'Выбери остановку', reply_markup=types.ReplyKeyboardRemove()
        )
    buttons = []
    user_data = await state.get_data()
    stations = await db.get_station_name(user_data)
    for title_station in stations:
        inline_button = InlineKeyboardButton(
            f'{title_station}',
            callback_data=f'{title_station[:32]}'
            )
        buttons.append(inline_button)
    inline_kb = InlineKeyboardMarkup(row_width=3)
    inline_go_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_back = InlineKeyboardButton(BACK, callback_data=BACK)
    inline_kb.add(*buttons)
    inline_kb.add(inline_back, inline_go_back)
    await UserState.STATION_STATE.set()
    await message.answer(
        text=f"{user_data['TRANSPORT_STATE']} № {user_data['ROUTES_STATE']}",
        reply_markup=inline_kb
        )
