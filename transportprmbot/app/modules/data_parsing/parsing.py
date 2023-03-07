from datetime import date
import re
import requests

from pymongo import MongoClient

# from db.config_db import ROUTE_TYPES_TREE_COLLECTION,\
#    TIME_TABLE_COLLECTION, FULL_ROUTE_COLLECTION,\
#    TIME_TRANSPORT, PLACES_COLLECTION, PLACES_COLLECTION_TEST, \
#    DATA_TRANSPORT

dt = date.today()
date_today = dt.strftime('%d.%m.%Y')
id_station_list = []
route = []


CLIENT = MongoClient('localhost', 28017)
DB = CLIENT['transportprmbot']
USER_COLLECTION = DB['user']
ROUTE_TYPES_TREE_COLLECTION = DB['data']
FULL_ROUTE_COLLECTION = DB['full_route']
TIME_TABLE_COLLECTION = DB['time_table']
TIME_TABLE_ROUTE_COLLECTION = DB['time_table_route']
TRANSPORT_ROUTES_BUS_COLLECTION = DB['transport_routes_bus']
TRANSPORT_ROUTES_TRAMWAY_COLLECTION = DB['transport_routes_tramway']
TRANSPORT_ROUTES_TAXI_COLLECTION = DB['transport_routes_taxi']
DATA_TRANSPORT = DB['data_transport']
TIME_TRANSPORT = DB['time_transport']
ROUTE_COLLECTION = DB['route']
TIME_TRANSPORT_OLD = DB['time_transport_old']
PLACES_COLLECTION = DB['places']
PLACES_COLLECTION_TEST = DB['places_test']


# Получение всех типов маршрутов
# (id маршрута, вид транспорта, маршрут движения)
def route_types_tree():    
    ROUTE_TYPES_TREE_COLLECTION.delete_many({})
    data = requests.get(
        f'https://www.map.gortransperm.ru/json/route-types-tree/{date_today}/'
        ).json()
    ROUTE_TYPES_TREE_COLLECTION.insert_many(data)
    print('Успех! route_types_tree')
    return 'Успех! route_types_tree'


# Получение всех данных маршрутов
# (по id маршрута получаем данные по остановкам (id остановок, название))
def full_route():
    FULL_ROUTE_COLLECTION.delete_many({})
    route = []
    # collection = FULL_ROUTE_COLLECTION.find()
    collection = ROUTE_TYPES_TREE_COLLECTION.find()
    # global route
    for i in collection:
        for j in i['children']:
            route.append(j['routeId'])
    print(route)
    for i in route:
        data = requests.get(
            f'https://www.map.gortransperm.ru/json/full-route-new/\
            {date_today}/{i}'
            ).json()
        # route_list.append(data)
        FULL_ROUTE_COLLECTION.insert_one(data)
    print('Успех full_route')
    return 'Успех! route_types_tree'


# Получение данных по конкретной остановке
# (какой транспорт и маршрут останавливается на данной остановке, расписание)
def time_table():
    id_station = set()
    TIME_TABLE_COLLECTION.delete_many({})
    collection = FULL_ROUTE_COLLECTION.find()
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
        data = requests.get(
            f'https://www.map.gortransperm.ru/json/stoppoint-time-table/\
            {date_today}/{i}'
            ).json()
        TIME_TABLE_COLLECTION.insert_many(data)
    print('Успех! time_table')
    return 'Успех! route_types_tree'


def sort_type_transport():
    TRANSPORT_ROUTES_BUS_COLLECTION.delete_many({})
    TRANSPORT_ROUTES_TRAMWAY_COLLECTION.delete_many({})
    TRANSPORT_ROUTES_TAXI_COLLECTION.delete_many({})
    data_bus = []
    data_tramway = []
    data_taxi = []
    for type_transport in ROUTE_TYPES_TREE_COLLECTION.find():
        for type_routes in type_transport['children']:
            if type_routes['routeTypeId'] == 0:
                data_bus.append(type_routes['routeId'])
            elif type_routes['routeTypeId'] == 2:
                data_tramway.append(type_routes['routeId'])
            elif type_routes['routeTypeId'] == 3:
                data_taxi.append(type_routes['routeId'])
    TRANSPORT_ROUTES_BUS_COLLECTION.insert_one({'routeId': data_bus})
    TRANSPORT_ROUTES_TRAMWAY_COLLECTION.insert_one({'routeId': data_tramway})
    TRANSPORT_ROUTES_TAXI_COLLECTION.insert_one({'routeId': data_taxi})
    return 'Успех! route_types_tree'


