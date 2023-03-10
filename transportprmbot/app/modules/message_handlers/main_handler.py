from aiogram import types
from aiogram.dispatcher import FSM as FSM

from app.user_state import UserState
from app.constants import MAIN_MENU, LOCATION


async def go_to_main_state(message: types.Message, state: FSM):
    await state.finish()
    await state.update_data(MAIN_STATE=message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*MAIN_MENU)
    markup.add(types.KeyboardButton(LOCATION, request_location=True))
    await message.answer(text='Что будем делать?', reply_markup=markup)
    await UserState.MAIN_STATE.set()
