from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.constants import GO_BACK


async def go_to_transport_state(message: types.Message, state: FSMContext):
    await state.update_data(TRANSPORT_STATE=message.text)
    await message.answer(
        'Выбери номер маршрута.', reply_markup=types.ReplyKeyboardRemove()
        )
    list_button = []
    transport_list_button = await Data.parsing_categories(message.text)
    choice_transport = message.text
    for number_route in transport_list_button:
        inline_btn = InlineKeyboardButton(
            number_route, callback_data=f'{choice_transport}, {number_route}'
            )
        list_button.append(inline_btn)
    inline_go_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_kb = InlineKeyboardMarkup(row_width=8)
    inline_kb.add(*list_button)
    inline_kb.add(inline_go_back)
    await UserState.TRANSPORT_STATE.set()
    await message.answer(text=f'{choice_transport}', reply_markup=inline_kb)