def data_transport_sort():
    DATA_TRANSPORT.delete_many({})
    data_number = [i for i in FULL_ROUTE_COLLECTION.find(
        {}, {
                '_id': 0, 'routeId': 0, 'fwdStoppoints.note': 0,
                'fwdStoppoints.course': 0, 'fwdStoppoints.labelXOffset': 0,
                'fwdStoppoints.labelYOffset': 0, 'bkwdStoppoints.note': 0,
                'bkwdStoppoints.course': 0, 'bkwdStoppoints.labelXOffset': 0,
                'bkwdStoppoints.labelYOffset': 0, 'twoStoppoints': 0,
                'threeStoppoints': 0,
                'fourStoppoints': 0, 'fiveStoppoints': 0, 'fwdTrackGeom': 0,
                'bkwdTrackGeom': 0, 'twoTrackGeom': 0, 'threeTrackGeom': 0,
                'fourTrackGeom': 0, 'fiveTrackGeom': 0
            }
        )]
    number_list = []
    route_number = []
    route_type_id = []
    j = 0
    for number in ROUTE_TYPES_TREE_COLLECTION.find():
        for i in number['children']:
            number_list.append(i['routeId'])
            route_number.append(i['routeNumber'])
            route_type_id.append(i['routeTypeId'])
    for i in range(len(number_list)):
        id = number_list[i]
        k = route_number[i]
        j = route_type_id[i]
        d = data_number[i]
        DATA_TRANSPORT.insert_one(
            {
                '_id': id, 'routeNumber': k, 'routeTypeId': j, 'station': d
            }
            )
    print('Успех!')
    return 'Успех! route_types_tree'


# Получение расписания определенного маршрута на конкретной остановке
def aggregate_collection():
    id_station = set()
    collection = FULL_ROUTE_COLLECTION.find()
    for i in collection:
        for j in i['fwdStoppoints']:
            id_station.add(j['stoppointId'])
        for j in i['bkwdStoppoints']:
            id_station.add(j['stoppointId'])
    global id_station_list
    id_station_list = list(id_station)
    id_station_list.sort()
    print(len(id_station_list))
    TIME_TRANSPORT.delete_many({})
    for i in range(len(id_station_list)):
        id = id_station_list[i]
        time = [i for i in TIME_TABLE_COLLECTION.aggregate(
            [
                {
                    '$project':
                        {
                            '_id': 0,
                            'stoppointId': 1,
                            'scheduledTime': 1,
                            'routeId': 1,
                            'routeNumber': 1,
                            'routeName': 1
                        }
                },
                {
                    '$match': {'stoppointId': id}
                }
            ]
            )]
        TIME_TRANSPORT.insert_one({'_id': id, 'station': time})
    return 'Успех! route_types_tree'


def geo():
    PLACES_COLLECTION.delete_many({})
    collection = DATA_TRANSPORT.find()
    list_common = []
    # print(collection)
    for i in collection:
        # print(i)
        for j in i['station']['fwdStoppoints']:
            list_common.append(j['stoppointId'])
        for k in i['station']['bkwdStoppoints']:
            list_common.append(k['stoppointId'])
    set_common = set(list_common)
    list_common = list(set_common)
    list_common.sort()
    stoppoint_name = ''
    for j in list_common:
        # geo_dict = {}
        route_id_list = []
        temp_dict = {}
        location = []
        list_forward = [i for i in FULL_ROUTE_COLLECTION.aggregate(
            [
                {
                    '$project':
                        {
                            '_id': 0,
                            'fwdStoppoints': 1,
                            'routeId': 1
                        }
                },
                {'$unwind': '$fwdStoppoints'},
                {'$match': {'fwdStoppoints.stoppointId': j}},
                {
                    '$project':
                        {
                            'routeId': 1,
                            'fwdStoppoints.stoppointName': 1,
                            'fwdStoppoints.location': 1
                        }
                }
            ]
            )]
        list_backward = [i for i in FULL_ROUTE_COLLECTION.aggregate(
                [
                    {
                        '$project':
                            {
                                '_id': 0,
                                'bkwdStoppoints': 1,
                                'routeId': 1
                            }
                    },
                    {'$unwind': '$bkwdStoppoints'},
                    {'$match': {'bkwdStoppoints.stoppointId': j}},
                    {
                        '$project':
                            {
                                'routeId': 1,
                                'bkwdStoppoints.stoppointName': 1,
                                'bkwdStoppoints.location': 1
                            }
                    }
                ]
            )]
        list_forward += list_backward
        # print(list_forward)
        for i in list_forward:
            # print(i)
            route_id_list.append(str(i['routeId']))
            if i.get('fwdStoppoints'):
                temp_dict.update(i['fwdStoppoints'])
            else:
                temp_dict.update(i['bkwdStoppoints'])
            stoppoint_name = temp_dict['stoppointName']
            location_temp = temp_dict['location']
            location_temp = re.findall(
                r'(?:([\d.]+)) (?:([\d.]+))', location_temp
                )
            location.append(float(location_temp[0][0]))
            location.append(float(location_temp[0][1]))
            location = list(set(location))
        PLACES_COLLECTION.insert_one(
            {
                '_id': j,
                'stop_id': j,
                'name': stoppoint_name,
                'route_id': route_id_list,
                'location':
                    {
                        'type': 'Point',
                        'coordinates': location
                    }
            }
        )
    return 'Успех! route_types_tree'


