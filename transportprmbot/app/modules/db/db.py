# import asyncio
from datetime import datetime
import re
import pytz

from app.constants import BUS, TRAMWAY, YES
from app.modules.db.config_db import ROUTE_TYPES_TREE_COLLECTION, \
    FULL_ROUTE_COLLECTION, TIME_TRANSPORT, \
    PLACES_COLLECTION, DATA_TRANSPORT


# Получение списка номеров маршрутов.
async def get_route_numbers(message):
    routes_bus = []
    routes_tramway = []
    routes_taxi = []
    for type_transport in ROUTE_TYPES_TREE_COLLECTION.find():
        for type_routes in type_transport['children']:
            if type_routes['routeTypeId'] == 0:
                routes_bus.append(type_routes['routeNumber'])
            elif type_routes['routeTypeId'] == 2:
                routes_tramway.append(type_routes['routeNumber'])
            elif type_routes['routeTypeId'] == 3:
                routes_taxi.append(type_routes['routeNumber'])
    if message == BUS:
        return routes_bus
    elif message == TRAMWAY:
        return routes_tramway
    else:
        return routes_taxi


# Получаем данные о направлении движения
async def get_direction(number_route):
    directions = []
    type = number_route['TRANSPORT_STATE']
    route_number = number_route['ROUTES_STATE']
    route_id = await get_route_id(type, route_number)
    for direction_station in FULL_ROUTE_COLLECTION.find():
        for station in direction_station.values():
            if route_id == station:
                directions.append(
                    direction_station["fwdStoppoints"][0]["stoppointName"]
                    )
                directions.append(
                    direction_station["fwdStoppoints"][-1]["stoppointName"]
                    )
                if direction_station["bkwdStoppoints"] == []:
                    directions.append(
                        direction_station["fwdStoppoints"][-1]
                        ["stoppointName"]
                        )
                else:
                    directions.append(
                        direction_station["bkwdStoppoints"][0]
                        ["stoppointName"]
                        )
                    directions.append(
                        direction_station["bkwdStoppoints"][-1]
                        ["stoppointName"]
                        )
    return directions


# Ищем названия остановок транспорта по его типу
async def get_station_name(state_data):
    stations = []
    transport = state_data['TRANSPORT_STATE']
    route_number = state_data['ROUTES_STATE']
    direction = state_data['DIRECTION_STATE'].split('-')
    route_id = await get_route_id(transport, route_number)
    for direction_station in FULL_ROUTE_COLLECTION.find(
                {
                    'routeId': route_id
                }
            ):
        if direction[0] ==\
                direction_station["fwdStoppoints"][0]["stoppointName"]:
            for station in direction_station["fwdStoppoints"]:
                stations.append(station['stoppointName'])
        else:
            for station in direction_station["bkwdStoppoints"]:
                stations.append(station['stoppointName'])
    return stations


# По типу транспорта и номеру маршрута ищем id маршрута
async def get_route_id(transport, route_number):
    route_type_bus = ROUTE_TYPES_TREE_COLLECTION.find(
        {'children.routeTypeId': 0}
        )
    route_type_tramway = ROUTE_TYPES_TREE_COLLECTION.find(
        {'children.routeTypeId': 2}
        )
    route_type_taxi = ROUTE_TYPES_TREE_COLLECTION.find(
        {'children.routeTypeId': 3}
        )
    if transport == BUS:
        for bus_dict in route_type_bus:
            for id in bus_dict['children']:
                if id['routeNumber'] == route_number:
                    return id['routeId']
    elif transport == TRAMWAY:
        for tramway_dict in route_type_tramway:
            for id in tramway_dict['children']:
                if id['routeNumber'] == route_number:
                    return id['routeId']
    else:
        for taxi_dict in route_type_taxi:
            for id in taxi_dict['children']:
                if id['routeNumber'] == route_number:
                    return id['routeId']


