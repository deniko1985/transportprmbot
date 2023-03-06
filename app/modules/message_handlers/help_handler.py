from aiogram import types
from aiogram.dispatcher import FSMContext

from app.constants import GO_BACK
from app.user_state import UserState
from app.modules.help.help import send_help


async def go_to_help_state(
        message: types.Message,
        state: FSMContext
        ):
    await state.update_data(HELP_STATE=message.text)
    help = await send_help(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(GO_BACK)
    await UserState.HELP_STATE.set()
    await message.answer(help, reply_markup=markup)
