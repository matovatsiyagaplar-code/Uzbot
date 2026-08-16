import telebot
from telebot import types
import random
import time
from keep_alive import keep_alive

TOKEN = "8816940858:AAEwDQ94ues00rcG1RVkNMPumQh7Xxgfowc"
ADMIN_ID = 8753350906

bot = telebot.TeleBot(TOKEN)

# Bazalar
user_db = {}   # {user_id: {'lang': 'uz', 'vip_expire': 0, 'blocked': False, 'step': None}}
movies_db = {} # {code: {'file_id': '...', 'type': 'normal' or 'vip'}}

# VIP Tariflar va Narxlar (Til bo'yicha)
VIP_TARIFFS = {
    'uz': {
        '1': ("1 oy — 15,000 so'm", 30 * 86400),
        '3': ("3 oy — 20,000 so'm", 90 * 86400),
        '6': ("6 oy — 35,000 so'm", 180 * 86400),
    },
    'ru': {
        '1': ("1 месяц — 200 руб", 30 * 86400),
        '3': ("3 месяца — 300 руб", 90 * 86400),
        '6': ("6 месяцев — 520 руб", 180 * 86400),
    },
    'en': {
        '1': ("1 month — $12", 30 * 86400),
        '3': ("3 months — $15", 90 * 86400),
        '6': ("6 months — $22", 180 * 86400),
    }
}

translations = {
    'uz': {
        'sub_success': "✅ Xush kelibsiz! Asosiy menyu:",
        'search': "🔍 Qidirish",
        'random': "🎲 Tasodifiy",
        'recommend': "💡 Kino tavsiya qilish",
        'upload': "📤 Shaxsiy kino qo'shish",
        'vip': "💎 VIP Obuna",
        'lang': "🌐 Tilni o'zgartirish",
        'vip_menu_title': "💎 **VIP Obuna Bo'limi**\nTarifni tanlang:",
        'card_info': (
            "💎 Tanlangan tarif: **{tariff_name}**\n\n"
            "💳 **Karta raqam:** `6262 5701 4806 4381`\n"
            "👤 **Karta egasi:** Obidjonova M\n\n"
            "📥 Pulni o'tkazgach, to'lov **chekini (rasmini)** shu botga yuboring. "
            "Bot avtomatik ravishda VIP obunani ulab qo'yadi!"
        ),
        'receipt_success': "✅ Chekingiz qabul qilindi va bot avtomatik ravishda sizga VIP obunani ulab qo'ydi! 🎉",
        'not_found': "❌ `{text}` kodli kino topilmadi.",
        'vip_needed': "💎 Bu VIP kino! Uni ko'rish uchun VIP obuna kerak.",
        'enter_code': "🔍 Kino kodini yuboring:",
        'no_movies': "❌ Hozircha kinolar yo'q.",
        'choose_lang': "Tilni tanlang:"
    },
    'ru': {
        'sub_success': "✅ Добро пожаловать! Главное меню:",
        'search': "🔍 Поиск",
        'random': "🎲 Случайный",
        'recommend': "💡 Рекомендовать фильм",
        'upload': "📤 Добавить фильм",
        'vip': "💎 VIP Подписка",
        'lang': "🌐 Язык",
        'vip_menu_title': "💎 **Раздел VIP Подписки**\nВыберите тариф:",
        'card_info': (
            "💎 Выбранный тариф: **{tariff_name}**\n\n"
            "💳 **Номер карты:** `6262 5701 4806 4381`\n"
            "👤 **Владелец карты:** Obidjonova M\n\n"
            "📥 После перевода средств отправьте **чек (скриншот)** оплаты в этот бот. "
            "Бот автоматически подключит VIP подписку!"
        ),
        'receipt_success': "✅ Ваш чек принят, и бот автоматически подключил вам VIP подписку! 🎉",
        'not_found': "❌ Фильм с кодом `{text}` не найден.",
        'vip_needed': "💎 Это VIP фильм! Для просмотра нужна VIP подписка.",
        'enter_code': "🔍 Отправьте код фильма:",
        'no_movies': "❌ Потaм фильмов пока нет.",
        'choose_lang': "Выберите язык:"
    },
    'en': {
        'sub_success': "✅ Welcome! Main menu:",
        'search': "🔍 Search",
        'random': "🎲 Random",
        'recommend': "💡 Recommend movie",
        'upload': "📤 Upload movie",
        'vip': "💎 VIP Subscription",
        'lang': "🌐 Language",
        'vip_menu_title': "💎 **VIP Subscription Section**\nChoose a tariff:",
        'card_info': (
            "💎 Selected tariff: **{tariff_name}**\n\n"
            "💳 **Card number:** `6262 5701 4806 4381`\n"
            "👤 **Card holder:** Obidjonova M\n\n"
            "📥 After transferring the money, send the payment **receipt (screenshot)** to this bot. "
            "The bot will automatically activate your VIP subscription!"
        ),
        'receipt_success': "✅ Your receipt has been accepted and the bot has automatically activated your VIP subscription! 🎉",
        'not_found': "❌ Movie with code `{text}` not found.",
        'vip_needed': "💎 This is a VIP movie! You need a VIP subscription to watch it.",
        'enter_code': "🔍 Send the movie code:",
        'no_movies': "❌ No movies available yet.",
        'choose_lang': "Choose language:"
    }
}

