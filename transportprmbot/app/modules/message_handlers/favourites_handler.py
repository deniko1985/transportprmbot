from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from app.user_state import UserState
from app import favourites
from app.constants import BUS, TRAMWAY, TAXI, GO_BACK, DELETE, YES, NO


async def go_to_favourites_state(
        message: types.Message,
        state: FSMContext
        ):
    await state.update_data(FAVOURITES_STATE=message.text)
    await message.answer(
        'Избранное:',
        reply_markup=types.ReplyKeyboardRemove()
        )
    user_numbers = await favourites.get_route_numbers(
        message.from_user.id)
    f_bus_kb = InlineKeyboardMarkup(row_width=5)
    f_tramway_kb = InlineKeyboardMarkup(row_width=5)
    f_taxi_kb = InlineKeyboardMarkup(row_width=5)
    # keybord = await keyboard_fovourites(user_numbers)
    f_bus_buttons = []
    f_tramway_buttons = []
    f_taxi_buttons = []
    f_bus_numbers = user_numbers[0]
    f_tramway_numbers = user_numbers[1]
    f_taxi_numbers = user_numbers[2]
    if f_bus_numbers[1] != []:
        for number_route in f_bus_numbers[1]:
            f_bus_button = InlineKeyboardButton(
                f'{number_route}',
                callback_data=f'{f_bus_numbers[0]}, {number_route}'
                )
            f_bus_buttons.append(f_bus_button)
    if f_tramway_numbers[1] != []:
        for number_route in f_tramway_numbers[1]:
            f_tramway_button = InlineKeyboardButton(
                f'{number_route}',
                callback_data=f'{f_tramway_numbers[0]}, {number_route}'
                )
            f_tramway_buttons.append(
                f_tramway_button
                )
    if f_taxi_numbers[1] != []:
        for number_route in f_taxi_numbers[1]:
            f_taxi_button = InlineKeyboardButton(
                f'{number_route}',
                callback_data=f'{f_taxi_numbers[0]}, {number_route}'
                )
            f_taxi_buttons.append(f_taxi_button)
    f_bus_kb.add(*f_bus_buttons)
    f_tramway_kb.add(*f_tramway_buttons)
    f_taxi_kb.add(*f_taxi_buttons)
    # await UserState.next()
    if f_bus_numbers[1] == []\
            and f_tramway_numbers[1] == []\
            and f_taxi_numbers[1] == []:
        await message.answer(text='У вас не добавлено ни одного маршрута!')
    if f_bus_numbers[1] != []:
        await message.answer(
            text=BUS, reply_markup=f_bus_kb
            )
    if f_tramway_numbers[1] != []:
        await message.answer(
            text=TRAMWAY, reply_markup=f_tramway_kb
            )
    if f_taxi_numbers[1] != []:
        await message.answer(
            text=TAXI, reply_markup=f_taxi_kb
            )
    inline_kb_favourites = InlineKeyboardMarkup(row_width=1)
    inline_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_del = InlineKeyboardButton(DELETE, callback_data=DELETE)
    inline_kb_favourites.add(inline_back, inline_del)
    await UserState.FAVOURITES_STATE.set()
    await message.answer(text='Или', reply_markup=inline_kb_favourites)


async def go_to_delete_type_favourites(
        message: types.Message,
        state: FSMContext
        ):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    bus_btn = types.KeyboardButton(BUS)
    tramway_btn = types.KeyboardButton(TRAMWAY)
    taxi_btn = types.KeyboardButton(TAXI)
    button_go_back = types.KeyboardButton(GO_BACK)
    # button_back = types.KeyboardButton(BACK)
    markup.add(bus_btn, tramway_btn, taxi_btn)
    markup.add(button_go_back)
    await message.answer(
        'Введи вид транспорта для удаления',
        reply_markup=markup
        )
    await UserState.DELETE_TYPE_FAVOURITES_STATE.set()


async def go_to_delete_route_favourites(
        message: types.Message,
        state: FSMContext
        ):
    await message.answer(
        'Введи номер маршрута для удаления',
        reply_markup=types.ReplyKeyboardRemove()
        )
    await UserState.DELETE_ROUTE_FAVOURITES_STATE.set()


async def go_to_delete_favourites(
        message: types.Message,
        state: FSMContext
        ):
    await message.answer(text=f'{message.text}')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    yes_btn = types.KeyboardButton(YES)
    no_btn = types.KeyboardButton(NO)
    markup.add(yes_btn, no_btn)
    await message.answer(
        'Выбрать еще для удаления?',
        reply_markup=markup
        )
    await UserState.DELETE_FAVOURITES_STATE.set()
