import os

import requests
from datetime import date

from config import route_types_tree_collection, full_route_collection, \
    time_table_collection, time_table_route_collection, \
    transport_routes_bus_collection, transport_routes_tramway_collection, \
    transport_routes_taxi_collection, data_transport, time_transport

dt = date.today()
date_today = dt.strftime('%d.%m.%Y')
id_station_list = []
route = []

# Получение всех типов маршрутов (id маршрута, вид транспорта, маршрут движения)
def route_types_tree():
    route_types_tree_collection.delete_many({})
    data = requests.get(f'http://www.map.gptperm.ru/json/route-types-tree/{date_today}/').json()
    route_types_tree_collection.insert_many(data)
    print('Успех! route_types_tree')    

# Получение всех данных маршрутов (по id маршрута получаем данные по остановкам (id остановок, название))
def full_route():
    full_route_collection.delete_many({})        
    route_list = []
    collection = route_types_tree_collection.find()
    global route
    for i in collection:
        for j in i['children']:
            route.append(j['routeId'])    
    for i in route:
        data = requests.get(f'http://www.map.gptperm.ru/json/full-route-new/{date_today}/{i}').json()
        route_list.append(data)
    full_route_collection.insert_many(route_list)
    print('Успех full_route')

# Получение данных по конкретной остановке (какой транспорт и маршрут останавливается на данной остановке, расписание)
def time_table():
    id_station = set()
    time_table_collection.delete_many({})
    collection = full_route_collection.find()
    for i in collection:        
        for j in i['fwdStoppoints']:            
            id_station.add(j['stoppointId'])
        for j in i['bkwdStoppoints']:
            id_station.add(j['stoppointId'])
    global id_station_list
    id_station_list = list(id_station)
    id_station_list.sort()
    print(len(id_station_list))
    for i in id_station_list:        
        data = requests.get(f'http://www.map.gptperm.ru/json/stoppoint-time-table/{date_today}/{i}').json()
        time_table_collection.insert_many(data)
    print('Успех! time_table')

def sort_type_transport():
    data_bus = []
    data_bus_stop = []
    data_tramway = []
    data_tramway_stop = []
    data_taxi = []
    data_taxi_stop = []
    for type_transport in route_types_tree_collection.find():    
        for type_routes in type_transport['children']:
            if type_routes['routeTypeId'] == 0:
                data_bus.append(type_routes['routeId'])               
            elif type_routes['routeTypeId'] == 2:
                data_tramway.append(type_routes['routeId'])
            elif type_routes['routeTypeId'] == 3:
                data_taxi.append(type_routes['routeId'])
    #transport_routes_bus_collection.insert_one({'routeId': data_bus})
    #transport_routes_tramway_collection.insert_one({'routeId': data_tramway})
    #transport_routes_taxi_collection.insert_one({'routeId': data_taxi})

def sort_type_route_id():
    collection = {i['fwdStoppoints'] for i in full_route_collection.find()}
    data_bus = []
    data_bus_stop = []
    data_tramway = []
    data_tramway_stop = []
    data_taxi = []
    data_taxi_stop = []
    bus = [i['routeId'] for i in transport_routes_bus_collection.find()]
    tramway = [i['routeId'] for i in transport_routes_tramway_collection.find()]
    taxi = [i['routeId'] for i in transport_routes_taxi_collection.find()]
        
def data_transport_sort():
    data_transport.delete_many({})
    data = [i['children'] for i in route_types_tree_collection.find({}, {'_id': 0, 'children.routeNumber': 1, 'children.routeTypeId': 1})]
    data_number = [i for i in full_route_collection.find({}, {'_id': 0, 'routeId': 0, 'fwdStoppoints.note': 0,\
        'fwdStoppoints.course': 0, 'fwdStoppoints.labelXOffset': 0, 'fwdStoppoints.labelYOffset': 0, 'bkwdStoppoints.note': 0,\
        'bkwdStoppoints.course': 0, 'bkwdStoppoints.labelXOffset': 0, 'bkwdStoppoints.labelYOffset': 0, 'twoStoppoints': 0, 'threeStoppoints': 0, \
            'fourStoppoints': 0, 'fiveStoppoints': 0, 'fwdTrackGeom': 0, 'bkwdTrackGeom': 0, 'twoTrackGeom': 0, 'threeTrackGeom': 0, 'fourTrackGeom': 0, 'fiveTrackGeom': 0})]
    number_list = []
    route_number = []
    route_type_id = []
    j = 0
    for number in route_types_tree_collection.find():
        for i in number['children']:                    
            number_list.append(i['routeId']) 
            route_number.append(i['routeNumber']) 
            route_type_id.append(i['routeTypeId']) 
    for i in range(len(number_list)): 
        id = number_list[i]    
        k = route_number[i]
        j = route_type_id[i]
        d = data_number[i]
        data_transport.insert_one({'_id': id, 'routeNumber': k, 'routeTypeId': j, 'station': d})
    print('Успех!')

# Получение расписания определенного маршрута на конкретной остановке
def aggregate_collection():
    id_station = set()
    collection = full_route_collection.find()
    for i in collection:        
        for j in i['fwdStoppoints']:            
            id_station.add(j['stoppointId'])
        for j in i['bkwdStoppoints']:
            id_station.add(j['stoppointId'])
    global id_station_list
    id_station_list = list(id_station)
    id_station_list.sort()
    print(len(id_station_list))
    time_transport.delete_many({})
    for i in range(len(id_station_list)):
        id = id_station_list[i]
        time = [i for i in time_table_collection.aggregate([{'$project': {'_id': 0, 'stoppointId': 1, 'scheduledTime': 1, 'routeId': 1, 'routeNumber': 1, \
        'routeName': 1}}, {'$match': {'stoppointId': id}}])]
        time_transport.insert_one({'_id': id, 'station': time})

if __name__=='__main__':
#    route_types_tree()
#    full_route()
#    time_table()
#    sort_type_transport()
#    time_table_route()
#    time_table_route_last()
#    time_table_route_bus()
#    list_comprehensions()
    sort_type_route_id()