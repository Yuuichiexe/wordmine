from pymongo import MongoClient, ASCENDING, DESCENDING

# MongoDB Connection
DATABASE_URL = "mongodb+srv://Altor:matrix7bonten@cluster0.izvyz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(DATABASE_URL)
db = client["wordmine"]

# Collections
global_scores = db["global_scores"]
chat_scores = db["chat_scores"]
usersdb = db["users"]
chatsdb = db["chats"]

# Ensure Indexes for Performance
global_scores.create_index([("score", DESCENDING)])
chat_scores.create_index([("chat_id", ASCENDING), ("score", DESCENDING)])


# ** User Management **  
def is_served_user(user_id: int) -> bool:
    return usersdb.find_one({"user_id": user_id}) is not None

def get_served_users() -> list:
    return [user["user_id"] for user in usersdb.find({}, {"_id": 0, "user_id": 1})]

def add_served_user(user_id: int):
    if not is_served_user(user_id):
        usersdb.insert_one({"user_id": user_id})
        print(f"🆕 New User Added: {user_id}")  # ✅ Print user ID when added

# ** Chat Management **  
def is_served_chat(chat_id: int) -> bool:
    return chatsdb.find_one({"chat_id": chat_id}) is not None

def get_served_chats() -> list:
    return [chat["chat_id"] for chat in chatsdb.find({}, {"_id": 0, "chat_id": 1})]

def add_served_chat(chat_id: int):
    if not is_served_chat(chat_id):
        chatsdb.insert_one({"chat_id": chat_id})
        print(f"🆕 New Chat Added: {chat_id}")  # ✅ Print chat ID when added


# Users Global and chat scores 

def get_user_score(user_id):
    user = global_scores.find_one({"user_id": user_id}, {"_id": 0, "score": 1})
    return user["score"] if user else 0  # Default to 0 if user not found


# Get user's current score in a chat
def get_chat_user_score(chat_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT score FROM chat_scores WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    row = c.fetchone()
    conn.close()
    return row["score"] if row else 0  # Default to 0 if user not found

# Add points to a user globally
def add_points(user_id, points):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO global_scores (user_id, score) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET score = score + ?
    """, (user_id, points, points))
    conn.commit()
    conn.close()

# Deduct points from a user globally (without going negative)
def deduct_points(user_id, points):
    conn = get_connection()
    c = conn.cursor()
    current_score = get_user_score(user_id)
    new_score = max(0, current_score - points)  # Prevent negative points
    c.execute("UPDATE global_scores SET score = ? WHERE user_id = ?", (new_score, user_id))
    conn.commit()
    conn.close()

# Update global score
def update_global_score(user_id, points=1):
    add_points(user_id, points)  # This function now handles global score updates

# Get user balance (alias of get_user_score)
def get_user_balance(user_id):
    return get_user_score(user_id)

# Update chat-specific score
def update_chat_score(chat_id, user_id, points=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO chat_scores (chat_id, user_id, score) VALUES (?, ?, ?)
        ON CONFLICT(chat_id, user_id) DO UPDATE SET score = score + ?
    """, (chat_id, user_id, points, points))
    conn.commit()
    conn.close()

# Deduct points from a user's chat-specific score
def deduct_chat_points(chat_id, user_id, points):
    conn = get_connection()
    c = conn.cursor()
    current_score = get_chat_user_score(chat_id, user_id)
    new_score = max(0, current_score - points)  # Prevent negative points
    c.execute("UPDATE chat_scores SET score = ? WHERE chat_id = ? AND user_id = ?", (new_score, chat_id, user_id))
    conn.commit()
    conn.close()



def get_user_points(user_id):  
    return get_user_score(user_id)

# Update both global and chat leaderboards
def update_user_points(user_id, chat_id, points):
    if points > 0:
        add_points(user_id, points)  # Global leaderboard update
        update_chat_score(chat_id, user_id, points)  # Chat leaderboard update
    else:
        deduct_points(user_id, abs(points))  # Global leaderboard update
        deduct_chat_points(chat_id, user_id, abs(points))  # Chat leaderboard update



#  Leaderboard and Score Management 
def update_global_score(user_id: int, points: int = 1):
    global_scores.update_one(
        {"user_id": user_id},
        {"$inc": {"score": points}},
        upsert=True
    )
    updated_user = global_scores.find_one({"user_id": user_id})
    print(f"Updated Global Score: {updated_user}")  # Debugging output

def update_chat_score(chat_id: int, user_id: int, points: int = 1):
    chat_scores.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"score": points}},
        upsert=True
    )
    updated_user = chat_scores.find_one({"chat_id": chat_id, "user_id": user_id})
    print(f"Updated Chat Score: {updated_user}")  # Debugging output

def get_global_leaderboard(limit: int = 10):
    leaderboard = list(global_scores.find({}, {"_id": 0, "user_id": 1, "score": 1})
                        .sort("score", DESCENDING)
                        .limit(limit))
    print(f"🔍 Global Leaderboard Retrieved: {leaderboard}")  # Debugging Output
    return leaderboard

def get_chat_leaderboard(chat_id: int, limit: int = 10):
    leaderboard = list(chat_scores.find({"chat_id": chat_id}, {"_id": 0, "user_id": 1, "score": 1})
                        .sort("score", DESCENDING)
                        .limit(limit))
    print(f"🔍 Chat Leaderboard Retrieved for chat {chat_id}: {leaderboard}")  # Debugging Output
    return leaderboard


# ** Debugging: Fetch and Print Leaderboards **
if __name__ == "__main__":
    print("🌍 Global Leaderboard Data:")
    for entry in get_global_leaderboard():
        print(entry)

    chat_id = -10012345678  # Replace with actual chat ID
    print(f"\n🏆 Chat Leaderboard Data for chat {chat_id}:")
    for entry in get_chat_leaderboard(chat_id):
        print(entry)
