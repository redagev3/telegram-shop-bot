from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import json

load_dotenv()
TOKEN = "8355969427:AAE90WG33-Jdrm5Pg915ZziUeZg3kyCblSg"
CHANNEL_ID = -1003288178338
WHITELIST = [8160020054]
ADMINS = [8160020054]
YOUR_USER_ID = 8160020054
USERS_FILE = "users.json"

# Загружаем пользователей
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Сохраняем пользователей
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

USERS = load_users()

FILES = {
    "system1": {
        "name": "🎮 [A-Chassis 1.7.1 Sochi County Full FIX]",
        "url": "https://drive.google.com/uc?id=1example1&export=download",
        "description": "Профессиональная система для Roblox Studio"
    },
    "system2": {
        "name": "🎮 Roblox System #2",
        "url": "https://drive.google.com/uc?id=1example2&export=download",
        "description": "Продвинутая система с интеграциями"
    },
    "system3": {
        "name": "🎮 Roblox System #3",
        "url": "https://drive.google.com/uc?id=1example3&export=download",
        "description": "Легкая и быстрая система"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name
    
    # Сохраняем пользователя
    if user_id not in USERS:
        USERS[user_id] = {
            "name": user_name,
            "banned": False,
            "warns": 0,
            "downloads": 0
        }
        save_users(USERS)
    
    keyboard = [
        [KeyboardButton("👤 Профиль")],
        [KeyboardButton("💾 Сливы")],
        [KeyboardButton("📞 Поддержка")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎉 Добро пожаловать!\n\nВыбери раздел:",
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name
    
    # Сохраняем пользователя при каждом сообщении
    if user_id not in USERS:
        USERS[user_id] = {
            "name": user_name,
            "banned": False,
            "warns": 0,
            "downloads": 0
        }
        save_users(USERS)
    
    # Проверяем бан
    if USERS.get(user_id, {}).get("banned"):
        await update.message.reply_text("🚫 Ты забанен и не можешь использовать бота")
        return

    if text == "👤 Профиль":
        user_id = str(update.message.from_user.id)
        from datetime import datetime
        
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        role_text = ""
        if int(user_id) in ADMINS:
            role_text = f"\n🎖️ Роль: 👑 Админ"
        
        keyboard = [[KeyboardButton("⬅️ Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_photo(
            photo="https://drive.google.com/uc?id=1lLD2UGFbJaGM1fBQ7Vz0a5-l_mP5ciDQ&export=view",
            caption=f"👤 Ваш профиль:\n\n"
                    f"📆 Последний вход: {current_time}\n\n"
                    f"🔑 ID: {user_id}\n"
                    f"💎 Никнейм: @{update.message.from_user.username or 'не указан'}\n"
                    f"📥 Скачиваний: {USERS.get(user_id, {}).get('downloads', 0)}{role_text}",
            reply_markup=reply_markup
        )

    elif text == "💾 Сливы":
        user_id = str(update.message.from_user.id)
        
        # Проверяем забан
        if USERS.get(user_id, {}).get("banned"):
            await update.message.reply_text("🚫 Ты забанен и не можешь скачивать файлы")
            return
            keyboard = []
            for file_id, file_info in FILES.items():
                keyboard.append([KeyboardButton(file_info["name"])])
            keyboard.append([KeyboardButton("⬅️ Назад")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                "💾 Доступные файлы:",
                reply_markup=reply_markup
            )
            context.user_data["in_files"] = True
            return
        
        is_subscribed = False
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ["member", "administrator", "creator"]:
                is_subscribed = True
        except:
            is_subscribed = False
        
        if not is_subscribed:
            keyboard = [[KeyboardButton("⬅️ Назад")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "❌ Ты не подписан на канал!\n\n"
                "Подпишись: https://t.me/bitocer\n\n"
                "После подписки попробуй снова",
                reply_markup=reply_markup
            )
            return

        keyboard = []
        for file_id, file_info in FILES.items():
            keyboard.append([KeyboardButton(file_info["name"])])
        keyboard.append([KeyboardButton("⬅️ Назад")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "💾 Доступные файлы:",
            reply_markup=reply_markup
        )
        context.user_data["in_files"] = True

    elif text in [file_info["name"] for file_info in FILES.values()]:
        file_info = None
        for f_info in FILES.values():
            if f_info["name"] == text:
                file_info = f_info
                break

        if file_info:
            if 'downloads' not in context.user_data:
                context.user_data['downloads'] = 0
            context.user_data['downloads'] += 1
            
            keyboard = [[KeyboardButton("⬅️ Назад")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f"{file_info['name']}\n\n"
                f"{file_info['description']}\n\n"
                f"Ссылка: {file_info['url']}",
                reply_markup=reply_markup
            )

    elif text == "📞 Поддержка":
        keyboard = [[KeyboardButton("⬅️ Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_photo(
            photo="https://drive.google.com/uc?id=1hzzbSlEKxu39ve_GrtjaHiiPCKFZEP1p&export=view",
            caption="📞 Поддержка\n\n"
                    "Напиши @YOUR_USERNAME если есть вопросы",
            reply_markup=reply_markup
        )

    elif text == "⬅️ Назад":
        keyboard = [
            [KeyboardButton("👤 Профиль")],
            [KeyboardButton("💾 Сливы")],
            [KeyboardButton("📞 Поддержка")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "🎉 Добро пожаловать!\n\nВыбери раздел:",
            reply_markup=reply_markup
        )
        context.user_data["in_files"] = False

async def send_ad(context: ContextTypes.DEFAULT_TYPE):
    ad_message = (
        "🎉 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🎉\n\n"
        "📢 ПРИСОЕДИНЯЙСЯ К НАШЕМУ КАНАЛУ!\n\n"
        "💎 Эксклюзивные сливы и много чего другого\n"
        "🎮 Профессиональные скрипты и коды\n"
        "⚡ Регулярные обновления и новинки\n"
        "🔥 Только лучшее для разработчиков\n\n"
        "👉 https://t.me/bitocer\n\n"
        "🎉 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🎉"
    )
    
    try:
        await context.bot.send_message(
            chat_id=YOUR_USER_ID,
            text=ad_message
        )
    except Exception as e:
        print(f"Ошибка при отправке рекламы: {e}")

def main():
    app = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60).write_timeout(60).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.job_queue.run_repeating(send_ad, interval=300, first=10)

    print("✅ Бот запущен...")
    app.run_polling(allowed_updates=["message"], drop_pending_updates=True)

if __name__ == "__main__":
    main()
