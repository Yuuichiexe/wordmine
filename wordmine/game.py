import random
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database import update_global_score, update_chat_score, get_global_leaderboard, get_chat_leaderboard, add_served_user, add_served_chat
from wordmine import app
from wordmine.challenge import *
from wordmine.cd import challenger_data
# Fallback words in case the API fails
fallback_words = {
    4: ["play", "word", "game", "chat"],
    5: ["guess", "brain", "smart", "think"],
    6: ["random", "puzzle", "letter", "breeze"],
    7: ["amazing", "thought", "journey", "fantasy"]
}


LOGGER_GROUP_ID = -1002267039087 # 🔹 Replace with your actual Logger Group ID



def fetch_words(word_length, max_words=40):
    try:
        response = requests.get(
            f"https://api.datamuse.com/words?sp={'?' * word_length}&max=40",
            timeout=5
        )
        response.raise_for_status()
        words = [word["word"] for word in response.json()]

        # Filter words that have definitions
        valid_words = []
        for word in words:
            definition = fetch_word_definition(word)
            if definition and definition != "No definition available.":
                valid_words.append(word)
        
        return valid_words if valid_words else fallback_words[word_length]
    except requests.RequestException:
        return fallback_words[word_length]

def fetch_word_definition(word):
    """Fetch the definition of the word using the Datamuse API."""
    try:
        response = requests.get(f"https://api.datamuse.com/words?ml={word}", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0].get('defs', ['No definition available.'])[0]
        else:
            return "No definition available."
    except requests.RequestException:
        return "No definition available."


# Fetch words for different lengths
word_lists = {length: fetch_words(length) for length in fallback_words}

# Game data storage
group_games = {}



# Check if a word is valid

def is_valid_english_word(word):
    """Check if a word is valid using the Datamuse API (with timeout)."""
    try:
        response = requests.get(
            f"https://api.datamuse.com/words?sp={word}&max=1",
            timeout=5
        )
        response.raise_for_status()
        return word in [w["word"] for w in response.json()]
    except requests.RequestException:
        return False
        

# Check a user's guess
def check_guess(guess, word_to_guess):
    feedback = []
    word_to_guess_list = list(word_to_guess)
    
    for i in range(len(word_to_guess)):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")
            word_to_guess_list[i] = None  
        else:
            feedback.append(None)
    
    for i in range(len(word_to_guess)):
        if feedback[i] is None and guess[i] in word_to_guess_list:
            feedback[i] = "🟨"
            word_to_guess_list[word_to_guess_list.index(guess[i])] = None  
        elif feedback[i] is None:
            feedback[i] = "🟥"
    
    return ''.join(feedback)


