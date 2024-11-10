# 7592879872:AAHEnhXe9bDC7RzBYr5Tkjth69LWnEzlQvk
import telebot
from yt_dlp import YoutubeDL
import os
import re
import json

DATA_FILE = "users_data.json"

# Fayldan ma'lumotlarni yuklash funksiyasi
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Faylga ma'lumotlarni saqlash funksiyasi
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Foydalanuvchi ma'lumotlarini saqlash funksiyasi
def save_user_info(message):
    data = load_data()
    user_id = str(message.from_user.id)

    data[user_id] = {
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "user_id": message.from_user.id,
        "phone_number": message.contact.phone_number if message.contact else None
    }

    save_data(data)

# Maxsus kodni tekshirish
def is_special_code(message):
    return message.text.strip() == "A20050116a"

TOKEN = "7592879872:AAHEnhXe9bDC7RzBYr5Tkjth69LWnEzlQvk"
bot = telebot.TeleBot(TOKEN)

# YouTube havolasini aniqlash uchun regex
YOUTUBE_URL_PATTERN = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga YouTube linkini yuboring, men esa videoni yuklab beraman.")
    save_user_info(message)



# Foydalanuvchilarga qo'shimcha ma'lumotlarni ko'rsatish
def show_user_data(message):
    data = load_data()

    # Foydalanuvchilarning ro'yxatini yaratish
    total_users = len(data)
    user_list = "\n".join([f"{index + 1}. {user['first_name']} {user.get('username', 'N/A')}" for index, user in enumerate(data.values())])

    # Tugmalarni yaratish
    markup = telebot.types.InlineKeyboardMarkup()

    # Tugmalarga callback_data sifatida faqat kerakli ma'lumotni uzating
    markup.add(telebot.types.InlineKeyboardButton("🧮Foydalanuvchilar soni", callback_data="total_users"))
    markup.add(telebot.types.InlineKeyboardButton("👬Foydalanuvchilar ism/familyasi", callback_data="user_names"))
    markup.add(telebot.types.InlineKeyboardButton("📝To'liq ma'lumot", callback_data="user_details"))
    markup.add(telebot.types.InlineKeyboardButton("🧰Boshqa ma'lumot", callback_data="other_info"))

    # Foydalanuvchiga ro'yxatni yuborish
    bot.send_message(message.chat.id, "🔑Maxsus kod kiritildi. \n🕵🏻‍♀️Mana, foydalanuvchi ma'lumotlari:", reply_markup=markup)

# Callback handler


def callback_query1(call):
    # callback_data'ni ajratib olish
    if '|' in call.data:  # Agar `callback_data` format_id va url bo'lsa
        format_id, url = call.data.split('|')
        bot.send_message(call.message.chat.id, f"{format_id} formatida yuklanmoqda...")
        # Bu yerda yuklash funksiyasini chaqirishingiz mumkin
        # Masalan: download_video(format_id, url)

    else:
        # Aks holda, oddiy `action` qiymatlari bo'yicha qayta ishlash
        action = call.data  

        if action == "total_users":
            total_users = len(load_data())  # Foydalanuvchilar soni
            bot.send_message(call.message.chat.id, f"👬Foydalanuvchilar soni: {total_users}")

        elif action == "user_names":
            data = load_data()
            user_list = "\n".join([f"{index + 1}. {user['first_name']} (@{user.get('username', 'N/A')})" for index, user in enumerate(data.values())])
            bot.send_message(call.message.chat.id, f"🙋‍♂️Foydalanuvchilar: \n{user_list}")

        elif action == "user_details":
            data = load_data()
            user_details = "\n".join([f"____________________\n{index + 1}. ID: {user['user_id']}, \nName: {user['first_name']}, \nUsername: @{user.get('username', 'N/A')}, \nPhone: {user.get('phone_number', 'Not provided')}" for index, user in enumerate(data.values())])
            bot.send_message(call.message.chat.id, f"🥸To'liq foydalanuvchi ma'lumotlari: \n{user_details}")

        elif action == "other_info":
            bot.send_message(call.message.chat.id, "Boshqa ma'lumot: Sizga kerakli boshqa ma'lumotni shu yerga kiritishingiz mumkin.")

