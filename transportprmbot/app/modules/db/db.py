# import asyncio
import re

from app.constants import BUS, TRAMWAY
from app.modules.db.config_db import ROUTE_TYPES_TREE_COLLECTION, \
    FULL_ROUTE_COLLECTION, TIME_TRANSPORT, \
    PLACES_COLLECTION, DATA_TRANSPORT


class Data():

    # Получение списка номеров маршрутов.
    @staticmethod
    async def parsing_categories(message):
        transport_routes_bus = []
        transport_routes_tramway = []
        transport_routes_taxi = []
        for type_transport in ROUTE_TYPES_TREE_COLLECTION.find():
            for type_routes in type_transport['children']:
                if type_routes['routeTypeId'] == 0:
                    transport_routes_bus.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 2:
                    transport_routes_tramway.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 3:
                    transport_routes_taxi.append(type_routes['routeNumber'])
        if message == BUS:
            return transport_routes_bus
        elif message == TRAMWAY:
            return transport_routes_tramway
        else:
            return transport_routes_taxi

    # Получаем данные о направлении движения
    @staticmethod
    async def choice_direction(number_route):
        direction = []
        transport = number_route['TRANSPORT_STATE']
        route_number = number_route['ROUTES_STATE']
        binding = await Data.binding_id(transport, route_number)
        for station_direction in FULL_ROUTE_COLLECTION.find():
            for station in station_direction.values():
                if binding == station:
                    direction.append(
                        station_direction["fwdStoppoints"][0]["stoppointName"]
                        )
                    direction.append(
                        station_direction["fwdStoppoints"][-1]["stoppointName"]
                        )
                    if station_direction["bkwdStoppoints"] == []:
                        direction.append(
                            station_direction["fwdStoppoints"][-1]
                            ["stoppointName"]
                            )
                    else:
                        direction.append(
                            station_direction["bkwdStoppoints"][0]
                            ["stoppointName"]
                            )
                        direction.append(
                            station_direction["bkwdStoppoints"][-1]
                            ["stoppointName"]
                            )
        return direction

    # Ищем названия остановок транспорта по его типу
    @staticmethod
    async def choice_station(dict_route):
        station_list = []
        transport = dict_route['TRANSPORT_STATE']
        route_number = dict_route['ROUTES_STATE']
        direction = dict_route['DIRECTION_STATE']
        binding = await Data.binding_id(transport, route_number)
        print(binding)
        for station_direction in FULL_ROUTE_COLLECTION.find(
                    {
                        'routeId': binding
                    }
                ):
            if direction ==\
                    station_direction["fwdStoppoints"][0]["stoppointName"]:
                for station in station_direction["fwdStoppoints"]:
                    station_list.append(station['stoppointName'])
            else:
                for station in station_direction["bkwdStoppoints"]:
                    station_list.append(station['stoppointName'])
        return station_list

    # По типу транспорта и номеру маршрута ищем id маршрута
    @staticmethod
    async def binding_id(transport, route_number):
        transport_type_routes_bus = ROUTE_TYPES_TREE_COLLECTION.find(
            {'children.routeTypeId': 0}
            )
        transport_type_routes_tramway = ROUTE_TYPES_TREE_COLLECTION.find(
            {'children.routeTypeId': 2}
            )
        transport_type_routes_taxi = ROUTE_TYPES_TREE_COLLECTION.find(
            {'children.routeTypeId': 3}
            )
        if transport == BUS:
            for bus_dict in transport_type_routes_bus:
                for id in bus_dict['children']:
                    if id['routeNumber'] == route_number:
                        return id['routeId']
        elif transport == TRAMWAY:
            for tramway_dict in transport_type_routes_tramway:
                for id in tramway_dict['children']:
                    if id['routeNumber'] == route_number:
                        return id['routeId']
        else:
            for taxi_dict in transport_type_routes_taxi:
                for id in taxi_dict['children']:
                    if id['routeNumber'] == route_number:
                        return id['routeId']

    # Получени расписания транспорта на остановке
    @staticmethod
    async def time_sort(number_route):
        try:
            transport = number_route['TRANSPORT_STATE']
            route_number = number_route['ROUTES_STATE']
            direction = number_route['DIRECTION_STATE']
            station = number_route['STATION_STATE']
        except KeyError:
            d_places = PLACES_COLLECTION.find({'_id': number_route['_id']})
            transport = number_route['TRANSPORT_STATE']
            route_number = number_route['ROUTES_STATE']
            direction = number_route['DIRECTION_STATE']
            station = d_places['STATION_STATE']
        route = await Data.binding_id(transport, route_number)
        id = await Data.sort_id_station(direction, station, route)
        time = [i for i in TIME_TRANSPORT.aggregate(
            [
                {'$project': {'_id': 1, 'station': 1}},
                {'$match': {'_id': id}}, {'$unwind': '$station'},
                {'$match': {'station.routeId': f'{route}'}},
                {'$project': {'station.scheduledTime': 1}}
            ])
            ]
        time_list = [j for i in time for j in i['station'].values()]
        str_answer = " ".join(map(str, time_list))
        time_list_answer = re.findall(r'\b\d{2}[:]\d{2}\b', str_answer)
        first_time = time_list_answer[0][0:2]
        new_time = []
        for i in range(len(time_list_answer)):
            if first_time == time_list_answer[i][0:2]:
                new_time.append(f'{time_list_answer[i]} ')
            else:
                first_time = time_list_answer[i][0:2]
                new_time.append('\n')
                new_time.append(f'{time_list_answer[i]} ')
        return "".join(new_time)

    # Ищем id остановки по направлению и названию.
    @staticmethod
    async def sort_id_station(direction, station, route):
        user_direction = ''
        id_station = 0
        list_id_transport = [i for i in FULL_ROUTE_COLLECTION.find(
            {'routeId': f'{route}'}
            )
            ]
        for i in list_id_transport:
            if i['fwdStoppoints'][0]['stoppointName'] == direction:
                user_direction = 'fwdStoppoints'
            else:
                user_direction = 'bkwdStoppoints'
        for j in list_id_transport:
            for k in j[user_direction]:
                if station == k['stoppointName'][:32]:
                    id_station = k['stoppointId']
        return id_station

    @staticmethod
    async def get_station_by_location(location):
        station_location_list = []
        # data_location_station = {}
        latitude = location['latitude']
        longitude = location['longitude']
        station_location_list = [i for i in PLACES_COLLECTION.find(
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
            return station_location_list[0]
        except IndexError:
            return []

    @staticmethod
    async def get_number_route(route_id):
        type_and_number_route = {'Bus': [], 'Tramway': [], 'Taxi': []}
        for id in route_id:
            number = [i for i in DATA_TRANSPORT.find({'_id': str(id)})]
            if number[0]['routeTypeId'] == 0:
                type_and_number_route['Bus'].append(
                    number[0]['routeNumber']
                    )
            elif number[0]['routeTypeId'] == 2:
                type_and_number_route['Tramway'].append(
                    number[0]['routeNumber']
                    )
            else:
                type_and_number_route['Taxi'].append(number[0]['routeNumber'])
        return type_and_number_route

    @staticmethod
    async def get_direction_for_location(
            transport_type, station_id,
            route_number
            ):
        route = await Data.binding_id(transport_type, route_number)
        user_direction = ''
        # id_station = 0
        list_id_transport = [i for i in FULL_ROUTE_COLLECTION.find(
            {'routeId': f'{route}'}
            )]
        for direction in list_id_transport[0]['fwdStoppoints']:
            if int(station_id) == int(direction['stoppointId']):
                user_direction =\
                    list_id_transport[0]['fwdStoppoints'][0]['stoppointName']
        for direction in list_id_transport[0]['bkwdStoppoints']:
            if int(station_id) == int(direction['stoppointId']):
                user_direction =\
                    list_id_transport[0]['bkwdStoppoints'][0]['stoppointName']
        return user_direction

    @staticmethod
    async def get_calldata(user_data):
        stop_id = user_data[0]
        stop_name = PLACES_COLLECTION.find_one(
                {'stop_id': int(stop_id)}
                )
        return stop_name['name']


if __name__ == '__main__':
    async def main():
        # route_id = 59
        message = 'Автобус'
        number_route = await Data.parsing_categories(message)
        print(number_route)

    main()
