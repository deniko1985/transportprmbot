import asyncio
import json
import requests
from quart import Quart, render_template, websocket, request
from werkzeug.exceptions import abort

from markupsafe import escape

from hypercorn.config import Config
from hypercorn.asyncio import serve

import uvicorn

app = Quart(__name__)

@app.route('/<id_route>', methods = ['GET'])
async def data(id_route):
    coordinates = await is_location(id_route)
    return await render_template('index.html', coordinates=coordinates)

@app.route('/')
async def index():
    return await render_template('index.html')

async def is_location(id_route):
    coordinates = []
    data = requests.get(f'http://www.map.gptperm.ru/json/get-moving-autos/{id_route}').json()
    for i in data['autos']:
        coordinates.append(i['n'])
        coordinates.append(i['e'])
    return ', '.join(map(str, coordinates))

if __name__ == "__main__":
   app.run() 
#    config = uvicorn.Config("index:index", port=5000, log_level="info")
#    server = uvicorn.Server(config)
#    server.run()