# Foydalanuvchiga video formatlarini tanlash imkoniyati bilan 
def display_video_options(message, url):
    try:
        bot.send_message(message.chat.id, "⏳Video ma'lumotlari olinmoqda, kuting...")

        ydl_opts = {'format': 'best'}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Miniatura URL va video nomi
        thumbnail_url = info.get("thumbnail")
        video_title = info.get("title")

        # Mavjud formatlar
        formats = {}
        format_details = []  # Hajmni ko'rsatish uchun matn shaklida yig'amiz
        # Umumiy keng tarqalgan rezolyutsiyalar va ularga eng yaqin formatlar
        desired_resolutions_map = {
            '144': range(144, 256),
            '240': range(256, 360),
            '360': range(360, 480),
            '480': range(480, 720),
            '720': range(720, 1080),
            '1080': range(1080, 2160)
        }

        # Har bir rezolyutsiya uchun eng birinchi mos formatni tanlash
        for fmt in info['formats']:
            if fmt['ext'] == 'mp4' and 'height' in fmt and fmt['height'] is not None:
                height = fmt['height']
                filesize = fmt.get('filesize')

                # Umumiy rezolyutsiyalardan eng mosini tanlash
                for common_res, res_range in desired_resolutions_map.items():
                    if height in res_range and common_res not in formats:
                        if filesize:  # Faqat hajmi mavjud bo'lgan formatlarni qo'shish
                            formats[common_res] = fmt['format_id']
                            size_mb = round(filesize / (1024 * 1024), 1)
                            format_details.append(f"🚀 {common_res}p:  {size_mb}MB")
                        break  # Birinchi mos topilgandan keyin chiqamiz

        # Tanlov uchun format tugmalari yaratish
        markup = telebot.types.InlineKeyboardMarkup()
        buttons = []

        for height in sorted(formats.keys(), key=int):  # Kichikdan kattaga tartiblash
            button = telebot.types.InlineKeyboardButton(f"📹{height}p", callback_data=f"{formats[height]}|{url}")
            buttons.append(button)

            # Har uchta tugmani bitta qatorga joylash
            if len(buttons) == 3:
                markup.row(*buttons)
                buttons = []

        # Qolgan tugmalarni qo'shish
        if buttons:
            markup.row(*buttons)

        # Formatlar va hajm haqida matnni yig'ish
        format_text = "\n".join(format_details)

        # Foydalanuvchiga miniaturani va format tugmalarini ko'rsatish
        bot.send_photo(
            message.chat.id,
            thumbnail_url,
            caption=f"📹 {video_title}\n\n{format_text}",
            reply_markup=markup
        )

    except Exception as e:
        bot.send_message(message.chat.id, "Xato, to'g'ri YouTube video havolasini yuboring.")

# Tanlangan format bo'yicha videoni yuklash va foydalanuvchiga yuborish funksiyasi
# Foydalanuvchilarga qo'shimcha ma'lumotlarni ko'rsatish
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    action = call.data  # `callback_data`ni to'g'ridan-to'g'ri olish

    if action == "total_users":
        total_users = len(load_data())  # Foydalanuvchilar soni
        bot.send_message(call.message.chat.id, f"👬Foydalanuvchilar soni: {total_users}")

    elif action == "user_names":
        data = load_data()
        user_list = "\n".join([f"{index + 1}. {user['first_name']} (@{user.get('username', 'N/A')})" for index, user in enumerate(data.values())])
        bot.send_message(call.message.chat.id, f"🙋‍♂️Foydalanuvchilar: \n{user_list}")

    elif action == "user_details":
        data = load_data()
        user_details = "\n".join([f"____________________\n{index + 1}. ID: {user['user_id']}, \nName: {user['first_name']}, \nUsername: @{user.get('username', 'N/A')}, \nPhone: {user.get('phone_number', 'Not provided')}" for index, user in enumerate(data.values())])
        bot.send_message(call.message.chat.id, f"🥸To'liq foydalanuvchi ma'lumotlari: \n{user_details}")

    elif action == "other_info":
        bot.send_message(call.message.chat.id, "Boshqa ma'lumot: Sizga kerakli boshqa ma'lumotni shu yerga kiritishingiz mumkin.")

    else:
    # Video yuklash uchun
        format_id, url = action.split("|")
        try:
            bot.send_message(call.message.chat.id, "⏳Tanlangan formatda video yuklanmoqda, kuting...")

            ydl_opts = {
                'format': format_id,
                'outtmpl': 'downloaded_video.mp4',
                'noprogress': True,
                'nooverwrites': True
            }

            if os.path.exists("downloaded_video.mp4"):
                os.remove("downloaded_video.mp4")

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open("downloaded_video.mp4", 'rb') as video_file:
                bot.send_video(call.message.chat.id, video_file, caption=f"""🙅🏼‍♂️Hech qanday kanalga obuna bo'lish shart emas
🤠NO ads
✅Shunchaki foydalaning.
@Youtube_Down2_Bot""")

            os.remove("downloaded_video.mp4")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"🤕Xatolik yuz berdi:\n♻️Qayta urinib ko'ring yoki to'g'ri havoladan foydalaning")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Maxsus kodni tekshirish
    if is_special_code(message):
        show_user_data(message)
        return

    url = message.text.strip()

    # Xabar YouTube havolasi ekanligini tekshirish
    if re.match(YOUTUBE_URL_PATTERN, url):
        display_video_options(message, url)
    else:
        bot.reply_to(message, "Xato, to'g'ri YouTube video havolasini yuboring.")




# Botni ishga tushirish
bot.polling(timeout=120, long_polling_timeout=20)


