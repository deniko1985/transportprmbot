from aiogram import types
from aiogram.dispatcher import FSMContext as FSM

from app.user_state import UserState
from app.help import send_help
from app.constants import GO_BACK


async def go_to_help_state(message: types.Message, state: FSM):
    await state.update_data(HELP_STATE=message.text)
    help = await send_help(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(GO_BACK)
    await UserState.HELP_STATE.set()
    await message.answer(help, reply_markup=markup)
