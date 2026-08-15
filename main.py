import telebot
import os
from telebot import types
from keep_alive import keep_alive

TOKEN = "8816940858:AAEwDQ94ues00rcG1RVkNMPumQh7Xxgfowc"
ADMIN_ID = 8753350906

bot = telebot.TeleBot(TOKEN)

# Kanallar ro'yxati
CHANNELS = [-1004393253930, -1003774304125, -1003500723640]

user_languages = {}
user_db = {}  
movies_db = {} 

FORBIDDEN_WORDS = [
    "porno", "sex", "sins", "baxm", "jalab", "kino_18", "18+", "erotika", 
    "islom", "namoz", "hadis", "quron", "alloh", "qur'on", "fatvo", "din"
]

def add_user(user_id):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write("")
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(str(user_id) + "\n")
    if user_id not in user_db:
        user_db[user_id] = {'vip': False, 'lang': 'uz', 'blocked': False}

def is_blocked(user_id):
    if user_id in user_db and user_db[user_id].get('blocked', False):
        return True
    return False

def check_content_safety(text):
    if not text:
        return True
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return False 
    return True

def get_total_users():
    if not os.path.exists("users.txt"):
        return 0
    with open("users.txt", "r") as f:
        return len(f.read().splitlines())

def get_total_videos():
    return len(movies_db)

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            return False
    return True

translations = {
    'uz': {
        'sub_error': "❌ Hamma kanallarga obuna bo'lmadingiz!",
        'sub_success': "✅ Obuna tasdiqlandi! Asosiy menyu:",
        'search_movie': "🔍 Qidiruv",
        'random_movie': "🎲 Tasodifiy",
        'recommend_movie': "💡 Kino tavsiya qilish",
        'my_movies': "👤 Shaxsiy kino qo'shish",
        'vip_menu': "💎 VIP video qo'shish",
        'lang_btn': "🌐 Tilni o'zgartirish",
        'vip_text': (
            "💎 **VIP Obuna Bo'limi**\n\n"
            "💳 **Karta raqam:** `6262 5701 4806 4381`\n"
            "👤 **Karta egasi:** OBIDJONOVA MOXLAROYIM\n\n"
            "Pulni o'tkazgach, to'lov **chekini (rasmini)** shu botga yuboring. "
            "Bot chekingizni qabul qilib, avtomatik ravishda VIP obunani ulab qo'yadi!"
        ),
        'back': "🔙 Orqaga"
    },
    'ru': {
        'sub_error': "❌ Вы подписались не на все каналы!",
        'sub_success': "✅ Подписка подтверждена!",
        'search_movie': "🔍 Поиск",
        'random_movie': "🎲 Случайный",
        'recommend_movie': "💡 Рекомендации",
        'my_movies': "👤 Добавить кино",
        'vip_menu': "💎 VIP видео",
        'lang_btn': "🌐 Изменить язык",
        'vip_text': "💎 **VIP Подписка**\n💳 `6262 5701 4806 4381` (OBIDJONOVA MOXLAROYIM)\nChekni yuboring va VIP avtomat ulanadi!",
        'back': "🔙 Назад"
    },
    'en': {
        'sub_error': "❌ You have not subscribed to all channels!",
        'sub_success': "✅ Subscription verified!",
        'search_movie': "🔍 Search",
        'random_movie': "🎲 Random",
        'recommend_movie': "💡 Recommendations",
        'my_movies': "👤 Add movie",
        'vip_menu': "💎 VIP video",
        'lang_btn': "🌐 Change Language",
        'vip_text': "💎 **VIP Subscription**\n💳 `6262 5701 4806 4381` (OBIDJONOVA MOXLAROYIM)\nSend receipt to get instant VIP!",
        'back': "🔙 Back"
    }
}

def get_lang(user_id):
    if user_id in user_db:
        return user_db[user_id]['lang']
    return user_languages.get(user_id, 'uz')

