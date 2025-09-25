# bot.py
import os
import json
import time
import psutil
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- prevent duplicate instances ----------
current_pid = os.getpid()
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['pid'] != current_pid and proc.info['cmdline']:
            if 'bot.py' in ' '.join(proc.info['cmdline']):
                print(f"⚠️ Duplicate bot.py detected (PID {proc.info['pid']}). Killing it...")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

# ---------- CONFIG (use environment variables) ----------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")          # set on server
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))      # set on server (your Telegram ID)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)   # optional

# ---------- initialize ----------
bot = telebot.TeleBot(BOT_TOKEN)
USERS_FILE = "users.json"

# ---------- remove webhook before polling ----------
try:
    bot.remove_webhook()
    print("✅ Webhook removed. Safe to start polling...")
except Exception as e:
    print(f"⚠️ Error removing webhook: {e}")

# ---------- helpers for JSON storage ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

users = load_users()

# ---------- build admin inline keyboard ----------
def admin_kbd_for(user_id):
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("Approve ✅", callback_data=f"approve:{user_id}"),
        InlineKeyboardButton("Deny ❌", callback_data=f"deny:{user_id}")
    )
    return kb

# ---------- /start handler ----------
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    uid = str(msg.chat.id)
    username = msg.from_user.username or msg.from_user.full_name or "NoUsername"
    if uid not in users:
        users[uid] = {"approved": False, "username": username}
        save_users(users)
        # Notify admin
        text = f"🔔 New user request\n\n👤 {username}\n🆔 {uid}\n\nClick to Approve or Deny."
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=admin_kbd_for(uid))
        bot.send_message(chat_id=uid, text="✅ Request sent. Please wait for admin approval.")
    else:
        if users[uid].get("approved"):
            bot.send_message(chat_id=uid, text="✅ You are approved. Start chatting!")
        else:
            bot.send_message(chat_id=uid, text="⏳ Your request is pending admin approval. Please wait.")

# ---------- callback query handler ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.from_user.id != ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "You are not authorized to do this.")
            return

        action, uid = call.data.split(":", 1)

        if uid not in users:
            bot.answer_callback_query(call.id, "User not found in DB.")
            return

        if action == "approve":
            users[uid]["approved"] = True
            save_users(users)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=f"✅ Approved user {users[uid].get('username')} (ID: {uid})")
            bot.send_message(chat_id=int(uid), text="🎉 You are approved! You can now use the bot.")
            bot.answer_callback_query(call.id, "User approved.")
        elif action == "deny":
            users[uid]["approved"] = False
            save_users(users)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=f"❌ Denied user {users[uid].get('username')} (ID: {uid})")
            bot.send_message(chat_id=int(uid), text="🚫 Your request was denied by the admin.")
            bot.answer_callback_query(call.id, "User denied.")
        else:
            bot.answer_callback_query(call.id, "Unknown action.")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}")

# ---------- message handler ----------
@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    uid = str(m.chat.id)
    if uid in users and users[uid].get("approved"):
        text = m.text.strip()
        if OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a polite assistant that writes short replies to user reviews."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=120
                )
                reply = resp["choices"][0]["message"]["content"].strip()
            except Exception as e:
                reply = f"⚠️ AI error: {e}"
        else:
            reply = f"🤖 (Demo reply) You said: {text}"

        bot.send_message(chat_id=m.chat.id, text=reply)
    else:
        bot.send_message(chat_id=m.chat.id, text="⏳ You are not approved yet. Please wait for admin approval.")

# ---------- start polling safely ----------
if __name__ == "__main__":
    print("🤖 Bot started...")
    while True:
        try:
            bot.remove_webhook()   # just in case
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"⚠️ Polling error: {e}")
            time.sleep(5)
