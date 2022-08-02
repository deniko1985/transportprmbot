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

from favourites import Favourites
from config import dp, bot, user_collection
from parsing import *
from data import Data
from maps import Maps
from help import send_help
from keyboard import keyboard_user_choice, keyboard_choice_action, BUS, TRAMWAY, TAXI, FAVOURITES, HELP, TIMETABLE, MAPS

class Transport(StatesGroup):        
    user_choice_transport = State()
    user_choice_action = State()
    user_choice_schedule = State()    
    user_choice_maps = State()
    user_choice_direction = State()
    user_choice_station = State()
    user_choice_favourites = State()
    user_choice_help = State()
    user_back_button = State()   

async def send_welcome(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)
    favour = Favourites()        
    list_button = []
    user_data = await state.get_data()
    #await favour.check_user(message.from_user.id, message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for button in keyboard_user_choice:
        list_button.append(button)    
    markup.add(*list_button)
    await message.answer(text='Что будем делать?', reply_markup=markup)
    await Transport.user_choice_transport.set()

async def user_choice(message: types.Message, state: FSMContext):
    await state.update_data(choice_transport=message.text)	
    transport_list_button = []
    list_button = []
    if message.text == FAVOURITES:
        list_button_favourites_bus = []
        list_button_favourites_tramway = []
        list_button_favourites_taxi = []
        user_data = await state.get_data()
        user_favourites = await Favourites.choice_favourites(message.from_user.id)        
        inline_kb_favourites = InlineKeyboardMarkup(row_width=1)
        inline_kb_favourites_bus = InlineKeyboardMarkup(row_width=5)
        inline_kb_favourites_tramway = InlineKeyboardMarkup(row_width=5)
        inline_kb_favourites_taxi = InlineKeyboardMarkup(row_width=5)              
        bus_favourites = user_favourites[0]
        tram_favourites = user_favourites[1]
        taxi_favourites = user_favourites[2]
        if user_favourites[0][1] != []:
            for number_favourites in user_favourites[0][1]:
                inline_btn_favourites_bus = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{user_favourites[0][0]}, {number_favourites}')
                list_button_favourites_bus.append(inline_btn_favourites_bus)
        if user_favourites[1][1] != []:
            for number_favourites in user_favourites[1][1]:
                inline_btn_favourites_tramway = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{user_favourites[1][0]}, {number_favourites}')
                list_button_favourites_tramway.append(inline_btn_favourites_tramway)     
        if user_favourites[2][1] != []:
            for number_favourites in user_favourites[2][1]:
                inline_btn_favourites_taxi = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{user_favourites[2][0]}, {number_favourites}')                      
                list_button_favourites_taxi.append(inline_btn_favourites_taxi)                           
        inline_back = InlineKeyboardButton('Вернуться назад', callback_data='back')
        inline_kb_favourites_bus.add(*list_button_favourites_bus)
        inline_kb_favourites_tramway.add(*list_button_favourites_tramway)
        inline_kb_favourites_taxi.add(*list_button_favourites_taxi)
        inline_kb_favourites.add(inline_back)
        await Transport.next()
        print(user_favourites[0][1], user_favourites[1][1], user_favourites[2][1])
        #await message.answer(text = 'Выбери номер маршрута', reply_markup=inline_kb_favourites)
        if user_favourites[0][1] == [] and user_favourites[1][1] == [] and user_favourites[2][1] == []:
            await message.answer(text = 'У вас не добавлено ни одного маршрута!')
        if user_favourites[0][1] != []:
            await message.answer(text = 'Автобус:', reply_markup=inline_kb_favourites_bus)
        if user_favourites[1][1] != []:
            await message.answer(text = 'Трамвай:', reply_markup=inline_kb_favourites_tramway)
        if user_favourites[2][1] != []:
            await message.answer(text = 'Маршрутное такси:', reply_markup=inline_kb_favourites_taxi)
    elif message.text == HELP:
        await send_help(message.from_user.id)
        return
    else:
        transport_list_button = await Data.parsing_categories(message.text)
        choice_transport=message.text
        for number_route in transport_list_button:
            inline_btn = InlineKeyboardButton(number_route, callback_data=f'{choice_transport}, {number_route}')
            list_button.append(inline_btn)
        inline_back = InlineKeyboardButton('Вернуться назад', callback_data='back')
        inline_kb = InlineKeyboardMarkup(row_width=8)
        inline_kb.add(*list_button)
        inline_kb.add(inline_back)
        await Transport.next()    
        await message.answer(text = 'Выбери номер маршрута', reply_markup=inline_kb)

