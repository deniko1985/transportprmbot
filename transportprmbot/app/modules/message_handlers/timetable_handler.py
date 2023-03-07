from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.favourites import Favourites
from app.constants import GO_BACK, YES, NO


async def go_to_timetable_choice(call: types.CallbackQuery, state: FSMContext):
    inline_choice_kb = InlineKeyboardMarkup(row_width=2)
    inline_yes = InlineKeyboardButton(YES, callback_data=YES)
    inline_no = InlineKeyboardButton(NO, callback_data=NO)
    inline_choice_kb.add(inline_yes, inline_no)
    await UserState.CHOICE_TIMETABLE_STATE.set()
    await call.message.answer(
        text="Показать 5 ближайших остановок или полное расписание",
        reply_markup=inline_choice_kb
        )


async def go_to_timetable_state(call: types.CallbackQuery, state: FSMContext):
    time_data = await state.get_data()
    print('=======================================')
    print('time_data: ', time_data)
    print('=======================================')
    user = await Data.time_sort(time_data)
    await call.message.answer(
        text=f'{user}', reply_markup=types.ReplyKeyboardRemove()
        )
    data = await Favourites.check_favourites(
        call.from_user.id, time_data['TRANSPORT_STATE'],
        time_data['ROUTES_STATE']
        )
    await UserState.TIMETABLE_STATE.set()
    if data:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_btn_1 = InlineKeyboardButton(YES, callback_data=YES)
        inline_btn_2 = InlineKeyboardButton(NO, callback_data=NO)
        inline_kb.add(inline_btn_1, inline_btn_2)
        await call.message.answer(
            'Добавить маршрут в избранное?', reply_markup=inline_kb
            )
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_btn_back = InlineKeyboardButton('Жми здесь', callback_data=GO_BACK)
    inline_kb.add(inline_btn_back)
    await call.message.answer('Вернуться в начало?', reply_markup=inline_kb)
