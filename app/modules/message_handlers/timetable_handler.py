from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.modules.favourites.favourites import Favourites
from app.constants import GO_BACK, YES, NO


async def go_to_timetable_state(call: types.CallbackQuery, state: FSMContext):
    time_data = await state.get_data()
    user = await Data.time_sort(time_data)
    await call.message.answer(
        text=f'{user}', reply_markup=types.ReplyKeyboardRemove()
        )
    data = await Favourites.check_favourites(
        call.from_user.id, time_data['TRANSPORT_STATE'],
        time_data['ROUTES_STATE']
        )
    if data:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_btn_1 = InlineKeyboardButton(YES, callback_data=YES)
        inline_btn_2 = InlineKeyboardButton(NO, callback_data=NO)
        inline_kb.add(inline_btn_1, inline_btn_2)
        await UserState.TIMETABLE_STATE.set()
        await call.message.answer(
            'Добавить маршрут в избранное?', reply_markup=inline_kb
            )
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_btn_back = InlineKeyboardButton('Жми здесь', callback_data=GO_BACK)
    inline_kb.add(inline_btn_back)
    await call.message.answer('Вернуться в начало?', reply_markup=inline_kb)
