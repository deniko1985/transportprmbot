from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext as FSM

from app.modules.db import db
from app.user_state import UserState
from app import favourites
from app.constants import YES, NO, HOME


async def go_to_timetable(call: types.CallbackQuery, state: FSM):
    await state.update_data(TIMETABLE_STATE=NO)
    user_data = await state.get_data()
    user = await db.get_timetable(user_data)
    await call.message.answer(text=f'{user}')
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_btn_1 = InlineKeyboardButton(YES, callback_data=YES)
    inline_btn_2 = InlineKeyboardButton(NO, callback_data=NO)
    inline_kb.add(inline_btn_1, inline_btn_2)
    await UserState.TIMETABLE_STATE.set()
    await call.message.answer('Показать полное расписание на день?', reply_markup=inline_kb)


async def go_to_timetable_state(call: types.CallbackQuery, state: FSM):
    user_data = await state.get_data()
    if user_data['FULL_TIMETABLE_STATE'] == YES:
        user = await db.get_timetable(user_data)
        await call.message.answer(text=f'{user}', reply_markup=types.ReplyKeyboardRemove())
    data = await favourites.get_favorites_data(
            call.from_user.id,
            user_data['TRANSPORT_STATE'],
            user_data['ROUTES_STATE']
        )
    if data:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_btn_1 = InlineKeyboardButton(YES, callback_data=YES)
        inline_btn_2 = InlineKeyboardButton(NO, callback_data=NO)
        inline_kb.add(inline_btn_1, inline_btn_2)
        await call.message.answer('Добавить маршрут в избранное?', reply_markup=inline_kb)
    await UserState.FULL_TIMETABLE_STATE.set()
    inline_kb = InlineKeyboardMarkup()
    inline_go_back = InlineKeyboardButton(HOME, callback_data=HOME)
    inline_kb.add(inline_go_back)
    await call.message.answer(text='На главную страницу', reply_markup=inline_kb)
