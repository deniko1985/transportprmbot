import aiogram
from aiogram import Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.web_app_info import WebAppInfo

from favourites.favourites import Favourites
from db.db import Data
from db.config_db import USER_COLLECTION
from maps.maps import Maps
from help.help import send_help
from constants import MAIN_MENU, MAIN_ROUTE, BUS, TRAMWAY, TAXI, FAVOURITES, HELP, TIMETABLE, MAPS, GO_BACK, BACK, YES, NO

class UserState(StatesGroup):
    MAIN_STATE = State()
    HELP_STATE = State()
    FAVOURITES_STATE = State()
    TRANSPORT_STATE = State()    
    ROUTES_STATE = State()
    ROUTE_STATE = State()
    DIRECTION_STATE = State()
    STATION_STATE = State()
    TIMETABLE_STATE = State()

async def state_message_start(message: types.Message, state: FSMContext):
    await go_to_main_state(message, state)

async def go_to_main_state(message: types.Message, state: FSMContext):
    await state.finish()
    await state.update_data(MAIN_STATE=message.text)    
    await Favourites.check_user(message.from_user.id, message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*MAIN_MENU)    
    await message.answer(text='Что будем делать?', reply_markup=markup)
    await UserState.MAIN_STATE.set()

async def main_state_message_handler(message: types.Message, state: FSMContext):
    if message.text == HELP:
        await go_to_help_state(message, state)
    elif message.text == FAVOURITES:
        await go_to_favourites_state(message, state)
    elif message.text in [BUS, TRAMWAY, TAXI]:
        await go_to_transport_state(message, state)

