import os
import re
import asyncio

from aiogram import Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import dp, bot
from schedule import *
from data import Data
from keyboard import keyboard_transport

class Transport(StatesGroup):
    user_id = State()    
    user_choice_transport = State()
    user_choice_action = State()
    user_choice_schedule = State()
    user_choice_favourites = State()
    user_choice_help = State()   

async def send_welcome(message: types.Message):
	#await Transport.user_id.set()
    list_button = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for button in keyboard_transport[:5]:
        list_button.append(button)    
    markup.add(*list_button)
    await message.answer(text='Что будем делать?', reply_markup=markup)
    await Transport.user_choice_transport.set()

async def transport_choice(message: types.Message, state: FSMContext):
    await state.update_data(choice_transport=message.text)	
    transport_list_button = []
    list_button = []
    if message.text == 'Автобус' or message.text == 'Трамвай' or message.text == 'Маршрутное такси':
        transport_list_button = Data.parsing_categories(message.text)
    #elif message.text == 'Трамвай':
    #    transport_list_button = Data.parsing_categories(message)
    #elif message.text == 'Маршрутное такси':
    #    transport_list_button = Data.parsing_categories(message)	
    #elif message.text == 'Избранное':
    #    pass                
        #await favourites(message, state=Transport.user_choice_favourites)
        #await Transport.user_choice_favourites.set()
    else:
        pass        
        #await send_help(message, state=Transport.user_choice_help)
        #await Transport.user_choice_help.set()
    for number_route in transport_list_button:
        inline_btn = InlineKeyboardButton(number_route, callback_data=f'{number_route}')
        list_button.append(inline_btn)
    inline_kb = InlineKeyboardMarkup(row_width=5)
    inline_kb.add(*list_button)
    await Transport.next()    
    await message.answer(text = 'Выбери номер маршрута', reply_markup=inline_kb)

async def choice_action(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(choice_number=call.data)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Расписание')
    btn2 = types.KeyboardButton('Карта')
    btn3 = types.KeyboardButton('Вернуться в главное меню')
    markup.add(btn1, btn2, btn3)
    await Transport.next()
    await call.message.answer('Выбери расписание или поиск на карте ', reply_markup=markup)

async def schedule(message: types.Message, state: FSMContext):
    await state.update_data(choice_schedule=message.text)
    number_route = await state.get_data()
    direction = Data.choice_direction(number_route)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(f'{direction[0]}')
    btn2 = types.KeyboardButton(f'{direction[2]}')
    btn3 = types.KeyboardButton('Вернуться в главное меню')
    markup.add(btn1, btn2, btn3)
    await message.answer('Выбери направление движения автобуса', reply_markup=markup)

async def favourites(message: types.Message, state: FSMContext):
    await state.update_data(choice_favourites=message.text)
    await message.answer('Пока не умею.')

async def send_help(message: types.Message, state: FSMContext):
    await state.update_data(choice_help=message.text)
    greeting = '''
	Здравствуй. Я бот для отслеживания общественного траспорта в городе Перми.
	С моей помощью ты сможешь:
	\t- узнать расписание транспорта
	\t- отследить транспорт на карте
	Но хочу предупредить, что я нахожусь в разработке, поэтому работа может быть нестабильной.
	'''
    await message.answer(greeting)

#    await state.reset_state(with_data=False)

def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands='start', state="*")
    dp.register_message_handler(transport_choice, state=Transport.user_choice_transport)
    dp.register_callback_query_handler(choice_action, state=Transport.user_choice_action)
    dp.register_message_handler(schedule, state=Transport.user_choice_schedule)
    dp.register_message_handler(favourites, state=Transport.user_choice_favourites)
    dp.register_message_handler(send_help, state=Transport.user_choice_help)

async def main():
    register_handlers_main(dp)
    
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())