#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, \
    ConversationHandler
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv('BOT_TOKEN', '7729290828:AAFJl5pxtdnyvA6czTtcDQ3iexVq_Fd7_o0')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '7605860772')
GROUP_ID = os.getenv('GROUP_ID', '-1002930763309')

# Conversation states
FULLNAME, COUNTRY, BIRTHDATE, WORKPLACE, SPECIALTY, EDUCATION, NOMINATION, CREATIVE_WORK = range(8)

# Ma'lumotlar fayli
DATA_FILE = 'registered_users.json'

# Global ma'lumotlar
registered_users = []

# Ma'lumot darajalari
EDUCATION_LEVELS = [
    "O'rta ta'lim",
    "O'rta maxsus ta'lim",
    "Oliy ta'lim (Bakalavr)",
    "Oliy ta'lim (Magistr)",
    "Oliy ta'lim (Doktorantura)"
]

# Nominatsiyalar
NOMINATIONS = [
    "Eng tashabuskor o'zbek tili ustozi",
    "Eng yaxshi insho",
    "Eng yaxshi videorolik"
]


def load_data():
    global registered_users
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                registered_users = json.load(f)
        print("Ma'lumotlar yuklandi")
    except Exception as e:
        print(f"Xato: {e}")


def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=2)
        print("Ma'lumotlar saqlandi")
    except Exception as e:
        print(f"Xato: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🎉 Xush kelibsiz! Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni to'ldiring.\n\n"
        "📝 Iltimos, ismingiz, familiyangiz va sharifingizni kiriting:\n"
        "(Masalan: Ibragimov Samandar Iskandar o'g'li)"
    )

    return FULLNAME


async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fullname'] = update.message.text

    await update.message.reply_text("🌍 Hozirda qaysi davlatda istiqomat qilasiz?")

    return COUNTRY


async def country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text

    await update.message.reply_text(
        "📅 Tug'ilgan sanangizni kiriting (dd.mm.yyyy formatida):\n"
        "(Masalan: 04.06.1994)"
    )

    return BIRTHDATE


async def birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        datetime.strptime(text, '%d.%m.%Y')
        context.user_data['birthdate'] = text

        await update.message.reply_text("🏢 Ish yoki o'qish joyingizni kiriting:")

        return WORKPLACE
    except ValueError:
        await update.message.reply_text(
            "❌ Noto'g'ri format! Iltimos, dd.mm.yyyy formatida kiriting.\n"
            "(Masalan: 04.06.1994)"
        )
        return BIRTHDATE


async def workplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['workplace'] = update.message.text

    await update.message.reply_text("💼 Mutaxassisligingizni kiriting:")

    return SPECIALTY


async def specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['specialty'] = update.message.text

    keyboard = [[InlineKeyboardButton(level, callback_data=f"edu_{i}")]
                for i, level in enumerate(EDUCATION_LEVELS)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎓 Ma'lumot darajangizni tanlang:",
        reply_markup=reply_markup
    )

    return EDUCATION


async def education_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    edu_index = int(query.data.split('_')[1])
    context.user_data['education'] = EDUCATION_LEVELS[edu_index]

    await query.edit_message_text(f"✅ Tanlandi: {EDUCATION_LEVELS[edu_index]}")

    keyboard = [[InlineKeyboardButton(nom, callback_data=f"nom_{i}")]
                for i, nom in enumerate(NOMINATIONS)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🏆 Nominatsiyani tanlang:",
        reply_markup=reply_markup
    )

    return NOMINATION


async def education_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Education bosqichida noto'g'ri input"""
    await update.message.reply_text(
        "❌ Iltimos, yuqoridagi tugmalardan birini bosing!\n\n"
        "🎓 Ma'lumot darajangizni tugmalar orqali tanlang."
    )
    return EDUCATION


async def nomination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    nom_index = int(query.data.split('_')[1])
    context.user_data['nomination'] = NOMINATIONS[nom_index]

    await query.edit_message_text(f"✅ Tanlandi: {NOMINATIONS[nom_index]}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📎 Ijodiy ishingizni yuboring:\n(Video, audio, PDF, PowerPoint yoki boshqa hujjat)"
    )

    return CREATIVE_WORK


async def nomination_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nomination bosqichida noto'g'ri input"""
    await update.message.reply_text(
        "❌ Iltimos, yuqoridagi tugmalardan birini bosing!\n\n"
        "🏆 Nominatsiyani tugmalar orqali tanlang."
    )
    return NOMINATION


