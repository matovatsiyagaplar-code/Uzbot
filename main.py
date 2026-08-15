import telebot
import os
from telebot import types
from keep_alive import keep_alive

TOKEN = "8816940858:AAEwDQ94ues00rcG1RVkNMPumQh7Xxgfowc"
ADMIN_ID = 8753350906

bot = telebot.TeleBot(TOKEN)

# 3 ta zaifka kanallari
CHANNELS = [-1004393253930, -1003774304125, -1003500723640]

user_languages = {}
user_db = {}  # user_id: {'vip': False, 'lang': 'uz', 'blocked': False}
movies_db = {} 

# Taqiqlangan so'zlar (porno, uyatsiz yoki dinga oid kontentni aniqlash uchun)
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
        'search_movie': "🎬 Kino qidirish",
        'random_movie': "🎲 Tasodifiy kino",
        'recommend_movie': "💡 Kino tavsiya",
        'my_movies': "📂 Shaxsiy kinolarim",
        'add_movie_admin': "➕ Admin bilan kino qo'shish",
        'vip_menu': "💎 VIP Obuna",
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
        'search_movie': "🎬 Поиск фильма",
        'random_movie': "🎲 Случайный фильм",
        'recommend_movie': "💡 Рекомендации",
        'my_movies': "📂 Мои фильмы",
        'add_movie_admin': "➕ Добавить кино с админом",
        'vip_menu': "💎 VIP Подписка",
        'lang_btn': "🌐 Изменить язык",
        'vip_text': "💎 **Раздел VIP Подписки**\n💳 `6262 5701 4806 4381` (OBIDJONOVA MOXLAROYIM)\nChekni yuboring va VIP avtomat ulanadi!",
        'back': "🔙 Назад"
    },
    'en': {
        'sub_error': "❌ You have not subscribed to all channels!",
        'sub_success': "✅ Subscription verified!",
        'search_movie': "🎬 Search Movie",
        'random_movie': "🎲 Random Movie",
        'recommend_movie': "💡 Recommendations",
        'my_movies': "📂 My Movies",
        'add_movie_admin': "➕ Add movie with admin",
        'vip_menu': "💎 VIP Subscription",
        'lang_btn': "🌐 Change Language",
        'vip_text': "💎 **VIP Subscription**\n💳 `6262 5701 4806 4381` (OBIDJONOVA MOXLAROYIM)\nSend receipt to get instant VIP!",
        'back': "🔙 Back"
    }
}

