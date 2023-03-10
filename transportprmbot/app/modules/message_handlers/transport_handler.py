from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext as FSM

from app.modules.db import db
from app.user_state import UserState
from app.constants import GO_BACK


async def go_to_transport_state(message: types.Message, state: FSM):
    await state.update_data(TRANSPORT_STATE=message.text)
    await message.answer('Выбери номер маршрута.', reply_markup=types.ReplyKeyboardRemove())
    buttons = []
    route_numbers = await db.get_route_numbers(message.text)
    choice_transport = message.text
    for number_route in route_numbers:
        inline_btn = InlineKeyboardButton(
                number_route,
                callback_data=f'{choice_transport}, {number_route}'
            )
        buttons.append(inline_btn)
    inline_go_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_kb = InlineKeyboardMarkup(row_width=8)
    inline_kb.add(*buttons)
    inline_kb.add(inline_go_back)
    await UserState.TRANSPORT_STATE.set()
    await message.answer(text=f'{choice_transport}', reply_markup=inline_kb)
