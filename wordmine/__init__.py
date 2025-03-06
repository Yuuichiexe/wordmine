import os
from pyrogram import Client


OWNER_ID = 6058139652

API_ID = int(os.getenv("API_ID", "20222660"))
API_HASH = os.getenv("API_HASH", "5788f1f4a93f2de28835a0cf1b0ebae4")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6694970760:AAGe7pAorvORM7xRb-9AyOpdoEfNJMd6Ric")

app = Client("wordmine", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, parse_mode="MarkdownV2")
