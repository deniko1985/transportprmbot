import asyncio

from data import Data    
from config import user_collection, aiogram_state, aiogram_data
from keyboard import BUS, TRAMWAY, TAXI

class Favourites():
    
    @staticmethod
    async def check_user(user_id, chat_id):
        user_clt = user_collection.find()
        id_list = []        
        for cursor in user_collection.find({}, {'_id': 1}):
            print(cursor)
            for i in cursor.values():
                print(i)
                id_list.append(i)
                print(id_list)
        if user_id not in id_list:
            user_collection.insert_one({'_id': user_id, 'chat_id': chat_id, 'bus': [], 'tramway': [], 'taxi': []})
    
    @staticmethod
    async def add_favourites(user_id, user_data):
        transport = user_data['choice_transport']
        route_number = user_data['choice_number']
        id = await Data.binding_id(transport, route_number)
        transport_add = ''
        if transport == BUS:
            transport_add = 'bus'
        elif transport == TRAMWAY:
            transport_add = 'tramway'
        else:
            transport_add = 'taxi'
        user_collection.update_one({'_id': user_id}, {'$addToSet': {transport_add: route_number}})
        return ('Добавлено!')

    @staticmethod
    async def choice_favourites(user_id):
        favourites_list = []
        favourites_bus_list = [BUS, []]
        favourites_tramway_list = [TRAMWAY, []]
        favourites_taxi_list = [TAXI, []]
        print(user_id)
        for favourites_route in user_collection.find({'_id': user_id}):
            if favourites_route.setdefault('bus'):
                favourites_bus_list[1] += favourites_route['bus']                
            if favourites_route.setdefault('tramway'):
                favourites_tramway_list[1] += favourites_route['tramway']               
            if favourites_route.setdefault('taxi'):    
                favourites_taxi_list[1] += favourites_route['taxi']                
        favourites_list.append(favourites_bus_list)
        favourites_list.append(favourites_tramway_list)
        favourites_list.append(favourites_taxi_list)
        return favourites_list

    async def check_favourites(user_id, choice_transport, choice_number):
        list_check_favourites = []
        for favourites_route in user_collection.find({'_id': user_id}):
            if choice_transport == BUS:
                list_check_favourites += favourites_route.get('bus')                   
            elif choice_transport == TRAMWAY:
                list_check_favourites += favourites_route.get('tramway')
            else:
                list_check_favourites += favourites_route.get('taxi')                    
        if choice_number not in list_check_favourites:
            return True