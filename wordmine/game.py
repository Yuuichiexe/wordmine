import asyncio
import random
import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    update_global_score, update_chat_score, get_global_leaderboard, 
    get_chat_leaderboard, add_served_user, add_served_chat, get_user_points, update_user_points
)
from wordmine import app
from wordmine.challenge import *
from wordmine.cd import challenger_data, fallback_words

group_games = {}

LOGGER_GROUP_ID = -1002358816253  # Replace with your actual Logger Group ID

# Preload word lists for faster local validation
word_lists = {length: set(fallback_words[length]) for length in fallback_words}


async def fetch_word_definition(word):
    """Fetch word definition asynchronously."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    async with aiohttp.ClientSession() as session:  # ✅ Use local session
        try:
            async with session.get(url, timeout=3) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]["meanings"][0]["definitions"][0]["definition"] if data else "No definition available."
        except:
            return "No definition available."


async def is_valid_english_word(word):
    """Check if a word is valid using an external API."""
    url = f"https://api.datamuse.com/words?sp={word}"
    async with aiohttp.ClientSession() as session:  # ✅ Use local session
        try:
            async with session.get(url, timeout=3) as response:
                return response.status == 200
        except:
            return False  # Assume invalid if API request fails
    

def check_guess(guess, word_to_guess):
    """Optimized word checking using dictionary instead of list."""
    feedback = ["🟥"] * len(word_to_guess)
    char_count = {char: word_to_guess.count(char) for char in set(word_to_guess)}

    for i, char in enumerate(guess):
        if char == word_to_guess[i]:
            feedback[i] = "🟩"
            char_count[char] -= 1

    for i, char in enumerate(guess):
        if feedback[i] == "🟥" and char in char_count and char_count[char] > 0:
            feedback[i] = "🟨"
            char_count[char] -= 1

    return "".join(feedback)


@app.on_message(filters.new_chat_members)
async def log_new_group(client, message):
    """Logs bot additions to groups asynchronously."""
    bot_id = (await client.get_me()).id  # Get bot's own user I

    for new_member in message.new_chat_members:
        if new_member.id == bot_id:  # Check if the added user is the bot itself
            chat_id = message.chat.id
            chat_name = message.chat.title or "Unknown Group"
            added_by = message.from_user.id if message.from_user else "Unknown"
            added_by_username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "None"
 
            add_served_chat(chat_id)  # Track the new group in DB

            await client.send_message(
                LOGGER_GROUP_ID,
                f"🆕 **Bot Added to a New Group!**\n📌 **Chat:** {chat_name}\n🆔 **ID:** `{chat_id}\n👤 **Added by User ID:** `{added_by}`\n🔗 **Username:** {added_by_username}"
            )
            break  # Stop further execution if the bot is found


@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Start command with inline buttons."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = message.from_user.mention
    add_served_user(user_id)

    welcome_text = (
        f"<b>Yo, Word miners! {mention} in the house! 🧙‍♂️ Welcome to the ultimate Word Mine Bot showdown!</b>\n\n"
        "<b>🕹️ How to Play:</b>\n"
        "<u><i>- Start a new game using</u> /new</i>\n"
        "<u><i>- Choose a word length</i></u>\n"
        "<u><i>- Guess the word and get results with 🟩🟨🟥</i></u>\n"
        "<u><i>- Score points and climb the leaderboard!</i></u>\n\n"
        "<i>Ready to crush your friends? Bring the battle to your group! ⚔️ Add me and let the word wars begin!</i>"
    )
    
    bot_info = await client.get_me()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_info.username}?startgroup=true")],
        [InlineKeyboardButton("⚙️ Commands", callback_data="commands"),
         InlineKeyboardButton("🛡 Support", url="https://t.me/WordMiners")]
    ])

    await message.reply_photo(
        photo="https://files.catbox.moe/3qhaq0.jpg",
        caption=welcome_text,
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("^commands$"))
async def show_commands(client, callback_query):
    commands_text = (
        "**Word Mine Bot Help**\n\n"
        "🎮 **Commands:**\n"
        "- /start - Start the bot and see the welcome message\n"
        "- /new - Start a new word guessing game\n"
        "- /end - End the current game\n"
        "- /leaderboard - View the global leaderboard\n"
        "- /chatleaderboard - View the chat leaderboard\n"
        "- /help - Show this help message\n"
    )
    
    await callback_query.message.edit_text(commands_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]))


@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start(client, callback_query):
    await callback_query.message.delete()  # Delete the previous message
    await start_command(client, callback_query.message)  # Send a new start message


@app.on_message(filters.command("new"))
async def start_new_game(client, message):
    """New game selection with inline buttons."""
    user_id = message.from_user.id
    chat_name = message.chat.title or "Unknown Group"
    buttons = [[InlineKeyboardButton(f"{i} Letters", callback_data=f"new_length_{i}_{user_id}")] for i in range(4, 8)]
    await message.reply("📌 **Select a word length:**", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^new_length_"))
async def select_new_game_length(client, callback_query):
    """Starts a game with chosen word length."""
    data = callback_query.data.split("_")
    chat_name = callback_query.message.chat.title or "Unknown Group"
    word_length, user_id, chat_id = int(data[2]), int(data[3]), callback_query.message.chat.id

    if user_id != callback_query.from_user.id:
        await callback_query.answer("⚠️ This is not your game!", show_alert=True)
        return

    word = random.choice(list(word_lists[word_length]))
    group_games[chat_id] = {
    "word": word,
    "used_words": set(),
    "history": []
    }

    print(f"DEBUG: Game started in chat {chat_name} with word {word}")
    asyncio.create_task(client.send_message(
        LOGGER_GROUP_ID,
        f"**New Game Event**\n\nGame started in chat - \n```{chat_name}```\n\nWith the word - \n```{word}```",
        parse_mode=ParseMode.MARKDOWN
    ))

    
    await callback_query.message.edit_text(f"**New Game Started!** ✅\n🛡 **Word Length:** `{word_length}`\n🤔 Start guessing!")

@app.on_message(filters.text & ~filters.command(["new", "leaderboard", "chatleaderboard", "end", "help", "challenge", "start"]))
async def process_guess(client, message):
    """Handles word guessing with group games first, then challenge mode."""
    chat_id, user_id, text = message.chat.id, message.from_user.id, message.text.strip().lower()
    mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"

    # Check if there's an active group game
    if chat_id in group_games:
        word_to_guess = group_games[chat_id]["word"]

        if len(text) != len(word_to_guess):
            return

        if text in group_games[chat_id]["used_words"]:
            await message.reply(f"🔄 {mention}, you already used this word! Try a different one.")
            return

        is_valid = await is_valid_english_word(text)
        if not is_valid:
            await message.reply("⚠️ Not a valid English word!")
            return

        feedback = check_guess(text, word_to_guess)
        group_games[chat_id]["used_words"].add(text)
        group_games[chat_id]["history"].append(f"{feedback} → {text.upper()}")
        guess_history = "\n".join(group_games[chat_id]["history"])

        await message.reply(guess_history)

        if text == word_to_guess:
            update_chat_score(chat_id, user_id)
            update_global_score(user_id)

            leaderboard = get_global_leaderboard()
            user_score = next((score for uid, score in leaderboard if uid == user_id), 0)
            user_rank = next((i + 1 for i, (uid, _) in enumerate(leaderboard) if uid == user_id), "Unranked")

            del group_games[chat_id]

            definition = await fetch_word_definition(word_to_guess)

            await message.reply(
                f"🎉 Congratulations {mention}! 🎉\n"
                f"🔖 Correct guess! it was {word_to_guess.upper()}\n"
                f"🏆 You earned 1 point!\n"
                f"📊 Your total score: {user_score}\n"
                f"🌍 Your global rank: #{user_rank}\n"
                f"📖 Definition of the word:\n"
                f"```\n{definition}```\n\n",
                parse_mode=ParseMode.MARKDOWN
            )
        return

    # If no group game, check challenge mode
    for challenger_id, game_data in list(challenger_data.items()):
        if user_id in [challenger_id, game_data["opponent_id"]]:
            word, bet_amount = game_data["word"], game_data["bet_amount"]

            if len(text) != len(word):
                return

            feedback = check_guess(text, word)
            await message.reply(f"{feedback} → {text.upper()}")

            if text == word:
                winner_id = user_id
                winnings = bet_amount * 2
                update_user_points(winner_id, chat_id, winnings)
                total_points = get_user_points(winner_id)

                del challenger_data[challenger_id]

                definition = await fetch_word_definition(word)

                await message.reply(
                    f"🎉 Congratulations, {mention}! 🎉\n"
                    f"🏆 Correct guess! it was **{word.upper()}**\n"
                    f"💰 You won **{winnings} points**!\n"
                    f"🔥 Your new total: **{total_points} points**!\n"
                    f"📖 Definition of the word:\n"
                    f"```\n{definition}```\n\n",
                    parse_mode=ParseMode.MARKDOWN
                )
            return


@app.on_message(filters.command("leaderboard"))
async def leaderboard(client: Client, message: Message):
    leaderboard = get_global_leaderboard()
    if not leaderboard or not isinstance(leaderboard, list):
        await message.reply("No scores recorded yet.")
        return
    
    
    leaderboard_text = "🌍 **Global Leaderboard:**\n\n"
    
    for rank, (user_id, score) in enumerate(leaderboard, start=1):
        try:
            user = await client.get_users(user_id)  # Fetch user info
            mention = f"[{user.first_name}](tg://user?id={user.id})"
        except Exception:  # Handle unknown users
            mention = f"User {user_id}"

        leaderboard_text += f"🏅 **#{rank}** - {mention} → **{score} POINTS**\n"
    
    await message.reply(leaderboard_text)



@app.on_message(filters.command("chatleaderboard"))
async def chat_leaderboard(client: Client, message: Message):
    leaderboard = get_chat_leaderboard(message.chat.id)

    if not leaderboard or not isinstance(leaderboard, list):
        await message.reply("No scores recorded yet.")
        return

    leaderboard_text = "🏆 **Chat Leaderboard:**\n\n"

    for rank, entry in enumerate(leaderboard, start=1):
        user_id = entry.get("user_id")  # ✅ Fix unpacking issue
        score = entry.get("score", 0)

        try:
            user = await client.get_users(user_id)  # Fetch user info
            mention = f"[{user.first_name}](tg://user?id={user.id})"
        except Exception:  # Handle unknown users
            mention = f"User {user_id}"

        leaderboard_text += f"🏅 **#{rank}** - {mention} → **{score} POINTS**\n"

    await message.reply(leaderboard_text)
    

@app.on_message(filters.command("end"))
async def end_game(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in group_games:
        del group_games[chat_id]
        await message.reply("🚫 The game has been ended. Start a new one with /new!")
    else:
        await message.reply("⚠️ No active game to end.")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "**Word Mine Bot Help**\n\n"
        "🎮 **Commands:**\n"
        "- /start - Start the bot and see the welcome message\n"
        "- /new - Start a new word guessing game\n"
        "- /end - End the current game\n"
        "- /leaderboard - View the global leaderboard\n"
        "- /chatleaderboard - View the chat leaderboard\n"
        "- /help - Show this help message\n"
        
    )
    await message.reply(help_text)