async def creative_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Agar text yuborilsa
    if update.message.text:
        await update.message.reply_text(
            "❌ Iltimos, matn emas, <b>fayl</b> yuboring!\n\n"
            "📎 Quyidagi fayl turlarini yuborishingiz mumkin:\n"
            "• 🎥 Video fayl\n"
            "• 🎵 Audio fayl\n"
            "• 📄 PDF hujjat\n"
            "• 📊 PowerPoint (pptx)\n"
            "• 📝 Word hujjat\n"
            "• 📁 Boshqa hujjatlar\n\n"
            "🔄 Iltimos, fayl yuboring.",
            parse_mode='HTML'
        )
        return CREATIVE_WORK

    # Agar rasm yuborilsa
    if update.message.photo:
        await update.message.reply_text(
            "❌ Rasm emas, iltimos to'g'ri <b>fayl</b> yuboring!\n\n"
            "📎 Quyidagi fayl turlarini yuborishingiz mumkin:\n"
            "• 🎥 Video fayl\n"
            "• 🎵 Audio fayl\n"
            "• 📄 PDF hujjat\n"
            "• 📊 PowerPoint (pptx)\n"
            "• 📝 Word hujjat\n"
            "• 📁 Boshqa hujjatlar\n\n"
            "🔄 Iltimos, qaytadan urinib ko'ring.",
            parse_mode='HTML'
        )
        return CREATIVE_WORK

    # Faqat document, video, audio qabul qilish
    if not (update.message.document or update.message.video or update.message.audio):
        await update.message.reply_text(
            "❌ Iltimos, to'g'ri fayl turini yuboring!\n\n"
            "📎 Quyidagi fayl turlarini yuborishingiz mumkin:\n"
            "• 🎥 Video fayl\n"
            "• 🎵 Audio fayl\n"
            "• 📄 PDF hujjat\n"
            "• 📊 PowerPoint (pptx)\n"
            "• 📝 Word hujjat\n"
            "• 📁 Boshqa hujjatlar\n\n"
            "🔄 Iltimos, qaytadan urinib ko'ring.",
            parse_mode='HTML'
        )
        return CREATIVE_WORK

    file_info = {}

    if update.message.document:
        file_info = {
            'file_id': update.message.document.file_id,
            'file_type': 'document',
            'file_name': update.message.document.file_name
        }
    elif update.message.video:
        file_info = {
            'file_id': update.message.video.file_id,
            'file_type': 'video',
            'file_name': 'video'
        }
    elif update.message.audio:
        file_info = {
            'file_id': update.message.audio.file_id,
            'file_type': 'audio',
            'file_name': 'audio'
        }

    context.user_data['file'] = file_info

    user_info = {
        'user_id': user.id,
        'username': user.username or "Username yo'q",
        'registration_date': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
    }
    user_info.update(context.user_data)

    registered_users.append(user_info)
    save_data()

    # Ma'lumotlarni ko'rsatish
    await update.message.reply_text(
        "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        "📋 Sizning ma'lumotlaringiz:\n"
        f"👤 F.I.Sh: {user_info['fullname']}\n"
        f"🌍 Davlat: {user_info['country']}\n"
        f"📅 Tug'ilgan sana: {user_info['birthdate']}\n"
        f"🏢 Ish joyi: {user_info['workplace']}\n"
        f"💼 Mutaxassislik: {user_info['specialty']}\n"
        f"🎓 Ma'lumot: {user_info['education']}\n"
        f"🏆 Nominatsiya: {user_info['nomination']}"
    )

    # Yuborgan faylni qaytadan ko'rsatish
    await update.message.reply_text("📎 Sizning ijodiy ishingiz:")

    if file_info['file_type'] == 'video':
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=file_info['file_id'],
            caption=f"🎥 Video fayl: {file_info['file_name']}"
        )
    elif file_info['file_type'] == 'audio':
        await context.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=file_info['file_id'],
            caption=f"🎵 Audio fayl: {file_info['file_name']}"
        )
    else:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file_info['file_id'],
            caption=f"📄 Hujjat: {file_info['file_name']}"
        )

    await update.message.reply_text(
        "✅ Ma'lumotlaringiz administratorga yuborildi.\n"
        "Rahmat! 🙏"
    )

    await send_to_admin(context, user_info)

    return ConversationHandler.END


