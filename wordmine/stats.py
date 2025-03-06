import asyncio
from pyrogram import Client, filters
from pyrogram.errors import MessageIdInvalid, FloodWait
from pyrogram.types import InputMediaPhoto, Message, InlineKeyboardMarkup, InlineKeyboardButton
from wordmine import app, OWNER_ID  # Ensure OWNER_ID is an integer
from database import get_served_chats, get_served_users

STATS_IMG_URL = "https://files.catbox.moe/0kxtco.jpg"

# **Button Layouts**
def stats_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Overall Stats", callback_data="getstats")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])

def back_stats_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="stats_menu")]
    ])

# **Global Stats**
@app.on_message(filters.command(["stats", "gstats"]) & filters.user(OWNER_ID))
async def stats_global(client, message: Message):
    await message.reply_photo(
        photo=STATS_IMG_URL,
        caption="📊 Global Statistics\n\nClick below to view overall stats!",
        reply_markup=stats_buttons(),
    )

@app.on_callback_query(filters.regex("getstats"))
async def overall_stats(client, CallbackQuery):
    await CallbackQuery.answer()
    
    await CallbackQuery.edit_message_text("📊 Gathering stats, please wait...")

    served_chats = len(get_served_chats())  
    served_users = len(get_served_users())

    text = f"""
📊 Overall Bot Statistics
    
🏠 Total Groups: `{served_chats}`
👥 Total Users: `{served_users}`
    """

    try:
        await CallbackQuery.edit_message_media(
            media=InputMediaPhoto(media=STATS_IMG_URL, caption=text),
            reply_markup=back_stats_buttons()
        )
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=STATS_IMG_URL, caption=text, reply_markup=back_stats_buttons()
        )

@app.on_callback_query(filters.regex("close"))
async def close_stats(client, CallbackQuery):
    await CallbackQuery.message.delete()

@app.on_callback_query(filters.regex("stats_menu"))
async def back_to_stats(client, CallbackQuery):
    await CallbackQuery.answer()
    await CallbackQuery.edit_message_media(
        InputMediaPhoto(
            media=STATS_IMG_URL, 
            caption="📊 Global Statistics\n\nClick below to view overall stats!"
        ),
        reply_markup=stats_buttons()
    )


@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_message(client, message):
    if message.reply_to_message:
        msg_id = message.reply_to_message.id
        chat_id = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("Please provide some text to broadcast.")
        query = message.text.split(None, 1)[1]

    await message.reply_text("Started broadcasting...")

    # **Broadcast to Groups**
    sent, pin = 0, 0
    served_chats = get_served_chats()  # No await here

    for chat in served_chats:
        chat_id = int(chat)  # ✅ Convert Int64 directly to int
        try:
            if message.reply_to_message:
                sent_msg = await app.forward_messages(chat_id, chat_id, msg_id)
            else:
                sent_msg = await app.send_message(chat_id, text=query)

            sent += 1
            if "-pin" in message.text:
                await sent_msg.pin(disable_notification=True)
                pin += 1
            elif "-pinloud" in message.text:
                await sent_msg.pin(disable_notification=False)
                pin += 1

            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue
    
    await message.reply_text(f"Successfully broadcasted message to {sent} chats with {pin} pins.")

    # **Broadcast to Users**
    sent_users = 0
    served_users = get_served_users()  # No await here

    for user in served_users:
        user_id = int(user) # Ensure safe access  # Extract user ID
        try:
            if message.reply_to_message:
                await app.forward_messages(user_id, chat_id, msg_id)
            else:
                await app.send_message(user_id, text=query)

            sent_users += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue
    
    await message.reply_text(f"Successfully broadcasted message to {sent_users} users.")
