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



TOKEN = "7592879872:AAHEnhXe9bDC7RzBYr5Tkjth69LWnEzlQvk"
bot = telebot.TeleBot(TOKEN)

# YouTube havolasini aniqlash uchun regex
YOUTUBE_URL_PATTERN = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga YouTube linkini yuboring, men esa videoni yuklab beraman.")
    save_user_info(message)

# Bloklangan foydalanuvchilarni saqlash yoki o'qish funksiyalari
def load_blocked_users():
    try:
        with open("blocked_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_blocked_users(blocked_users):
    with open("blocked_users.json", "w") as f:
        json.dump(blocked_users, f)

# Foydalanuvchilarga qo'shimcha ma'lumotlarni ko'rsatish
def show_user_data(message):
    data = load_data()

    # Tugmalarni yaratish
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🧮Foydalanuvchilar soni", callback_data="total_users"))
    markup.add(telebot.types.InlineKeyboardButton("👬Foydalanuvchilar ism/familyasi", callback_data="user_names"))
    markup.add(telebot.types.InlineKeyboardButton("📝To'liq ma'lumot", callback_data="user_details"))
    markup.add(telebot.types.InlineKeyboardButton("📤Foydalanuvchilarga xabar yuborish", callback_data="send_messages"))
    markup.add(telebot.types.InlineKeyboardButton("🚫 Foydalanuvchini bloklash", callback_data="manage_block"))

    bot.send_message(message.chat.id, "🔑Maxsus kod kiritildi. \n🕵🏻‍♀️Mana, foydalanuvchi ma'lumotlari:", reply_markup=markup)

# Bloklash menyusini ko'rsatish
def show_block_menu(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚫 Foydalanuvchini bloklash", callback_data="block_user"))
    markup.add(telebot.types.InlineKeyboardButton("✅ Foydalanuvchini blokdan chiqarish", callback_data="unblock_user"))
    bot.send_message(call.message.chat.id, "Foydalanuvchini boshqarish uchun quyidagilardan birini tanlang:", reply_markup=markup)

# Xabar yuborish tugmalari
def show_send_options(call):
    # 3 ta tugma yaratish
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📩 1 ta foydalanuvchiga", callback_data="send_to_one"))
    markup.add(telebot.types.InlineKeyboardButton("👥 Ma'lum foydalanuvchilarga", callback_data="send_to_some"))
    markup.add(telebot.types.InlineKeyboardButton("📬 Barcha foydalanuvchilarga", callback_data="send_to_all"))

    bot.send_message(call.message.chat.id, "🧐Xabarni kimga yubormoqchisiz?", reply_markup=markup)

# Foydalanuvchini bloklash
# Foydalanuvchini bloklash
def block_user(message):
    user_input = message.text.strip()  # Foydalanuvchi tomonidan kiritilgan xabarni olamiz
    if not user_input.isdigit():  # Agar xabar raqam bo'lmasa
        bot.send_message(message.chat.id, "❗️Bu ID ga ega foydalanuvchi topilmadi.")
        return

    user_id = int(user_input)
    blocked_users = load_blocked_users()
    
    if user_id == 1663567950:  # Admin ID'sini bloklashga urinishni tekshirish
        bot.send_message(message.chat.id, "❗️Siz Adminni bloklay olmaysiz.")
        bot.send_message(1663567950, f"❗️Sizni {message.chat.id} ID ga ega foydalanuvchi bloklashga harakat qildi\nUsername: @{bot.get_chat(message.chat.id).username}")
        return
    
    if user_id in blocked_users:
        bot.send_message(message.chat.id, f"❗️Foydalanuvchi {user_id} allaqachon bloklangan.")
    else:
        blocked_users.append(user_id)
        save_blocked_users(blocked_users)
        bot.send_message(message.chat.id, f"✅ Foydalanuvchi {user_id} muvaffaqiyatli bloklandi.")

# Foydalanuvchini blokdan chiqarish
def unblock_user(message):
    user_input = message.text.strip()  # Foydalanuvchi tomonidan kiritilgan xabarni olamiz
    if not user_input.isdigit():  # Agar xabar raqam bo'lmasa
        bot.send_message(message.chat.id, "❗️Bu ID ga ega foydalanuvchi topilmadi.")
        return

    user_id = int(user_input)
    blocked_users = load_blocked_users()
    
    if user_id in blocked_users:
        blocked_users.remove(user_id)
        save_blocked_users(blocked_users)
        bot.send_message(message.chat.id, f"✅ Foydalanuvchi {user_id} blokdan chiqarildi.")
    else:
        bot.send_message(message.chat.id, f"❗️Foydalanuvchi {user_id} bloklangan emas.")

def load_blocked_users():
    try:
        with open("blocked_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Agar fayl bo'lmasa yoki noto'g'ri bo'lsa, bo'sh ro'yxat qaytariladi

# Foydalanuvchining bloklanganligini tekshirish
def is_user_blocked(user_id):
    blocked_users = load_blocked_users()
    return user_id in blocked_users

# Foydalanuvchining xabarini qayta ishlash
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    # Agar foydalanuvchi bloklangan bo'lsa, xabar yuborishni to'xtatish
    if is_user_blocked(user_id):
        bot.send_message(message.chat.id, "🚫 Siz bloklangansiz! Botdan foydalanishingiz mumkin emas.")
        return  # Bloklangan foydalanuvchilar uchun boshqa amallar bajarilmaydi

    # Foydalanuvchi bloklanmagan bo'lsa, YouTube havolasini tekshiradi yoki boshqa xizmatlarni bajaradi
    url = message.text.strip()
    # Maxsus kodni tekshirish
    def is_special_code(message):
        return message.text.strip() == "A20050116a" #and user_id ==  1663567950
    # YouTube havolasi bo'lsa, qayta ishlash
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


# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query1(call):
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
        user_details = "\n".join([f"____________________\n{index + 1}. ID: {user['user_id']} \nName: {user['first_name']}, \nUsername: @{user.get('username', 'N/A')}, \nPhone: {user.get('phone_number', 'Not provided')}" for index, user in enumerate(data.values())])
        bot.send_message(call.message.chat.id, f"🥸To'liq foydalanuvchi ma'lumotlari: \n{user_details}")

    elif action == "send_messages":
        show_send_options(call)

    elif action == "send_to_one":
        msg = bot.send_message(call.message.chat.id, "❓Xabarni kimga yubormoqchisiz? Foydalanuvchi ID sini kiriting:")
        bot.register_next_step_handler(msg, send_to_one_user)

    elif action == "send_to_some":
        msg = bot.send_message(call.message.chat.id, "🙋‍♂️Xabarni yubormoqchi bo'lgan foydalanuvchilarning ID sini vergul bilan ajratib kiriting:")
        bot.register_next_step_handler(msg, send_to_some_users)

    elif action == "send_to_all":
        msg = bot.send_message(call.message.chat.id, "📝Yubormoqchi bo'lgan xabar, rasm yoki video faylni kiriting:")
        bot.register_next_step_handler(msg, send_to_all_users)

    elif action == "manage_block":
        show_block_menu(call)

    elif action == "block_user":
        msg = bot.send_message(call.message.chat.id, "🚫 Bloklamoqchi bo'lgan foydalanuvchi ID sini kiriting:")
        bot.register_next_step_handler(msg, block_user)

    elif action == "unblock_user":
        msg = bot.send_message(call.message.chat.id, "✅ Blokdan chiqarish uchun foydalanuvchi ID sini kiriting:")
        bot.register_next_step_handler(msg, unblock_user)

# Foydalanuvchilarga xabar yuborish funksiyalari
# 1 ta foydalanuvchiga yuborish funksiyasi
def send_to_one_user(message):
    try:
        user_id = int(message.text)
        # Foydalanuvchini tekshirish
        data = load_data()
        if user_id not in [user['user_id'] for user in data.values()]:
            bot.send_message(message.chat.id, f"❗️Kiritilgan ID ({user_id}) ga ega foydalanuvchi topilmadi.")
            return

        # Xabarni kiritish so'rovi
        msg = bot.send_message(message.chat.id, "📝Yubormoqchi bo'lgan xabar, rasm yoki video faylni kiriting:")
        bot.register_next_step_handler(msg, lambda m: send_content_to_user(m, user_id))

    except ValueError:
        bot.send_message(message.chat.id, "❗️Iltimos, haqiqiy foydalanuvchi ID sini kiriting.")


# Xabar yoki faylni yuborish funksiyasi
def send_content_to_user(message, user_id):
    try:
        if message.content_type == 'text':
            bot.send_message(user_id, message.text)
        elif message.content_type == 'photo':
            bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == 'video':
            bot.send_video(user_id, message.video.file_id, caption=message.caption)
        else:
            bot.send_message(message.chat.id, "❗️Faqat matn, rasm yoki video yuborishingiz mumkin.")
        
        # Xabar yuborilganidan so'ng tasdiqlash
        bot.send_message(message.chat.id, "✅ Xabar muvaffaqiyatli yuborildi.")

    except telebot.apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, f"❗️Kiritilgan ID ({user_id}) ga ega foydalanuvchi topilmadi yoki u botda mavjud emas.")
        
# Ma'lum foydalanuvchilarga xabar yuborish funksiyasi
def send_to_some_users(message):
    try:
        # Foydalanuvchi ID-larini vergul bilan ajratib olish
        user_ids = [int(id.strip()) for id in message.text.split(',')]
        msg = bot.send_message(message.chat.id, "📝Yubormoqchi bo'lgan xabar, rasm yoki video faylni kiriting:")
        bot.register_next_step_handler(msg, lambda m: send_content_to_multiple_users(m, user_ids))
    except ValueError:
        bot.send_message(message.chat.id, "❗️Iltimos, haqiqiy foydalanuvchi ID larini vergul bilan ajratib kiriting.")
        
# Xabar yoki faylni ma'lum foydalanuvchilarga yuborish funksiyasi
def send_content_to_multiple_users(message, user_ids):
    data = load_data()
    all_user_ids = [user['user_id'] for user in data.values()]
    
    success_count = 0
    failure_count = 0

    for user_id in user_ids:
        if user_id in all_user_ids:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(user_id, message.video.file_id, caption=message.caption)
                success_count += 1
            except telebot.apihelper.ApiTelegramException:
                failure_count += 1
        else:
            failure_count += 1
    
    # Natijani yuborish
    bot.send_message(
        message.chat.id, 
        f"✅ Xabar yuborildi:\n\n"
        f"🔹 Muvaffaqiyatli: {success_count} ta \n"
        f"🔸 Muvaffaqiyatsiz: {failure_count} ta "
    )
    
def send_to_all_users(message):
    data = load_data()
    for user in data.values():
        try:
            if message.content_type == 'text':
                bot.send_message(user['user_id'], message.text)
            elif message.content_type == 'photo':
                bot.send_photo(user['user_id'], message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(user['user_id'], message.video.file_id, caption=message.caption)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, f"❗️Foydalanuvchi {user['user_id']} ga xabar yuborilmadi, u botda mavjud emas.")
    bot.send_message(message.chat.id, "✅ Xabar belgilangan foydalanuvchilarga yuborildi.")

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

    elif action == "send_messages":
        bot.send_message(call.message.chat.id, "👇👇👇Kerakli bo'limni tanlang")

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





# Botni ishga tushirish
bot.polling(timeout=120, long_polling_timeout=20)