def get_lang(user_id):
    return user_db.get(user_id, {}).get('lang', 'uz')

def is_vip(user_id):
    if user_id == ADMIN_ID:
        return True
    user = user_db.get(user_id, {})
    return user.get('vip_expire', 0) > time.time()

def get_main_menu(user_id):
    lang = get_lang(user_id)
    t = translations[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton(t['search']), types.KeyboardButton(t['random']))
        markup.add(types.KeyboardButton(t['recommend']), types.KeyboardButton(t['upload']))
        markup.add(types.KeyboardButton("🎬 Oddiy video qo'shish"), types.KeyboardButton("💎 VIP video qo'shish"))
        markup.add(types.KeyboardButton(t['vip']), types.KeyboardButton(t['lang']))
    else:
        markup.add(types.KeyboardButton(t['search']), types.KeyboardButton(t['random']))
        markup.add(types.KeyboardButton(t['recommend']), types.KeyboardButton(t['upload']))
        markup.add(types.KeyboardButton(t['vip']), types.KeyboardButton(t['lang']))
    return markup

def get_movie_inline_markup(user_id):
    lang = get_lang(user_id)
    vip_btn_text = translations[lang]['vip']
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(vip_btn_text, callback_data="buy_vip_menu"),
        types.InlineKeyboardButton("📢 Reklama", url="https://t.me/")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if user_id not in user_db:
        user_db[user_id] = {'lang': 'uz', 'vip_expire': 0, 'blocked': False, 'step': None}
    
    if user_db[user_id]['blocked']:
        bot.send_message(message.chat.id, "❌ Siz botdan foydalanishdan bloklangansiz.")
        return

    lang = get_lang(user_id)
    bot.send_message(message.chat.id, translations[lang]['sub_success'], reply_markup=get_main_menu(user_id))

def send_vip_menu(chat_id, user_id, message_id=None, is_edit=False):
    lang = get_lang(user_id)
    t = translations[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    tariffs = VIP_TARIFFS[lang]
    for key, data in tariffs.items():
        markup.add(types.InlineKeyboardButton(data[0], callback_data=f"select_tariff_{key}"))
    
    text = t['vip_menu_title']
    if is_edit and message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "buy_vip_menu" or call.data.startswith("vip_lang_"))
