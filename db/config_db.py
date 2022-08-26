from pymongo import MongoClient

CLIENT = MongoClient('localhost', 27017)
DB = CLIENT['test']
USER_COLLECTION = DB['user']
ROUTE_TYPES_TREE_COLLECTION = DB['data']
FULL_ROUTE_COLLECTION = DB ['full_route']
TIME_TABLE_COLLECTION = DB ['time_table']
TIME_TABLE_ROUTE_COLLECTION = DB ['time_table_route']
TRANSPORT_ROUTES_BUS_COLLECTION = DB ['transport_routes_bus']
TRANSPORT_ROUTES_TRAMWAY_COLLECTION = DB ['transport_routes_tramway']
TRANSPORT_ROUTES_TAXI_COLLECTION = DB ['transport_routes_taxi']
DATA_TRANSPORT = DB ['data_transport']
TIME_TRANSPORT = DB ['time_transport']
ROUTE_COLLECTION = DB ['route']
TIME_TRANSPORT_OLD = DB ['time_transport_old']