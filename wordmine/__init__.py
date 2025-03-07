import os
from pyrogram import *


OWNER_ID = 6058139652

API_ID = int(os.getenv("API_ID", "20222660"))
API_HASH = os.getenv("API_HASH", "5788f1f4a93f2de28835a0cf1b0ebae4")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7560532835:AAHOYKZhGS7rR4vVdQBNWxre0-1GV7SShXQ")

app = Client("word_mine", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)