def vip_menu_callback(call):
    send_vip_menu(call.message.chat.id, call.from_user.id, call.message.message_id, is_edit=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_tariff_"))
def select_tariff_callback(call):
    tariff_key = call.data.split("_")[2]
    user_id = call.from_user.id
    lang = get_lang(user_id)
    t = translations[lang]
    tariff_name = VIP_TARIFFS[lang][tariff_key][0]
    
    text = t['card_info'].format(tariff_name=tariff_name)
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except Exception:
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    user_db[user_id]['pending_tariff'] = tariff_key

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return
    
    lang = get_lang(user_id)
    t = translations[lang]
    
    user_db[user_id]['vip_expire'] = time.time() + (90 * 86400)
    bot.reply_to(message, t['receipt_success'])
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Haqiqiy", callback_data=f"admin_ok_{user_id}"),
        types.InlineKeyboardButton("❌ Soxta (Ban)", callback_data=f"admin_ban_{user_id}")
    )
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, f"💳 **Yangi to'lov cheki!**\n🆔 Foydalanuvchi: `{user_id}`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_check_action(call):
    if call.from_user.id != ADMIN_ID:
        return
    action, target_id = call.data.split("_")[1], int(call.data.split("_")[2])
    
    if action == "ok":
        bot.answer_callback_query(call.id, "Tasdiqlandi!")
        bot.send_message(target_id, "Admin chekingizni haqiqiy deb topdi. VIP obunangiz o'z kuchida qoldi!")
    elif action == "ban":
        user_db[target_id]['vip_expire'] = 0
        user_db[target_id]['blocked'] = True
        bot.answer_callback_query(call.id, "Chek soxta topildi va foydalanuvchi bloklandi!")
        bot.send_message(target_id, "❌ Chekingiz soxta deb topildi va siz botdan bloklandingiz.")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

@bot.message_handler(func=lambda message: True)
def text_router(message):
    user_id = message.from_user.id
    if user_id not in user_db:
        user_db[user_id] = {'lang': 'uz', 'vip_expire': 0, 'blocked': False, 'step': None}
    
    if user_db[user_id]['blocked']:
        bot.send_message(message.chat.id, "❌ Siz bloklangansiz.")
        return

    lang = get_lang(user_id)
    text = message.text.strip()
    t = translations[lang]

    step = user_db[user_id].get('step')

    if step == 'waiting_personal_code':
        code = text
        video_info = user_db[user_id].get('temp_video')
        movies_db[code] = {'file_id': video_info, 'type': 'normal'}
        user_db[user_id]['step'] = None
        bot.reply_to(message, f"✅ Shaxsiy kino bazaga muvaffaqiyatli qo'shildi! Kodi: `{code}`", parse_mode="Markdown")
        return

    if step == 'waiting_admin_normal':
        code = text
        video_info = user_db[user_id].get('temp_video')
        movies_db[code] = {'file_id': video_info, 'type': 'normal'}
        user_db[user_id]['step'] = None
        bot.reply_to(message, f"✅ Oddiy kino qo'shildi. Kodi: `{code}`", parse_mode="Markdown")
        return

    if step == 'waiting_admin_vip':
        code = text
        video_info = user_db[user_id].get('temp_video')
        movies_db[code] = {'file_id': video_info, 'type': 'vip'}
        user_db[user_id]['step'] = None
        bot.reply_to(message, f"✅ VIP kino qo'shildi. Kodi: `{code}`", parse_mode="Markdown")
        return

    # Barcha tillardagi VIP tugma variatsiyalarini ushlash
    if text == t['vip'] or text in ["💎 VIP Obuna", "💎 VIP Подписка", "💎 VIP Subscription"]:
        send_vip_menu(message.chat.id, user_id)
        return

    if text == t['lang']:
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("O'zbekcha 🇺🇿", callback_data="set_uz"),
            types.InlineKeyboardButton("Русский 🇷🇺", callback_data="set_ru"),
            types.InlineKeyboardButton("English 🇬🇧", callback_data="set_en")
        )
        bot.send_message(message.chat.id, t['choose_lang'], reply_markup=markup)
        return

    if text == t['upload']:
        user_db[user_id]['step'] = 'waiting_personal_video'
        bot.reply_to(message, "📤 Shaxsiy kino yuklash uchun **videoni yuboring**:\n\n_Eslatma: Agar noto'g'ri narsa tashlasangiz, bot avtomatik ravishda ban qiladi._", parse_mode="Markdown")
        return

    if text == "🎬 Oddiy video qo'shish" and user_id == ADMIN_ID:
        user_db[user_id]['step'] = 'waiting_admin_normal_video'
        bot.reply_to(message, "Admin: Oddiy videoni yuboring:")
        return

    if text == "💎 VIP video qo'shish" and user_id == ADMIN_ID:
        user_db[user_id]['step'] = 'waiting_admin_vip_video'
        bot.reply_to(message, "Admin: VIP videoni yuboring:")
        return

    if text == t['search']:
        bot.reply_to(message, t['enter_code'])
        return

    if text == t['random']:
        if not movies_db:
            bot.reply_to(message, t['no_movies'])
            return
        code = random.choice(list(movies_db.keys()))
        m = movies_db[code]
        if m['type'] == 'vip' and not is_vip(user_id):
            bot.reply_to(message, t['vip_needed'])
            return
        bot.send_video(message.chat.id, m['file_id'], caption=f"🎲 Tasodifiy kino (Kod: `{code}`)", reply_markup=get_movie_inline_markup(user_id), parse_mode="Markdown")
        return

    if text == t['recommend']:
        bot.reply_to(message, "💡 Tavsiya qilinadigan kinolar tez orada qo'shiladi.")
        return

    if text in movies_db:
        m = movies_db[text]
        if m['type'] == 'vip' and not is_vip(user_id):
            bot.reply_to(message, t['vip_needed'])
            return
        bot.send_video(message.chat.id, m['file_id'], caption=f"🎬 Siz so'ragan kino (Kod: `{text}`)", reply_markup=get_movie_inline_markup(user_id), parse_mode="Markdown")
    else:
        bot.reply_to(message, t['not_found'].format(text=text), parse_mode="Markdown")

