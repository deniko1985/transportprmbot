import asyncio
import json
import re
import requests
from quart import Quart, render_template, websocket, request
from werkzeug.exceptions import abort

from markupsafe import escape

from hypercorn.config import Config
from hypercorn.asyncio import serve

import uvicorn

app = Quart(__name__)


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/routes/<route_id>', methods=['GET'])
async def data(route_id):
    coordinates = await is_location(route_id)
    return await render_template('routes.html', coordinates=coordinates)


@app.route('/geo_station/<geo_data>', methods=['GET'])
async def get_geo_station(geo_data):
    location = re.findall(r'\b\d+.\d+\b', geo_data)
    coordinates = ', '.join(map(str, location))
    return await render_template('geo_station.html', coordinates=coordinates)


async def is_location(id_route):
    coordinates = []
    data = requests.get(f'https://www.map.gortransperm.ru/json/get-moving-autos/{id_route}').json()
    for i in data['autos']:
        coordinate = []
        coordinate.append(i['n'])
        coordinate.append(i['e'])
        coordinate.append(i['course'])
        coordinates.append(coordinate)
    # return ', '.join(map(str, coordinates))
    return coordinates


if __name__ == "__main__":

    app.run(host='0.0.0.0')
#    config = uvicorn.Config("index:index", port=5000, log_level="info")
#    server = uvicorn.Server(config)
#    server.run()
