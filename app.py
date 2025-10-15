#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

DATA_FILE = 'registered_users.json'
UPLOAD_DIR = 'uploads'

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
GROUP_ID = os.getenv('GROUP_ID')

app = Flask(__name__, static_folder='web', static_url_path='/')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

os.makedirs(UPLOAD_DIR, exist_ok=True)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get('/')
def index():
    return send_from_directory('web', 'index.html')


@app.post('/api/register')
def register():
    # Basic required fields only
    fullname = request.form.get('fullname', '').strip()
    country = request.form.get('country', '').strip()
    city = request.form.get('city', '').strip()
    birthdate = request.form.get('birthdate', '').strip()
    phone = request.form.get('phone', '').strip()
    workplace = request.form.get('workplace', '').strip()
    specialty = request.form.get('specialty', '').strip()
    education = request.form.get('education', '').strip()
    nomination = request.form.get('nomination', '').strip()

    file = request.files.get('file')

    if not fullname:
        return jsonify({'ok': False, 'error': 'fullname is required'}), 400

    filename = None
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(save_path)

    users = load_data()

    user_info = {
        'user_id': request.headers.get('X-Telegram-Id') or 0,
        'username': request.headers.get('X-Telegram-Username') or "",
        'first_name': request.headers.get('X-Telegram-First') or "",
        'last_name': request.headers.get('X-Telegram-Last') or "",
        'language_code': request.headers.get('X-Telegram-Lang') or "",
        'registration_date': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        'fullname': fullname,
        'country': country,
        'city': city,
        'birthdate': birthdate,
        'phone': phone,
        'workplace': workplace,
        'specialty': specialty,
        'education': education,
        'nomination': nomination,
        'file': {'file_path': filename}
    }

    users.append(user_info)
    save_data(users)

    # Optional: notify admin/group via bot
    try:
        if BOT_TOKEN and GROUP_ID:
            bot = Bot(BOT_TOKEN)
            message = (
                "📋 <b>Yangi ro'yxatdan o'tish</b>\n\n"
                f"👤 <b>F.I.Sh:</b> {user_info['fullname']}\n"
                f"🌍 <b>Davlat:</b> {user_info['country']}\n"
                f"🏙️ <b>Shahar/Tuman:</b> {user_info['city']}\n"
                f"🎂 <b>Tug'ilgan sana:</b> {user_info['birthdate']}\n"
                f"📱 <b>Telefon:</b> {user_info['phone']}\n"
                f"🏢 <b>Ish joyi:</b> {user_info['workplace']}\n"
                f"💼 <b>Mutaxassislik:</b> {user_info['specialty']}\n"
                f"🎓 <b>Ma'lumot:</b> {user_info['education']}\n"
                f"🏆 <b>Nominatsiya:</b> {user_info['nomination']}\n\n"
                f"⏰ <b>Ro'yxatdan o'tgan vaqt:</b> {user_info['registration_date']}"
            )

            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='HTML')
    except Exception as e:
        # Non-fatal
        print(f"Notify error: {e}")

    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))