@app.on_message(filters.new_chat_members)
def log_new_group(client, message):
    chat_id = message.chat.id
    chat_name = message.chat.title or "Unknown Group"
    
    added_by = message.from_user.id if message.from_user else "Unknown"
    added_by_username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "None"

    add_served_chat(chat_id)  # ✅ Add the chat to the database
    
    client.send_message(
        LOGGER_GROUP_ID, 
        f"🆕 Bot Added to a New Group!\n\n"
        f"📌 **Chat Name:** {chat_name}\n"
        f"🆔 **Chat ID:** `{chat_id}`\n"
        f"👤 **Added by User ID:** `{added_by}`\n"
        f"🔗 **Username:** {added_by_username}"
    )

    

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    add_served_user(user_id)  # ✅ Add the user to the database

    bot_info = await client.get_me()  # ✅ Fetch bot info
    bot_username = bot_info.username  # ✅ Ensure bot username is available

    await client.send_message(
        LOGGER_GROUP_ID, 
        f"📩 Private Message from `{mention}`:\n\n**{message.text or '📷 Media Message'}**"
    )

    welcome_text = (
        f"<b>Yo, Word miners! {mention} in the house! 🧙‍♂️ Welcome to the ultimate Word Mine Bot showdown!</b>\n\n"
        "<b>🕹️ How to Play:</b>\n"
        "<u><i>- Start a new game using</u> /new</i>\n"
        "<u><i>- Choose a word length</i></u>\n"
        "<u><i>- Guess the word and get results with 🟩🟨🟥</i></u>\n"
        "<u><i>- Score points and climb the leaderboard!</i></u>\n\n"
        "<i>Ready to crush your friends? Bring the battle to your group! ⚔️ Add me and let the word wars begin!</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")],  # ✅ Use bot_username
        [InlineKeyboardButton("⚙️ Bot Commands", callback_data="commands"),
         InlineKeyboardButton("🛡Support chat", url="https://t.me/WordMiners")
        ]
    ])

    await message.reply_photo(
        photo="https://files.catbox.moe/3qhaq0.jpg",  # Replace with an actual image URL
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
    user_id = message.from_user.id

    buttons = [
        [InlineKeyboardButton("4 Letters", callback_data=f"new_length_4_{user_id}")],
        [InlineKeyboardButton("5 Letters", callback_data=f"new_length_5_{user_id}")],
        [InlineKeyboardButton("6 Letters", callback_data=f"new_length_6_{user_id}")],
        [InlineKeyboardButton("7 Letters", callback_data=f"new_length_7_{user_id}")],
    ]

    await message.reply(
        "📌 **Select a word length for your game:**",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex("^new_length_"))
async def select_new_game_length(client, callback_query):
    data = callback_query.data.split("_")
    word_length = int(data[2])
    user_id = int(data[3])
    chat_id = callback_query.message.chat.id

    if user_id != callback_query.from_user.id:
        await callback_query.answer("⚠️ This selection is not for you!", show_alert=True)
        return

    # Generate a word
    word = random.choice(word_lists[word_length])
      # Store active game
    group_games[chat_id] = {
    "word": word,
    "length": word_length,
    "used_words": set(),
    "history": []
    }

    
    await callback_query.message.edit_text(
        f"🆕 **New Word Game Started!**\n"
        f"🛡 **Word Length:** `{word_length}`\n"
        f"🤔 Start guessing!"
    )


@app.on_message(filters.text & ~filters.command(["new", "leaderboard", "chatleaderboard", "end", "help", "start" "challenge", "stats", "broadcast"]))
async def process_guess(client: Client, message: Message):
    """Handles both normal game and challenge mode guesses."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    text = message.text.strip().lower()

    # Check if this is a challenge game
    for challenger_id, game_data in list(challenger_data.items()):
        if user_id in [challenger_id, game_data.get("opponent_id")]:
            word = game_data["word"]
            bet_amount = game_data["bet_amount"]

            if len(text) != len(word):
                await message.reply("⚠️ Invalid guess length!")
                return

            feedback = check_guess(text, word)

            await message.reply(f"{feedback} → {text.upper()}")

            if text == word:
                winner_id = user_id
                chat_id = message.chat.id
                loser_id = game_data["opponent_id"] if user_id == challenger_id else challenger_id
                winnings = bet_amount * 2

                update_user_points(winner_id, chat_id, winnings)
                total_points = get_user_points(winner_id)

                definition = fetch_word_definition(word)

                del challenger_data[challenger_id]

                await message.reply(
                    f"🎉 Congratulations, {mention}! 🎉\n"
                    f"🏆 correct guess! it was **{word.upper()}** \n"
                    f"💰 You won **{winnings} points**!\n"
                    f"🔥 Your new total: **{total_points} points**!\n"
                    f"🎯 Keep challenging and dominate the leaderboard!"
                    f"📖 **Definition of the word:** {definition}"
                )
            return  # Stop further processing since this was a challenge game

    # If not a challenge game, check for a normal /new game
    if chat_id not in group_games:
        return  # No active game in this group

    word_to_guess = group_games[chat_id]["word"]

    if len(text) != len(word_to_guess):
        return  

    if not is_valid_english_word(text):
        await message.reply(f"❌ {mention}, this word is not valid. Try another one!")
        return

    if text in group_games[chat_id]["used_words"]:
        await message.reply(f"🔄 {mention}, you already used this word! Try a different one.")
        return

    group_games[chat_id]["used_words"].add(text)
    feedback = check_guess(text, word_to_guess)

    group_games[chat_id]["history"].append(f"{feedback} → {text.upper()}")
    guess_history = "\n".join(group_games[chat_id]["history"])

    await message.reply(guess_history)

    if text == word_to_guess:
        update_chat_score(chat_id, user_id)
        update_global_score(user_id)

        leaderboard = get_global_leaderboard()
        print(f"🔍 Debug: Global Leaderboard Data → {leaderboard}")  # Add this line for debugging

        user_score = next((score for uid, score in leaderboard if uid == user_id), 0)
        user_rank = next((i + 1 for i, (uid, _) in enumerate(leaderboard) if uid == user_id), "Unranked")

        print(f"🔍 Debug: User Score → {user_score}, User Rank → {user_rank}")  # Add this line for debugging
        
        del group_games[chat_id]

        definition = fetch_word_definition(word_to_guess)

        await message.reply(
            f"🎉 Congratulations {mention}! 🎉\n"
            f"You guessed the word {word_to_guess.upper()} correctly!\n"
            f"🏆 You earned 1 point!\n"
            f"📊 Your total score: {user_score}\n"
            f"🌍 Your global rank: #{user_rank}"
            f"📖 **Definition of the word:** {definition}"
        )

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