# Получение расписания транспорта на остановке
async def get_timetable(user_data):
    transport = user_data['TRANSPORT_STATE']
    route_number = user_data['ROUTES_STATE']
    direction = user_data['DIRECTION_STATE'].split('-')
    try:
        station = user_data['STATION_STATE']
    except KeyError:
        d_places = PLACES_COLLECTION.find({'_id': user_data['_id']})
        station = d_places['STATION_STATE']
    td = pytz.timezone("Asia/Yekaterinburg")
    current_date_time = datetime.now(td)
    current_time = current_date_time.time()
    tn = current_time.strftime('%H:%M')
    route = await get_route_id(transport, route_number)
    id = await get_id_station(direction[0], station, route)
    times_res = [i for i in TIME_TRANSPORT.aggregate(
        [
            {'$project': {'_id': 1, 'station': 1}},
            {'$match': {'_id': id}}, {'$unwind': '$station'},
            {'$match': {'station.routeId': f'{route}'}},
            {'$project': {'station.scheduledTime': 1}}
        ])
        ]
    times_q = [j for i in times_res for j in i['station'].values()]
    str_answer = " ".join(map(str, times_q))
    time_list_answer = re.findall(r'\b\d{2}[:]\d{2}\b', str_answer)
    first_time = time_list_answer[0][0:2]
    full_timetable = []
    reduced_timetable = []
    for i in range(len(time_list_answer)):
        if first_time == time_list_answer[i][0:2]:
            full_timetable.append(f'{time_list_answer[i]} ')
        else:
            first_time = time_list_answer[i][0:2]
            full_timetable.append('\n')
            full_timetable.append(f'{time_list_answer[i]} ')
        if int(tn[0:2]) == int(time_list_answer[i][0:2]) \
                and int(tn[3:5]) <= int(time_list_answer[i][3:5]) \
                or int(tn[0:2]) < int(time_list_answer[i][0:2]):
            reduced_timetable.append(f'{time_list_answer[i]}')
            reduced_timetable.append('\n')
    if 'FULL_TIMETABLE_STATE' in user_data and \
            user_data['FULL_TIMETABLE_STATE'] == YES:
        return "".join(full_timetable)
    else:
        return "".join(reduced_timetable[0:9])


# Ищем id остановки по направлению и названию.
async def get_id_station(direction, station, route):
    user_direction = ''
    id_station = 0
    route_ids = [i for i in FULL_ROUTE_COLLECTION.find(
        {'routeId': f'{route}'}
        )
        ]
    for i in route_ids:
        if i['fwdStoppoints'][0]['stoppointName'] == direction:
            user_direction = 'fwdStoppoints'
        else:
            user_direction = 'bkwdStoppoints'
    for route_id in route_ids:
        for id in route_id[user_direction]:
            if station == id['stoppointName'][:32]:
                id_station = id['stoppointId']
    return id_station


# Получаем остановки по локации пользователя на растояннии 500м.
async def get_station_by_location(location):
    location_stations = []
    latitude = location['latitude']
    longitude = location['longitude']
    location_stations = [i for i in PLACES_COLLECTION.find(
        {
            'location':
            {
                '$nearSphere':
                {
                    '$geometry':
                        {
                            'type': 'Point',
                            'coordinates': [longitude, latitude]
                        },
                    '$minDistance': 0, '$maxDistance': 500
                }
            }
        }
        )
        ]
    try:
        return location_stations[0]
    except IndexError:
        return []


# Получаем данные по номерам маршрутов
async def get_number_route(route_id):
    types_numbers_route = {'Bus': [], 'Tramway': [], 'Taxi': []}
    for id in route_id:
        numbers = [i for i in DATA_TRANSPORT.find({'_id': str(id)})]
        if numbers[0]['routeTypeId'] == 0:
            types_numbers_route['Bus'].append(
                numbers[0]['routeNumber']
                )
        elif numbers[0]['routeTypeId'] == 2:
            types_numbers_route['Tramway'].append(
                numbers[0]['routeNumber']
                )
        else:
            types_numbers_route['Taxi'].append(numbers[0]['routeNumber'])
    return types_numbers_route


# Получаем направление транспорта исходя из найденной остановки
# по локации пользователя
async def get_direction_based_location(
        transport_type, station_id,
        route_number
        ):
    route = await get_route_id(transport_type, route_number)
    user_direction = ''
    route_ids = [i for i in FULL_ROUTE_COLLECTION.find(
        {'routeId': f'{route}'}
        )]
    for direction in route_ids[0]['fwdStoppoints']:
        if int(station_id) == int(direction['stoppointId']):
            user_direction =\
                route_ids[0]['fwdStoppoints'][0]['stoppointName']
    for direction in route_ids[0]['bkwdStoppoints']:
        if int(station_id) == int(direction['stoppointId']):
            user_direction =\
                route_ids[0]['bkwdStoppoints'][0]['stoppointName']
    return user_direction


# Получаем имя остановки по id
async def get_stop_name(user_data):
    stop_id = user_data[0]
    stop_name = PLACES_COLLECTION.find_one(
            {'stop_id': int(stop_id)}
            )
    return stop_name['name']