def get_lang(user_id):
    if user_id in user_db:
        return user_db[user_id]['lang']
    return user_languages.get(user_id, 'uz')

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if is_blocked(user_id):
        bot.send_message(message.chat.id, "🚫 Siz botdan foydalanishdan bloklangansiz!")
        return

    welcome_intro = (
        "✨ Assalomu alaykum! Botimizga xush kelibsiz.\n"
        "Kinolarni topish uchun quyidagi kanallarga obuna bo'ling:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, ch in enumerate(CHANNELS, 1):
        markup.add(types.InlineKeyboardButton(f"Zaifka {i} ga qo'shilish", url=f"https://t.me/c/{str(ch).replace('-100','')}/1"))
            
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
        show_main_menu(call.message.chat.id, lang)
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
        show_main_menu(call.message.chat.id, lang)
    else:
        bot.answer_callback_query(call.id, translations[lang]['sub_error'], show_alert=True)

def show_main_menu(chat_id, lang):
    t = translations[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(t['search_movie'], callback_data="search_movie"),
        types.InlineKeyboardButton(t['random_movie'], callback_data="random_movie")
    )
    markup.add(
        types.InlineKeyboardButton(t['recommend_movie'], callback_data="recommend_movie"),
        types.InlineKeyboardButton(t['my_movies'], callback_data="my_movies")
    )
    markup.add(types.InlineKeyboardButton(t['add_movie_admin'], url=f"tg://user?id={ADMIN_ID}"))
    markup.add(types.InlineKeyboardButton(t['vip_menu'], callback_data="vip_menu"))
    markup.add(types.InlineKeyboardButton(t['lang_btn'], callback_data="lang_menu"))
    
    if int(chat_id) == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel"))

    bot.send_message(chat_id, t['sub_success'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "vip_menu")
def vip_menu(call):
    user_id = call.from_user.id
    if is_blocked(user_id):
        return
    lang = get_lang(user_id)
    t = translations[lang]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(t['back'], callback_data="back_home"))
    bot.edit_message_text(t['vip_text'], call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["search_movie", "random_movie", "recommend_movie", "my_movies"])
def movie_actions(call):
    user_id = call.from_user.id
    if is_blocked(user_id):
        return
    lang = get_lang(user_id)
    
    if call.data == "my_movies":
        text = "📂 Shaxsiy kinolaringizni qo'shish uchun nomini yoki videoni yuboring (ogohlantirish: porno va dinga oid narsalar taqiqlangan va avtomat bloklanadi!):"
    else:
        text = "🔍 Kino qidirish bo'limi."
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(translations[lang]['back'], callback_data="back_home"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# Foydalanuvchi to'lov chekini rasm sifatida yuborganda (Srazu avtomatik VIP berish)
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return
    
    if is_blocked(user_id):
        return

    # Avtomatik ravishda VIP obuna ulab qo'yish
    if user_id not in user_db:
        user_db[user_id] = {'vip': True, 'lang': 'uz', 'blocked': False}
    else:
        user_db[user_id]['vip'] = True

    # Foydalanuvchiga xabar berish
    bot.reply_to(message, "🎉 Chekingiz qabul qilindi va sizga **AVTOMATIK ravishda VIP Obuna** ulandi! Endi VIP kinolardan foydalanishingiz mumkin.")

    # Adminga chekni yuborish (soxta bo'lsa VIP ni bekor qilish tugmasi bilan)
    caption = (
        f"💳 **Yangi VIP Chek Keldi! (Avtomat ulandi)**\n\n"
        f"👤 Foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username or 'yo\'q'})\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"Agar chek soxta bo'lsa, pastdagi tugmani bosib VIP statusini olib tashlashingiz mumkin:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Soxta (VIP ni bekor qilish)", callback_data=f"revoke_vip_{user_id}"))
    
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, caption, reply_markup=markup, parse_mode="Markdown")

# Admin chek soxtaligini ko'rsa VIP ni bekor qilishi
@bot.callback_query_handler(func=lambda call: call.data.startswith("revoke_vip_"))
def revoke_vip_handler(call):
    if call.from_user.id != ADMIN_ID:
        return
    target_user_id = int(call.data.split("_")[2])
    
    if target_user_id in user_db:
        user_db[target_user_id]['vip'] = False
        
    bot.send_message(target_user_id, "❌ Kechirasiz, admin chekingiz soxta ekanini aniqladi va VIP obunangiz bekor qilindi.")
    bot.edit_message_caption("❌ **Holat: Soxta deb topildi va VIP olib tashlandi**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "Foydalanuvchidan VIP obuna olib tashlandi!")

# Foydalanuvchi shaxsiy video yoki narsa yuborganda tekshirish va bloklash
@bot.message_handler(content_types=['video', 'document', 'text'])
def handle_user_uploads(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return
    
    if is_blocked(user_id):
        bot.reply_to(message, "🚫 Siz botdan foydalanishdan bloklangansiz!")
        return

    text_to_check = message.caption or message.text or ""
    
    if not check_content_safety(text_to_check):
        user_db[user_id]['blocked'] = True
        bot.reply_to(message, "❌ Siz taqiqlangan (uyatsiz/porno yoki dinga oid) kontent yuborganingiz uchun botdan **butunlay bloklandingiz!**")
        bot.send_message(ADMIN_ID, f"⚠️ **Qoidabuzar bloklandi!**\n\n👤 Foydalanuvchi: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n📝 Sabab: Taqiqlangan kontent.")
        return

@bot.callback_query_handler(func=lambda call: call.data == "back_home")
def back_home(call):
    if is_blocked(call.from_user.id):
        return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id, get_lang(call.from_user.id))

# Admin Panel: Oddiy videolar va VIP videolar uchun alohida bo'limlar
@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel_handler(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    total_users = get_total_users()
    total_videos = get_total_videos()
    
    admin_text = (
        f"👑 **Admin Panel**\n\n"
        f"📊 **Statistika:**\n"
        f"👥 Foydalanuvchilar: **{total_users} ta**\n"
        f"🎬 Jami kinolar: **{total_videos} ta**\n\n"
        f"Bo'limni tanlang:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📤 Oddiy videolar (Hamma uchun)", callback_data="upload_normal"),
        types.InlineKeyboardButton("💎 VIP videolar (Faqat VIP uchun)", callback_data="upload_vip"),
        types.InlineKeyboardButton("🔄 Statistikani yangilash", callback_data="admin_panel"),
        types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_home")
    )
    bot.edit_message_text(admin_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["upload_normal", "upload_vip"])
def admin_upload_menu(call):
    if call.from_user.id != ADMIN_ID:
        return
    mode_text = "📤 Oddiy videoni yuboring (Kod bilan):" if call.data == "upload_normal" else "💎 VIP videoni yuboring (Faqat obunachilar uchun):"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="admin_panel"))
    bot.edit_message_text(mode_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

keep_alive()

if __name__ == '__main__':
    bot.infinity_polling()