def create_index():
    PLACES_COLLECTION.create_index([("location", "2dsphere")])
    return 'Успех! route_types_tree'


def geo_station():
    collection = PLACES_COLLECTION.find(
        {}, {'fwdStoppoints.stoppointId': 1, 'bkwdStoppoints.stoppointId': 1}
        )
    list_common = []
    for i in collection:
        for j in i['fwdStoppoints']:
            list_common.append(j['stoppointId'])
        for k in i['bkwdStoppoints']:
            list_common.append(k['stoppointId'])
    set_common = set(list_common)
    list_common = list(set_common)
    list_common.sort()
    for j in list_common:
        # geo_dict = {}
        route_id_list = []
        temp_dict = {}
        location = []
        list_forward = [i for i in PLACES_COLLECTION.aggregate(
            [
                {
                    '$project':
                        {
                            '_id': 0,
                            'fwdStoppoints': 1,
                            'routeId': 1
                        }
                },
                {'$unwind': '$fwdStoppoints'},
                {'$match': {'fwdStoppoints.stoppointId': j}},
                {
                    '$project':
                        {
                            'routeId': 1,
                            'fwdStoppoints.stoppointName': 1,
                            'fwdStoppoints.location': 1
                        }
                }
            ]
            )]
        list_backward = [i for i in PLACES_COLLECTION.aggregate(
            [
                {
                    '$project':
                        {
                            '_id': 0,
                            'bkwdStoppoints': 1,
                            'routeId': 1
                        }
                },
                {'$unwind': '$bkwdStoppoints'},
                {'$match': {'bkwdStoppoints.stoppointId': j}},
                {
                    '$project':
                        {
                            'routeId': 1,
                            'bkwdStoppoints.stoppointName': 1,
                            'bkwdStoppoints.location': 1
                        }
                }
            ]
            )]
        list_forward += list_backward
        for i in list_forward:
            route_id_list.append(str(i['routeId']))
            if i.get('fwdStoppoints'):
                temp_dict.update(i['fwdStoppoints'])
            else:
                temp_dict.update(i['bkwdStoppoints'])
            stoppoint_name = temp_dict['stoppointName']
            location_temp = temp_dict['location']
            location_temp = re.findall(
                r'(?:([\d.]+)) (?:([\d.]+))', location_temp
                )
            location.append(float(location_temp[0][0]))
            location.append(float(location_temp[0][1]))
            location = list(set(location))
        PLACES_COLLECTION_TEST.insert_one(
            {
                '_id': j,
                'stop_id': j,
                'name': stoppoint_name,
                'route_id': route_id_list,
                'location': {'type': 'Point', 'coordinates': location}
            }
            )
    return 'Успех! route_types_tree'


def main():
    res = route_types_tree()
    if res:
        res = full_route()
        if res:
            res = time_table()
        else:
            print('None!')
            if res:
                res = sort_type_transport()
            else:
                print('None!')
                if res:
                    res = data_transport_sort()
                else:
                    print('None!')
                    if res:
                        res = aggregate_collection()
                    else:
                        print('None!')
                        if res:
                            res = geo()
                        else:
                            print('None!')
                            if res:
                                res = create_index()
                            else:
                                print('None!')
                                if res:
                                    geo_station()
                                else:
                                    print('None!')
    else:
        print('None!')


if __name__ == '__main__':
    main()
    # route_types_tree()
    # full_route()
    # time_table()
    # sort_type_transport()
    # data_transport_sort()
    # time_table_route()
    # time_table_route_last()
    # time_table_route_bus()
    # list_comprehensions()
    # sort_type_route_id()
    # aggregate_collection()
    # geo()
    # geo_station()