def main_menu_markup(lang):
    t = translations[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(t['search_movie']),
        types.KeyboardButton(t['random_movie'])
    )
    markup.add(
        types.KeyboardButton(t['recommend_movie']),
        types.KeyboardButton(t['my_movies'])
    )
    markup.add(types.KeyboardButton(t['vip_menu']))
    markup.add(types.KeyboardButton(t['lang_btn']))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if is_blocked(user_id):
        bot.send_message(message.chat.id, "🚫 Siz botdan foydalanishdan bloklangansiz!")
        return

    lang = get_lang(user_id)
    if check_subscription(user_id):
        bot.send_message(message.chat.id, translations[lang]['sub_success'], reply_markup=main_menu_markup(lang))
    else:
        welcome_intro = (
            "✨ Assalomu alaykum! Botimizga xush kelibsiz.\n"
            "Kinolarni topish uchun quyidagi kanallarga obuna bo'ling:"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, ch in enumerate(CHANNELS, 1):
            markup.add(types.InlineKeyboardButton(f"Obuna bo'lish {i}", url=f"https://t.me/c/{str(ch).replace('-100','')}/1"))
        markup.add(types.InlineKeyboardButton("🔄 Obunani tekshirish", callback_data="check_sub"))
        markup.add(types.InlineKeyboardButton("🌐 Tilni tanlash", callback_data="lang_menu"))
        bot.send_message(message.chat.id, welcome_intro, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "lang_menu")
def language_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("O'zbekcha 🇺🇿", callback_data="set_uz"),
        types.InlineKeyboardButton("Русский 🇷🇺", callback_data="set_ru"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="set_en")
    )
    bot.edit_message_text("Tilni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def set_lang_handler(call):
    user_id = call.from_user.id
    if is_blocked(user_id):
        return
    lang = call.data.split("_")[1]
    user_languages[user_id] = lang
    if user_id in user_db:
        user_db[user_id]['lang'] = lang
    bot.answer_callback_query(call.id, "Til o'zgartirildi!")
    
    if check_subscription(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, translations[lang]['sub_success'], reply_markup=main_menu_markup(lang))
    else:
        bot.answer_callback_query(call.id, translations[lang]['sub_error'], show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_handler(call):
    user_id = call.from_user.id
    if is_blocked(user_id):
        return
    lang = get_lang(user_id)
    
    if check_subscription(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, translations[lang]['sub_success'], reply_markup=main_menu_markup(lang))
    else:
        bot.answer_callback_query(call.id, translations[lang]['sub_error'], show_alert=True)

# Tugmalar bosilganda ishlaydigan qism
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    if is_blocked(user_id):
        bot.reply_to(message, "🚫 Siz botdan foydalanishdan bloklangansiz!")
        return

    lang = get_lang(user_id)
    t = translations[lang]
    text = message.text

    if not check_content_safety(text):
        user_db[user_id]['blocked'] = True
        bot.reply_to(message, "❌ Taqiqlangan kontent yuborganingiz uchun botdan **bloklandingiz!**")
        bot.send_message(ADMIN_ID, f"⚠️ **Qoidabuzar bloklandi!**\n🆔 ID: `{user_id}`")
        return

    if text in [translations['uz']['vip_menu'], translations['ru']['vip_menu'], translations['en']['vip_menu']]:
        bot.send_message(message.chat.id, t['vip_text'], parse_mode="Markdown")
    elif text in [translations['uz']['search_movie'], translations['ru']['search_movie'], translations['en']['search_movie']]:
        bot.reply_to(message, "🔍 Qidirmoqchi bo'lgan kino nomini yuboring:")
    elif text in [translations['uz']['random_movie'], translations['ru']['random_movie'], translations['en']['random_movie']]:
        bot.reply_to(message, "🎲 Tasodifiy kino qidirilmoqda...")
    elif text in [translations['uz']['recommend_movie'], translations['ru']['recommend_movie'], translations['en']['recommend_movie']]:
        bot.reply_to(message, "💡 Tavsiya qilinadigan kinolar tez orada qo'shiladi.")
    elif text in [translations['uz']['my_movies'], translations['ru']['my_movies'], translations['en']['my_movies']]:
        bot.reply_to(message, "👤 Kino qo'shish uchun nomini yoki videoni yuboring:")
    elif text in [translations['uz']['lang_btn'], translations['ru']['lang_btn'], translations['en']['lang_btn']]:
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("O'zbekcha 🇺🇿", callback_data="set_uz"),
            types.InlineKeyboardButton("Русский 🇷🇺", callback_data="set_ru"),
            types.InlineKeyboardButton("English 🇬🇧", callback_data="set_en")
        )
        bot.send_message(message.chat.id, "Tilni tanlang:", reply_markup=markup)
    elif message.text == "/panel" and user_id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👑 Admin Panel\n👥 Foydalanuvchilar: {get_total_users()}\n🎬 Kinolar: {get_total_videos()}")
    else:
        bot.reply_to(message, "✅ Xabaringiz qabul qilindi!")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return
    if is_blocked(user_id):
        return

    if user_id not in user_db:
        user_db[user_id] = {'vip': True, 'lang': 'uz', 'blocked': False}
    else:
        user_db[user_id]['vip'] = True

    bot.reply_to(message, "🎉 Chekingiz qabul qilindi va sizga **AVTOMATIK ravishda VIP Obuna** ulandi!")

    caption = (
        f"💳 **Yangi VIP Chek Keldi! (Avtomat ulandi)**\n\n"
        f"👤 Foydalanuvchi: {message.from_user.first_name}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"Soxta bo'lsa VIP ni bekor qilish:"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Soxta (VIP ni bekor qilish)", callback_data=f"revoke_vip_{user_id}"))
    
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, caption, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("revoke_vip_"))
def revoke_vip_handler(call):
    if call.from_user.id != ADMIN_ID:
        return
    target_user_id = int(call.data.split("_")[2])
    if target_user_id in user_db:
        user_db[target_user_id]['vip'] = False
    bot.send_message(target_user_id, "❌ Kechirasiz, admin chekingiz soxta ekanini aniqladi va VIP obunangiz bekor qilindi.")
    bot.answer_callback_query(call.id, "VIP olib tashlandi!")

keep_alive()

if __name__ == '__main__':
    bot.infinity_polling()
    
