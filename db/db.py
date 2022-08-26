import asyncio
import re

from constants import BUS, TRAMWAY, TAXI
from .config_db import ROUTE_TYPES_TREE_COLLECTION, FULL_ROUTE_COLLECTION, TIME_TRANSPORT, ROUTE_COLLECTION


class Data():    

    # Получение списка номеров маршрутов.
    @staticmethod
    async def parsing_categories(message):
        transport_routes = []
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
                    direction.append(station_direction["fwdStoppoints"][0]["stoppointName"])
                    direction.append(station_direction["fwdStoppoints"][-1]["stoppointName"])
                    if station_direction["bkwdStoppoints"] == []:
                        direction.append(station_direction["fwdStoppoints"][-1]["stoppointName"])
                    else:
                        direction.append(station_direction["bkwdStoppoints"][0]["stoppointName"])
                        direction.append(station_direction["bkwdStoppoints"][-1]["stoppointName"])
        return direction

    # Ищем названия остановок транспорта по его типу
    @staticmethod
    async def choice_station(dict_route):
        station_list = []
        transport = dict_route['TRANSPORT_STATE']
        route_number = dict_route['ROUTES_STATE']
        direction = dict_route['DIRECTION_STATE']
        binding = await Data.binding_id(transport, route_number)    
        for station_direction in ROUTE_COLLECTION.find({'routeId': binding}):            
            if direction == station_direction["fwdStoppoints"][0]["stoppointName"]:
                for station in station_direction["fwdStoppoints"]:
                    station_list.append(station['stoppointName'])
            else:
                for station in station_direction["bkwdStoppoints"]:
                    station_list.append(station['stoppointName'])
        return station_list

    # По типу транспорта и номеру маршрута ищем id маршрута
    @staticmethod
    async def binding_id(transport, route_number):
        transport_type_routes_bus = ROUTE_TYPES_TREE_COLLECTION.find({'children.routeTypeId': 0})
        transport_type_routes_tramway = ROUTE_TYPES_TREE_COLLECTION.find({'children.routeTypeId': 2})
        transport_type_routes_taxi = ROUTE_TYPES_TREE_COLLECTION.find({'children.routeTypeId': 3})
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
        transport = number_route['TRANSPORT_STATE']
        route_number = number_route['ROUTES_STATE']
        direction = number_route['DIRECTION_STATE']
        station = number_route['STATION_STATE']
        route = await Data.binding_id(transport, route_number)
        id = await Data.sort_id_station(direction, station, route)
        time = [i for i in TIME_TRANSPORT.aggregate([{'$project': {'_id': 1, 'station': 1}}, {'$match': {'_id': id}}, {'$unwind': '$station'}, \
            {'$match': {'station.routeId': f'{route}'}}, {'$project': {'station.scheduledTime': 1}} ])]
        time_list = [j for i in time for j in i['station'].values()]
        str_answer = " ".join(map(str, time_list))
        time_list_answer = re.findall(r'\b\d{2}[:]\d{2}\b', str_answer)
        first_time = time_list_answer[0][0:2]
        new_time = []
        for i in range(len(time_list_answer)):
            if first_time ==time_list_answer[i][0:2]:
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
        list_id_transport = [i for i in ROUTE_COLLECTION.find({'routeId': f'{route}'})]        
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