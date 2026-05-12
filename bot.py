import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import time

# --- Configuration ---
BOT_TOKEN = '8690652847:AAGCR4XDtTNkzU1qdgOS1dXwlI0YUwLvwvg' # Your Bot Token
OWNER_USERNAME = 'help_sourav'
REQUIRED_CHANNELS = [
    {"name": "IncomeTech X", "username": "@incometechx", "url": "https://t.me/incometechx"},
    {"name": "IncomeTech Chat", "username": "@IncomeTech_Chat", "url": "https://t.me/IncomeTech_Chat"}
]

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

# --- Logging System ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Anti-Spam Cooldown System ---
user_cooldowns = {}
COOLDOWN_TIME = 3 # Seconds

def is_spamming(user_id):
    """Returns True if the user is spamming the bot."""
    current_time = time.time()
    if user_id in user_cooldowns:
        if current_time - user_cooldowns[user_id] < COOLDOWN_TIME:
            return True
    user_cooldowns[user_id] = current_time
    return False

# --- Helper Functions ---
def check_membership(user_id):
    """Checks if the user has joined all required channels."""
    try:
        for channel in REQUIRED_CHANNELS:
            # get_chat_member returns status like: 'creator', 'administrator', 'member', 'left', 'kicked'
            member = bot.get_chat_member(channel["username"], user_id)
            if member.status not in ['creator', 'administrator', 'member']:
                return False
        return True
    except Exception as e:
        logging.error(f"Error checking membership for user {user_id}: {e}")
        # If the bot is not admin in the channel, it will throw an error
        return False

def generate_join_keyboard():
    """Generates the inline keyboard with channel links side-by-side."""
    markup = InlineKeyboardMarkup()
    
    channel_buttons = []
    for channel in REQUIRED_CHANNELS:
        button = InlineKeyboardButton(text="📢 Join Channel", url=channel['url'])
        channel_buttons.append(button)
    
    # চ্যানেল বাটনগুলোকে এক সারিতে (Row) বসাচ্ছি
    markup.row(*channel_buttons)
    
    verify_button = InlineKeyboardButton(text="✅ I've Joined", callback_data="check_verify")
    markup.row(verify_button)
    
    return markup

def generate_success_keyboard():
    """Generates the success keyboard with Contact Owner button."""
    markup = InlineKeyboardMarkup()
    contact_btn = InlineKeyboardButton(text="👨‍💻 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}")
    markup.add(contact_btn)
    return markup

# --- Message Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    if is_spamming(user_id):
        bot.send_message(message.chat.id, "⚠️ *Please slow down!* Wait a few seconds.", parse_mode="Markdown")
        return

    if check_membership(user_id):
        # User is already a member
        welcome_text = f"🎉 *Welcome {first_name}!*\n\nYou have successfully verified your membership. Click the button below to contact the owner."
        bot.send_message(message.chat.id, welcome_text, reply_markup=generate_success_keyboard(), parse_mode="Markdown")
    else:
        # ✅ মেসেজটি আপডেট করা হয়েছে (Owner এর সাথে কথা বলতে চ্যানেল জয়েন করো)
        join_text = f"👋 *Hello {first_name}!*\n\nIf you want to contact the owner, you must join our channels first.\n\n👇 Join below and click *I've Joined*."
        bot.send_message(message.chat.id, join_text, reply_markup=generate_join_keyboard(), parse_mode="Markdown")

# --- Callback Query Handlers (Button Clicks) ---
@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify_callback(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    if is_spamming(user_id):
        bot.answer_callback_query(call.id, "⚠️ Please don't spam the button!", show_alert=True)
        return

    if check_membership(user_id):
        # Delete the previous "Join" message
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        
        # Send Success message
        success_text = f"✅ *Verification Successful, {first_name}!*\n\nThank you for joining our channels. You can now contact the owner by clicking the button below."
        bot.send_message(call.message.chat.id, success_text, reply_markup=generate_success_keyboard(), parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Verification Successful!")
    else:
        # Show error alert if still not joined
        bot.answer_callback_query(call.id, "❌ You haven't joined all channels yet! Please join first.", show_alert=True)

# --- Auto Restart / Polling System ---
if __name__ == "__main__":
    logging.info("Bot is starting...")
    while True:
        try:
            # infinity_polling automatically handles temporary connection errors
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"Bot crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)