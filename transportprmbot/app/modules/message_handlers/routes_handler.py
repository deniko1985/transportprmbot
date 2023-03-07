from aiogram import types
from aiogram.dispatcher import FSMContext

from app.modules.db.db import Data
from app.user_state import UserState
from app.constants import TIMETABLE, MAPS, GO_BACK, BACK


async def go_to_routes_state(call: types.CallbackQuery, state: FSMContext):
    number_route = call.data.split(', ')
    await state.update_data(
        TRANSPORT_STATE=number_route[0], ROUTES_STATE=number_route[1]
        )
    user_data = await state.get_data()
    route_id = await Data.binding_id(
        user_data['TRANSPORT_STATE'], user_data['ROUTES_STATE']
        )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    app_maps = types.WebAppInfo(
        url=f'https://app.deniko1985.ml/routes/{route_id}'
        )
    # app_maps = types.WebAppInfo(
    #    url=f'https://www.m.gortransperm.ru/map/{route_id}'
    #    )
    button_maps = types.KeyboardButton(MAPS, web_app=app_maps)
    button_timetable = types.KeyboardButton(TIMETABLE)
    button_go_back = types.KeyboardButton(GO_BACK)
    button_back = types.KeyboardButton(BACK)
    markup.add(button_timetable, button_maps)
    markup.add(button_back, button_go_back)
    await UserState.ROUTES_STATE.set()
    await call.message.answer(
        'Выбери расписание или поиск на карте ', reply_markup=markup
        )