async def send_to_admin(context: ContextTypes.DEFAULT_TYPE, user_info: dict):
    print(f"GROUP_ID ishlatilmoqda: {GROUP_ID}")
    print(f"ADMIN_CHAT_ID ishlatilmoqda: {ADMIN_CHAT_ID}")

    try:
        message = (
            "📋 <b>Yangi ro'yxatdan o'tish</b>\n\n"
            f"👤 <b>F.I.Sh:</b> {user_info['fullname']}\n"
            f"🌍 <b>Davlat:</b> {user_info['country']}\n"
            f"🎂 <b>Tug'ilgan sana:</b> {user_info['birthdate']}\n"
            f"📞 <b>Telegram:</b> @{user_info['username']}\n"
            f"📱 <b>Qo'shimcha:</b> {user_info['birthdate'].replace('.', '')}\n"
            f"🏢 <b>Ish joyi:</b> {user_info['workplace']}\n"
            f"💼 <b>Mutaxassislik:</b> {user_info['specialty']}\n"
            f"🎓 <b>Ma'lumot:</b> {user_info['education']}\n"
            f"🏆 <b>Nominatsiya:</b> {user_info['nomination']}\n\n"
            f"⏰ <b>Ro'yxatdan o'tgan vaqt:</b> {user_info['registration_date']}"
        )

        file_info = user_info['file']

        # Tasdiqlash tugmalarini qo'shish
        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user_info['user_id']}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_info['user_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = None

        if file_info['file_type'] == 'video':
            sent_message = await context.bot.send_video(
                chat_id=GROUP_ID,
                video=file_info['file_id'],
                caption=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        elif file_info['file_type'] == 'audio':
            sent_message = await context.bot.send_audio(
                chat_id=GROUP_ID,
                audio=file_info['file_id'],
                caption=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            sent_message = await context.bot.send_document(
                chat_id=GROUP_ID,
                document=file_info['file_id'],
                caption=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

        # Xabar ID ni saqlash
        if sent_message:
            # Guruh username yoki ID dan link yaratish
            group_id_str = str(GROUP_ID).replace('-100', '')
            message_link = f"https://t.me/c/{group_id_str}/{sent_message.message_id}"

            # User ma'lumotlariga link qo'shish
            for user in registered_users:
                if user['user_id'] == user_info['user_id']:
                    user['message_link'] = message_link
                    user['message_id'] = sent_message.message_id
                    break

            save_data()

        print("Adminga yuborildi")
    except Exception as e:
        print(f"Admin xato: {e}")


async def approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Tasdiqlandi!")
    await query.edit_message_reply_markup(reply_markup=None)


async def reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❌ Rad etildi!")
    await query.edit_message_reply_markup(reply_markup=None)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    print(f"Export so'raldi. User ID: {user_id}")
    print(f"Admin ID: {ADMIN_CHAT_ID}")
    print(f"Tekshiruv: {user_id} == {ADMIN_CHAT_ID} ? {user_id == ADMIN_CHAT_ID}")

    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text(f"❌ Sizda ruxsat yo'q!\nSizning ID: {user_id}\nKerakli ID: {ADMIN_CHAT_ID}")
        return

    print(f"Ro'yxatdan o'tganlar soni: {len(registered_users)}")

    if not registered_users:
        await update.message.reply_text("📊 Hozircha ro'yxatdan o'tgan foydalanuvchilar yo'q.")
        return

    try:
        await update.message.reply_text("⏳ Excel fayli tayyorlanmoqda...")
        print("Excel yaratish boshlandi...")

        # Excel fayli yaratish
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ro'yxatdan o'tganlar"

        # Sarlavha stilini sozlash
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Border
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Sarlavhalar
        headers = [
            "№", "F.I.Sh", "Davlat", "Tug'ilgan sana",
            "Ish joyi", "Mutaxassislik", "Ma'lumot", "Nominatsiya",
            "Telegram", "Ro'yxatdan o'tgan vaqt", "Ijodiy ish"
        ]

        # Sarlavhalarni yozish
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = thin_border

        print("Sarlavhalar yozildi...")

        # Ma'lumotlarni yozish
        for row_num, user in enumerate(registered_users, 2):
            # Ijodiy ish linkini olish
            work_link = user.get('message_link', 'Link yo\'q')

            data = [
                row_num - 1,
                user['fullname'],
                user['country'],
                user['birthdate'],
                user['workplace'],
                user['specialty'],
                user['education'],
                user['nomination'],
                f"@{user['username']}",
                user['registration_date'],
                work_link
            ]

            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                cell.border = thin_border

                # Agar link bo'lsa, uni hyperlink qilish
                if col_num == 11 and work_link != 'Link yo\'q':
                    cell.hyperlink = work_link
                    cell.style = "Hyperlink"

        print("Ma'lumotlar yozildi...")

        # Ustunlar kengligini sozlash
        column_widths = [5, 25, 15, 15, 25, 20, 25, 30, 15, 20, 50]
        for col_num, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = width

        # Qatorlar balandligini sozlash
        ws.row_dimensions[1].height = 30
        for row_num in range(2, len(registered_users) + 2):
            ws.row_dimensions[row_num].height = 25

        # Faylni saqlash
        excel_filename = f"royxat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(excel_filename)
        print(f"Excel fayl saqlandi: {excel_filename}")

        # Excel faylni yuborish
        with open(excel_filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 Jami {len(registered_users)} ta foydalanuvchi\n\n✅ Excel formatda",
                filename=excel_filename
            )

        print("Excel yuborildi!")
        os.remove(excel_filename)
        print("Excel fayl o'chirildi")

        # Text faylni ham yuborish (opsional)
        export_text = "📊 RO'YXATDAN O'TGAN FOYDALANUVCHILAR\n"
        export_text += "=" * 40 + "\n\n"

        for i, user in enumerate(registered_users, 1):
            work_link = user.get('message_link', 'Link yo\'q')

            export_text += f"{i}. 👤 {user['fullname']}\n"
            export_text += f"   🌍 Davlat: {user['country']}\n"
            export_text += f"   📅 Tug'ilgan sana: {user['birthdate']}\n"
            export_text += f"   🏢 Ish joyi: {user['workplace']}\n"
            export_text += f"   💼 Mutaxassislik: {user['specialty']}\n"
            export_text += f"   🎓 Ma'lumot: {user['education']}\n"
            export_text += f"   🏆 Nominatsiya: {user['nomination']}\n"
            export_text += f"   📞 Telegram: @{user['username']}\n"
            export_text += f"   ⏰ Vaqt: {user['registration_date']}\n"
            export_text += f"   📎 Ijodiy ish: {work_link}\n"
            export_text += "   " + "-" * 35 + "\n\n"

        filename = f"royxat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(export_text)

        with open(filename, 'rb') as txt_file:
            await update.message.reply_document(
                document=txt_file,
                caption="📄 Text formatda",
                filename=filename
            )

        print("Text yuborildi!")
        os.remove(filename)

        print("✅ Export muvaffaqiyatli tugadi!")

    except Exception as e:
        print(f"❌ Export xatosi: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Xatolik yuz berdi:\n{str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Ro'yxatdan o'tish bekor qilindi.\n"
        "Qaytadan boshlash uchun /start buyrug'ini yuboring."
    )
    return ConversationHandler.END


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruh yoki chat ID ni olish"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title or "Private chat"

    await update.message.reply_text(
        f"📊 Chat ma'lumotlari:\n\n"
        f"🆔 Chat ID: <code>{chat_id}</code>\n"
        f"📝 Chat type: {chat_type}\n"
        f"📌 Chat nomi: {chat_title}\n\n"
        f"ID ni nusxalash uchun bosing ☝️",
        parse_mode='HTML'
    )


def main():
    print("Bot ishga tushmoqda...")
    load_data()

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FULLNAME: [
                CommandHandler('start', start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, fullname),
                MessageHandler(filters.ALL, fullname)
            ],
            COUNTRY: [
                CommandHandler('start', start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, country),
                MessageHandler(filters.ALL, country)
            ],
            BIRTHDATE: [
                CommandHandler('start', start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate),
                MessageHandler(filters.ALL, birthdate)
            ],
            WORKPLACE: [
                CommandHandler('start', start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, workplace),
                MessageHandler(filters.ALL, workplace)
            ],
            SPECIALTY: [
                CommandHandler('start', start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, specialty),
                MessageHandler(filters.ALL, specialty)
            ],
            EDUCATION: [
                CommandHandler('start', start),
                CallbackQueryHandler(education_callback, pattern='^edu_'),
                MessageHandler(filters.ALL, education_invalid_input)
            ],
            NOMINATION: [
                CommandHandler('start', start),
                CallbackQueryHandler(nomination_callback, pattern='^nom_'),
                MessageHandler(filters.ALL, nomination_invalid_input)
            ],
            CREATIVE_WORK: [
                CommandHandler('start', start),
                MessageHandler(filters.Document.ALL | filters.VIDEO | filters.AUDIO, creative_work),
                MessageHandler(filters.ALL, creative_work)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('export', export_command))
    application.add_handler(CommandHandler('chatid', get_chat_id))
    application.add_handler(CallbackQueryHandler(approve_callback, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(reject_callback, pattern='^reject_'))

    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()