async def go_to_help_state(message: types.Message, state: FSMContext):
    await state.update_data(HELP_STATE=message.text)
    help = await send_help(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(GO_BACK)
    await UserState.HELP_STATE.set()
    await message.answer(help, reply_markup=markup)

async def help_state_message_handler(message: types.Message, state: FSMContext):
    print(message.text)
    if message.text == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(message, state)
    else:
        await message.answer('Попробуй еще раз.')
        return

async def go_to_favourites_state(message: types.Message, state: FSMContext):
    await state.update_data(FAVOURITES_STATE=message.text)
    await message.answer('Избранное:', reply_markup=types.ReplyKeyboardRemove())
    list_button_favourites_bus = []
    list_button_favourites_tramway = []
    list_button_favourites_taxi = []
    user_data = await state.get_data()
    user_favourites = await Favourites.choice_favourites(message.from_user.id)        
    inline_kb_favourites_bus = InlineKeyboardMarkup(row_width=5)
    inline_kb_favourites_tramway = InlineKeyboardMarkup(row_width=5)
    inline_kb_favourites_taxi = InlineKeyboardMarkup(row_width=5)              
    bus_favourites = user_favourites[0]
    tram_favourites = user_favourites[1]
    taxi_favourites = user_favourites[2]
    if bus_favourites[1] != []:
        for number_favourites in bus_favourites[1]:
            inline_btn_favourites_bus = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{bus_favourites[0]}, {number_favourites}')
            list_button_favourites_bus.append(inline_btn_favourites_bus)
    if tram_favourites[1] != []:
        for number_favourites in tram_favourites[1]:
            inline_btn_favourites_tramway = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{tram_favourites[0]}, {number_favourites}')
            list_button_favourites_tramway.append(inline_btn_favourites_tramway)     
    if taxi_favourites[1] != []:
        for number_favourites in taxi_favourites[1]:
            inline_btn_favourites_taxi = InlineKeyboardButton(f'{number_favourites}', callback_data=f'{taxi_favourites[0]}, {number_favourites}')                      
            list_button_favourites_taxi.append(inline_btn_favourites_taxi)                           
    inline_kb_favourites_bus.add(*list_button_favourites_bus)
    inline_kb_favourites_tramway.add(*list_button_favourites_tramway)
    inline_kb_favourites_taxi.add(*list_button_favourites_taxi)
    await UserState.next()
    if bus_favourites[1] == [] and tram_favourites[1] == [] and taxi_favourites[1] == []:
        await message.answer(text = 'У вас не добавлено ни одного маршрута!')
    if bus_favourites[1] != []:
        await message.answer(text = BUS, reply_markup=inline_kb_favourites_bus)
    if tram_favourites[1] != []:
        await message.answer(text = TRAMWAY, reply_markup=inline_kb_favourites_tramway)
    if taxi_favourites[1] != []:
        await message.answer(text = TAXI, reply_markup=inline_kb_favourites_taxi)
#    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#    markup.add(GO_BACK)
    inline_kb_favourites = InlineKeyboardMarkup(row_width=1)
    inline_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_kb_favourites.add(inline_back)
    await UserState.FAVOURITES_STATE.set()
    await message.answer(text = 'Или', reply_markup=inline_kb_favourites)

async def favourites_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    print(f'call: {call}')
    print(f'call.data: {call.data}')
    print(f'call.message: {call.message}')
    print(f'call.message.text: {call.message.text}')    
    if call.data == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(call.message, state)
    else:
        await go_to_routes_state(call, state)
        return

async def go_to_transport_state(message: types.Message, state: FSMContext):
    await state.update_data(TRANSPORT_STATE=message.text)
    list_button = []
    transport_list_button = await Data.parsing_categories(message.text)
    choice_transport=message.text
    for number_route in transport_list_button:
        inline_btn = InlineKeyboardButton(number_route, callback_data=f'{choice_transport}, {number_route}')
        list_button.append(inline_btn)
#        inline_back = InlineKeyboardButton(GO_BACK, callback_data='back')
    inline_kb = InlineKeyboardMarkup(row_width=8)
    inline_kb.add(*list_button)
#    inline_kb.add(inline_back)
    await UserState.TRANSPORT_STATE.set()
    await message.answer(text = 'Выбери номер маршрута', reply_markup=inline_kb)

async def transport_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    print(call.data)
    print(call.message.text)
    if call.message.text == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(call.message, state)
    else:
        await go_to_routes_state(call, state)        

async def go_to_routes_state(call: types.CallbackQuery, state: FSMContext):
    number_route=call.data.split(', ')
    await state.update_data(TRANSPORT_STATE=number_route[0], ROUTES_STATE=number_route[1])
    user_data = await state.get_data()
    route_id = await Data.binding_id(user_data['TRANSPORT_STATE'], user_data['ROUTES_STATE'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    app_maps = types.WebAppInfo(url=f'https://app-deniko1985.ml/{route_id}')
    button_maps = types.KeyboardButton(MAPS, web_app=app_maps)
    button_timetable = types.KeyboardButton(TIMETABLE)
    button_go_back = types.KeyboardButton(GO_BACK)
    button_back = types.KeyboardButton(BACK)
    markup.add(button_timetable, button_maps)
    markup.add(button_back, button_go_back)
    await UserState.ROUTES_STATE.set()
    await call.message.answer('Выбери расписание или поиск на карте ', reply_markup=markup)

async def routes_state_message_handler(message: types.Message, state: FSMContext):
    if message.text == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(message, state)
    elif message.text == BACK:
        user_data = await state.get_data()
        if user_data.get('FAVOURITES_STATE'):
            await UserState.FAVOURITES_STATE.set()
            message.text = user_data['FAVOURITES_STATE']
            await go_to_favourites_state(message, state)
        else:
            await UserState.TRANSPORT_STATE.set()
            message.text = user_data['TRANSPORT_STATE']
            await go_to_transport_state(message, state)
    else:
        await go_to_direction_state(message, state)

async def go_to_direction_state(message: types.Message, state: FSMContext):
#    await message.answer(reply_markup=types.ReplyKeyboardRemove())     
    number_route = await state.get_data()
    direction = await Data.choice_direction(number_route)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton(f'{direction[0]}')
    button2 = types.KeyboardButton(f'{direction[2]}')
    button3 = types.KeyboardButton(GO_BACK)
    button4 = types.KeyboardButton(BACK)
    markup.add(button1, button2)
    markup.add(button3, button4)
    await UserState.DIRECTION_STATE.set()
    await message.answer('Выбери направление движения транспорта', reply_markup=markup)

async def direction_state_message_handler(message: types.Message, state: FSMContext):
    if message.text == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(message, state)
    elif message.text == BACK:
        user_data = await state.get_data()
        message.text = user_data['DIRECTION_STATE']
        await UserState.ROUTES_STATE.set()
        await go_to_routes_state(message, state)
    else:
        await state.update_data(DIRECTION_STATE=message.text)
        await go_to_station_state(message, state)

async def go_to_station_state(message: types.Message, state: FSMContext):    
    list_button = []
    user_data = await state.get_data()
    station_list = await Data.choice_station(user_data)
    for title_station in station_list:
        inline_button = InlineKeyboardButton(f'{title_station}', callback_data=f'{title_station[:32]}')
        list_button.append(inline_button)
    inline_station_list = InlineKeyboardMarkup(row_width=3)
    inline_go_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_back = InlineKeyboardButton(BACK, callback_data=BACK)
    inline_station_list.add(*list_button)
    inline_station_list.add(inline_back, inline_go_back)    
    await UserState.STATION_STATE.set()    
    await message.answer(text = 'Выбери остановку', reply_markup=inline_station_list)

async def station_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(call.message, state)
    elif call.data == BACK:
        user_data = await state.get_data()
        call.data = user_data['STATION_STATE']
        await UserState.STATION_STATE.set()
        await go_to_direction_state(call, state)
    else:
        await state.update_data(STATION_STATE=call.data)
        await go_to_timetable_state(call, state)

async def go_to_timetable_state(call: types.CallbackQuery, state: FSMContext):            
    time_data = await state.get_data()
    user = await Data.time_sort(time_data)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(GO_BACK)
    markup.add(button)
    await call.message.answer(text = f'{user}', reply_markup=markup)
    data = await Favourites.check_favourites(call.from_user.id, time_data['TRANSPORT_STATE'], time_data['ROUTES_STATE'])
    if data:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_btn_1 = InlineKeyboardButton(YES, callback_data=YES)
        inline_btn_2 = InlineKeyboardButton(NO, callback_data=NO)
        inline_kb.add(inline_btn_1, inline_btn_2)        
        await UserState.TIMETABLE_STATE.set()   
        await call.message.answer('Добавить маршрут в избранное?', reply_markup=inline_kb)
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_btn_back = InlineKeyboardButton(GO_BACK, callback_data=GO_BACK)
    inline_kb.add(inline_btn_back)
    await call.message.answer('Вернуться назад', reply_markup=inline_kb)

async def timetable_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(TIMETABLE_STATE=call.data)
    if call.data == GO_BACK:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(call.message, state)
    elif call.data == NO:
        await UserState.MAIN_STATE.set()
        await go_to_main_state(call.message, state)
    elif call.data == YES:
        user_data = await state.get_data()
        add_user = await Favourites.add_favourites(call.from_user.id, user_data)
        await call.message.answer(text = f'{add_user}')

def register_handlers_message_handler(dp: Dispatcher):
    dp.register_message_handler(state_message_start, commands='start', state='*')
    dp.register_message_handler(main_state_message_handler, state=UserState.MAIN_STATE)
    dp.register_message_handler(help_state_message_handler, state=UserState.HELP_STATE)    
    dp.register_callback_query_handler(favourites_state_message_handler, state=UserState.FAVOURITES_STATE)
    dp.register_callback_query_handler(transport_state_message_handler, state=UserState.TRANSPORT_STATE)
    dp.register_message_handler(routes_state_message_handler, state=UserState.ROUTES_STATE)
    dp.register_message_handler(direction_state_message_handler, state=UserState.DIRECTION_STATE)
    dp.register_callback_query_handler(station_state_message_handler, state=UserState.STATION_STATE)
    dp.register_callback_query_handler(timetable_state_message_handler, state=UserState.TIMETABLE_STATE)