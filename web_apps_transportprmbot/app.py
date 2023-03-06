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


@app.route('/<bot_data>', methods=['GET'])
async def data(bot_data):
    if len(bot_data) < 4:
        coordinates = await is_location(bot_data)
    else:
        location = re.findall(r'\b\d+.\d+\b', bot_data)
        coordinates = ', '.join(map(str, location))
    return await render_template('index.html', coordinates=coordinates)


@app.route('/')
async def index():
    return await render_template('index.html')


async def is_location(id_route):
    coordinates = []
    data = requests.get(f'https://www.map.gortransperm.ru/json/get-moving-autos/{id_route}').json()
    for i in data['autos']:
        coordinates.append(i['n'])
        coordinates.append(i['e'])
        coordinates.append(i['course'])
        print(coordinates)
    return ', '.join(map(str, coordinates))


if __name__ == "__main__":

    app.run(host='0.0.0.0')
#    config = uvicorn.Config("index:index", port=5000, log_level="info")
#    server = uvicorn.Server(config)
#    server.run()
