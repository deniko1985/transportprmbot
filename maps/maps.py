import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

class Maps():
    
    async def choice_maps(user_id):
        return ('Пока не умею.')