@bot.message_handler(content_types=['video'])
def handle_video_steps(message):
    user_id = message.from_user.id
    if user_id not in user_db:
        user_db[user_id] = {'lang': 'uz', 'vip_expire': 0, 'blocked': False, 'step': None}
    
    step = user_db[user_id].get('step')

    if step == 'waiting_personal_video':
        user_db[user_id]['temp_video'] = message.video.file_id
        user_db[user_id]['step'] = 'waiting_personal_code'
        bot.reply_to(message, "✅ Video qabul qilindi. Endi shu kino uchun **kod kiriting** (masalan: `777`):")
        return

    if step == 'waiting_admin_normal_video' and user_id == ADMIN_ID:
        user_db[user_id]['temp_video'] = message.video.file_id
        user_db[user_id]['step'] = 'waiting_admin_normal'
        bot.reply_to(message, "Kino kodini kiriting:")
        return

    if step == 'waiting_admin_vip_video' and user_id == ADMIN_ID:
        user_db[user_id]['temp_video'] = message.video.file_id
        user_db[user_id]['step'] = 'waiting_admin_vip'
        bot.reply_to(message, "VIP kino kodini kiriting:")
        return

    if user_id != ADMIN_ID:
        user_db[user_id]['blocked'] = True
        bot.reply_to(message, "🚫 Qoidaga zid harakat amalga oshirildi! Bot avtomatik ravishda sizni blokladi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def set_lang_callback(call):
    user_id = call.from_user.id
    lang = call.data.split("_")[1]
    user_db[user_id]['lang'] = lang
    bot.answer_callback_query(call.id, "Til o'zgartirildi!")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id, translations[lang]['sub_success'], reply_markup=get_main_menu(user_id))

keep_alive()

if __name__ == '__main__':
    bot.infinity_polling()
