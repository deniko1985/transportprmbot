import json
import requests
from datetime import date

from config import path

class Data():
    transport_routes_bus = []
    transport_routes_tramway = []
    transport_routes_taxi = []
    transport_routes = []
    transport_direction = []
    transport_direction_bus = []
    transport_direction_tramway = []
    transport_direction_taxi = []
    dt = date.today()
    date_today = dt.strftime('%d.%m.%Y')
    with open(f'{path}transport_file.json', 'r') as read_file:
        transport_routes_files = json.load(read_file)

    @staticmethod
    def parsing():        
        transport = requests.get(f'http://www.map.gptperm.ru/json/route-types-tree/{Data.date_today}/').json()
        with open(f'{path}transport_file.json', 'w') as write_file:
            json.dump(transport, write_file)

    @staticmethod
    def parsing_categories(message):
        for type_transport in Data.transport_routes_files:    
            for type_routes in type_transport['children']:
                Data.transport_routes.append(type_routes['routeId'])
                Data.transport_direction.append(type_routes['title'])            
                if type_routes['routeTypeId'] == 0:            
                    Data.transport_direction_bus.append(type_routes['title'])
                    Data.transport_routes_bus.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 2:            
                    Data.transport_direction_tramway.append(type_routes['title'])
                    Data.transport_routes_tramway.append(type_routes['routeNumber'])
                elif type_routes['routeTypeId'] == 3:            
                    Data.transport_direction_taxi.append(type_routes['title'])
                    Data.transport_routes_taxi.append(type_routes['routeNumber'])
        if message == 'Автобус':
            return Data.transport_routes_bus
        elif message == 'Трамвай':
            return Data.transport_routes_tramway
        else:
            return Data.transport_routes_taxi

    @staticmethod
    def route_parsing():
        for i in Data.transport_routes:
            transport_station = requests.get(f'http://www.map.gptperm.ru/json/full-route-new/{Data.date_today}/{i}').json()
            with open(f'{path}transport_file-{i}.json', 'w') as write_file:
                json.dump(transport_station, write_file)    
    
    @staticmethod
    def choice_route(message):
        if message == 'Автобус':
            return Data.transport_routes_bus
        elif message == 'Трамвай':
            return Data.transport_routes_tramway
        else:
            return Data.transport_routes_taxi

    @staticmethod
    def choice_direction(number_route):
        direction = []
        transport = number_route['choice_transport']
        route_number = number_route['choice_number']
        binding = Data.binding_id(transport, route_number)
        with open(f'{path}transport_file-{binding}.json', 'r') as read_file:
            transport_direction_files = json.load(read_file)
        direction.append(transport_direction_files["fwdStoppoints"][0]["stoppointName"])
        direction.append(transport_direction_files["fwdStoppoints"][-1]["stoppointName"])
        direction.append(transport_direction_files["bkwdStoppoints"][0]["stoppointName"])
        direction.append(transport_direction_files["bkwdStoppoints"][-1]["stoppointName"])
        return direction

    @staticmethod
    def binding_id(transport, route_number):
        transport_type_routes_bus = Data.transport_routes_files[0]['children']
        transport_type_routes_tramway = Data.transport_routes_files[1]['children']
        transport_type_routes_taxi = Data.transport_routes_files[2]['children']
        if transport == 'Автобус':
            for id in transport_type_routes_bus:
                if id['routeNumber'] == route_number:
                    return id['routeId']                
        elif transport == 'Трамвай':
            for id in transport_type_routes_tramway:
                if id['routeNumber'] == route_number:
                    return id['routeId']                
        else:
            for id in transport_type_routes_taxi:
                if id['routeNumber'] == route_number:
                    return id['routeId']                

if __name__=='__main__':
    number_route = ['taxi', '3т']
    Data.choice_direction(number_route)