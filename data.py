import asyncio
import re

from config import route_types_tree_collection, full_route_collection, \
    time_table_collection, time_table_route_collection, \
        transport_routes_bus_collection, transport_routes_tramway_collection, \
            transport_routes_taxi_collection, data_transport, time_transport, route_collection, \
                user_collection, aiogram_state, aiogram_data

class Data():    

    # Получение списка номеров маршрутов.
    @staticmethod
    async def parsing_categories(message):
        transport_routes = []
        transport_routes_bus = []
        transport_routes_tramway = []
        transport_routes_taxi = []
        for type_transport in route_types_tree_collection.find():    
            for type_routes in type_transport['children']:  
                if type_routes['routeTypeId'] == 0:            
                    transport_routes_bus.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 2:            
                    transport_routes_tramway.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 3:            
                    transport_routes_taxi.append(type_routes['routeNumber'])
        if message == 'Автобус':
            return transport_routes_bus
        elif message == 'Трамвай':
            return transport_routes_tramway
        else:
            return transport_routes_taxi

    # Получаем данные о направлении движения
    @staticmethod
    async def choice_direction(number_route):
        direction = []
        transport = number_route['choice_transport']
        route_number = number_route['choice_number']
        binding = await Data.binding_id(transport, route_number)        
        for station_direction in full_route_collection.find():
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
    async def choice_station(number_route):
        station_list = []
        transport = number_route['choice_transport']
        route_number = number_route['choice_number']
        direction = number_route['user_direction']
        binding = await Data.binding_id(transport, route_number)    
        for station_direction in route_collection.find({'routeId': binding}):            
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
        transport_type_routes_bus = route_types_tree_collection.find({'children.routeTypeId': 0})
        transport_type_routes_tramway = route_types_tree_collection.find({'children.routeTypeId': 2})
        transport_type_routes_taxi = route_types_tree_collection.find({'children.routeTypeId': 3})
        if transport == 'Автобус':
            for bus_dict in transport_type_routes_bus:
                for id in bus_dict['children']:
                    if id['routeNumber'] == route_number:                        
                        return id['routeId']                
        elif transport == 'Трамвай':
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
        transport = number_route['choice_transport']
        route_number = number_route['choice_number']
        direction = number_route['user_direction']
        station = number_route['user_station']
        route = await Data.binding_id(transport, route_number)
        id = await Data.sort_id_station(direction, station, route)
        time = [i for i in time_transport.aggregate([{'$project': {'_id': 1, 'station': 1}}, {'$match': {'_id': id}}, {'$unwind': '$station'}, \
            {'$match': {'station.routeId': f'{route}'}}, {'$project': {'station.scheduledTime': 1}} ])]
        time_list = [j for i in time for j in i['station'].values()]
        str_answer = " ".join(map(str, time_list))
        time_list_answer = re.findall(r'\b\d{2}[:]\d{2}\b', str_answer)
        return " ".join(map(str, time_list_answer))

    # Ищем id остановки по направлению и названию.
    @staticmethod
    async def sort_id_station(direction, station, route):
        user_direction = ''
        id_station = 0
        list_id_transport = [i for i in route_collection.find({'routeId': f'{route}'})]        
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

if __name__=='__main__':
#    number_route = {'choice_transport': 'Трамвай', 'choice_number': '12', 'choice_schedule': 'Расписание', 'user_direction': 'Школа №107', 'user_station': 'Разгуляй'}
    number_route ={'choice_transport': 'Автобус', 'choice_number': '14', 'choice_schedule': 'Расписание', 'user_direction': 'Микрорайон Юбилейный', 'user_station': 'Микрорайон Юбилейный', 'user_time': 'yes'}
#    number_route_1 = {'choice_transport': 'Трамвай', 'choice_number': '5', 'choice_schedule': 'Раписание', 'choice_station': 'Станция Бахаревка'}
#    Data.parsing_categories('Машрутное такси')
#    Data.binding_id('Трамвай', '11')
    Data.choice_direction(number_route)
#    Data.choice_station(number_route)
#    print(Data.transport_direction_bus)
#    print(Data.time_sort(number_route))
#    Data.sort_id_station('Школа №107', 'Разгуляй', 812)
#    Data.add_favourites(number_route)
#    Data.choice_favourites()