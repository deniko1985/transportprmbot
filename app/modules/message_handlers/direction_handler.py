from aiogram import types
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.constants import GO_BACK


async def go_to_direction_state(message: types.Message, state: FSMContext):
    number_route = await state.get_data()
    direction = await Data.choice_direction(number_route)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton(f'{direction[0]}')
    button2 = types.KeyboardButton(f'{direction[2]}')
    # button3 = types.KeyboardButton(BACK)
    button4 = types.KeyboardButton(GO_BACK)
    markup.add(button1, button2)
    markup.add(button4)
    await UserState.DIRECTION_STATE.set()
    await message.answer(
        'Выбери направление движения транспорта', reply_markup=markup
        )