async def choice_action(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await Transport.previous()
        return await call.message.answer('Хорошо.')        
    else:
        number=call.data.split(', ')
        await state.update_data(choice_transport=number[0], choice_number=number[1])
        list_button = []
        user_data = await state.get_data()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)    
        for button in keyboard_choice_action:
            list_button.append(button)
        button_back = types.KeyboardButton('Вернуться назад')
        markup.add(*list_button)
        markup.add(button_back)
        await Transport.next()
        await call.message.answer('Выбери расписание или поиск на карте ', reply_markup=markup)

async def schedule(message: types.Message, state: FSMContext):
#    await message.answer(reply_markup=types.ReplyKeyboardRemove()) 
    if message.text == 'Вернуться назад':       
        await Transport.user_choice_action.set()
        return await message.answer('Хорошо.')        
    elif message.text == MAPS:
        await Maps.choice_maps(message.from_user.id)
    else:
        await state.update_data(choice_schedule=message.text)
        number_route = await state.get_data()
        direction = await Data.choice_direction(number_route)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton(f'{direction[0]}')
        button2 = types.KeyboardButton(f'{direction[2]}')
        markup.add(button1, button2)
        await Transport.user_choice_direction.set()
        await message.answer('Выбери направление движения транспорта', reply_markup=markup)             

async def station(message: types.Message, state: FSMContext):
    await state.update_data(user_direction=message.text)
    list_button = []
    user_data = await state.get_data()
    print(user_data)
    station_list = await Data.choice_station(user_data)
    for title_station in station_list:
        inline_button = InlineKeyboardButton(f'{title_station}', callback_data=f'{title_station[:32]}')
        list_button.append(inline_button)
    inline_station_list = InlineKeyboardMarkup(row_width=2)
    inline_station_list.add(*list_button)    
    await Transport.next()    
    await message.answer(text = 'Выбери остановку', reply_markup=inline_station_list)

async def time(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_station=call.data)        
    time_data = await state.get_data()
    print(time_data)
    user = await Data.time_sort(time_data)
    await call.message.answer(text = f'{user}')
    data = await Favourites.check_favourites(call.from_user.id, time_data['choice_transport'], time_data['choice_number'])
    if data:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_btn_1 = InlineKeyboardButton('Да', callback_data='yes')
        inline_btn_2 = InlineKeyboardButton('Нет', callback_data='no')
        inline_kb.add(inline_btn_1, inline_btn_2)
        await Transport.user_choice_favourites.set()   
        await call.message.answer('Добавить маршрут в избранное?', reply_markup=inline_kb)
    else:
        await state.reset_state(with_data=True)   
    
async def favourites(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_time=call.data)
    user_data = await state.get_data()
    print(user_data)
    if call.data == 'yes':
        add_user = await Favourites.add_favourites(call.from_user.id, user_data)
        await call.message.answer(text = f'{add_user}')
    else:
        await call.message.answer(text = 'No.')
    
    await state.reset_state(with_data=True)

def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands='start', state="*")
    dp.register_message_handler(user_choice, state=Transport.user_choice_transport)
    dp.register_callback_query_handler(choice_action, state=Transport.user_choice_action)
    dp.register_message_handler(schedule, state=Transport.user_choice_schedule)
    dp.register_message_handler(station, state=Transport.user_choice_direction)
    dp.register_callback_query_handler(time, state=Transport.user_choice_station)
    dp.register_callback_query_handler(favourites, state=Transport.user_choice_favourites)

async def main():
    register_handlers_main(dp)
    
    #loop = asyncio.get_event_loop()
    #loop.create_task(send_welcome(10, state="*"))
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())