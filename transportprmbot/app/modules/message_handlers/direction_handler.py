from aiogram import types
from aiogram.dispatcher import FSMContext

from app.modules.db import db
from app.user_state import UserState
from app.constants import GO_BACK


async def go_to_direction_state(message: types.Message, state: FSMContext):
    number_route = await state.get_data()
    direction = await db.get_direction(number_route)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    forward = direction[0] + '-' + direction[1]
    backwards = direction[2] + '-' + direction[3]
    forward_btn = types.KeyboardButton(f'{forward}')
    backward_btn = types.KeyboardButton(f'{backwards}')
    go_back_btn = types.KeyboardButton(GO_BACK)
    markup.add(forward_btn)
    markup.add(backward_btn)
    markup.add(go_back_btn)
    await UserState.DIRECTION_STATE.set()
    await message.answer(
        'Выбери направление движения транспорта', reply_markup=markup
        )
