from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):
    MAIN_STATE = State()
    HELP_STATE = State()
    FAVOURITES_STATE = State()
    LOCATION_STATE = State()
    TRANSPORT_STATE = State()
    ROUTES_STATE = State()
    ROUTE_STATE = State()
    DIRECTION_STATE = State()
    STATION_STATE = State()
    TIMETABLE_STATE = State()
