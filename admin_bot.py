from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

TOKEN = "8483517921:AAFe5du2OsIAyeRa6IGmHFovgLCpRpKLg2I"
ADMIN_IDS = [8160020054]
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

USERS = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У тебя нет доступа к этому боту")
        return
    
    keyboard = [
        [KeyboardButton("👥 Список пользователей")],
        [KeyboardButton("📨 Отправить сообщение")],
        [KeyboardButton("🎁 Отправить подарок")],
        [KeyboardButton("🚫 Забанить")],
        [KeyboardButton("✅ Разбанить")],
        [KeyboardButton("⚠️ Предупреждение")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎛️ Админ-панель\n\nВыбери действие:",
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У тебя нет доступа")
        return
    
    if text == "👥 Список пользователей":
        USERS.clear()
        USERS.update(load_users())
        
        if not USERS:
            await update.message.reply_text("📭 Нет пользователей")
            return
        
        user_list = "👥 Список пользователей:\n\n"
        for uid, user_info in USERS.items():
            status = "🚫 Забанен" if user_info.get("banned") else "✅ Активен"
            warns = user_info.get("warns", 0)
            user_list += f"ID: {uid}\nИмя: {user_info['name']}\nСтатус: {status}\nПредупреждений: {warns}\n\n"
        
        await update.message.reply_text(user_list)
    
    elif text == "📨 Отправить сообщение":
        await update.message.reply_text("Отправь ID пользователя:")
        context.user_data['action'] = 'send_message'
    
    elif text == "🎁 Отправить подарок":
        await update.message.reply_text("Отправь ID пользователя:")
        context.user_data['action'] = 'send_gift'
    
    elif text == "🚫 Забанить":
        await update.message.reply_text("Отправь ID пользователя:")
        context.user_data['action'] = 'ban'
    
    elif text == "✅ Разбанить":
        await update.message.reply_text("Отправь ID пользователя:")
        context.user_data['action'] = 'unban'
    
    elif text == "⚠️ Предупреждение":
        await update.message.reply_text("Отправь ID пользователя:")
        context.user_data['action'] = 'warn'
    
    else:
        # Обработка действий
        action = context.user_data.get('action')
        
        if action == 'send_message':
            if 'target_user' not in context.user_data:
                context.user_data['target_user'] = text
                await update.message.reply_text("Отправь сообщение:")
            else:
                await update.message.reply_text(f"✅ Сообщение отправлено пользователю {context.user_data['target_user']}")
                context.user_data.clear()
        
        elif action == 'send_gift':
            if 'target_user' not in context.user_data:
                context.user_data['target_user'] = text
                await update.message.reply_text("Отправь текст подарка (ключ, код):")
            else:
                await update.message.reply_text(f"🎁 Подарок отправлен пользователю {context.user_data['target_user']}")
                context.user_data.clear()
        
        elif action == 'ban':
            try:
                target_id = str(int(text))
                if target_id in USERS:
                    USERS[target_id]["banned"] = True
                    save_users(USERS)
                    await update.message.reply_text(f"🚫 Пользователь {USERS[target_id]['name']} забанен!")
                else:
                    await update.message.reply_text("❌ Пользователь не найден")
                context.user_data.clear()
            except:
                await update.message.reply_text("❌ Неверный ID")
        
        elif action == 'unban':
            try:
                target_id = str(int(text))
                if target_id in USERS:
                    USERS[target_id]["banned"] = False
                    save_users(USERS)
                    await update.message.reply_text(f"✅ Пользователь {USERS[target_id]['name']} разбанен!")
                else:
                    await update.message.reply_text("❌ Пользователь не найден")
                context.user_data.clear()
            except:
                await update.message.reply_text("❌ Неверный ID")
        
        elif action == 'warn':
            try:
                target_id = str(int(text))
                if target_id in USERS:
                    USERS[target_id]["warns"] = USERS[target_id].get("warns", 0) + 1
                    warns = USERS[target_id]["warns"]
                    save_users(USERS)
                    await update.message.reply_text(f"⚠️ Предупреждение выдано ({warns}/3)")
                    
                    if warns >= 3:
                        USERS[target_id]["banned"] = True
                        save_users(USERS)
                        await update.message.reply_text(f"🚫 Пользователь автоматически забанен!")
                else:
                    await update.message.reply_text("❌ Пользователь не найден")
                context.user_data.clear()
            except:
                await update.message.reply_text("❌ Неверный ID")

def main():
    app = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60).write_timeout(60).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Админ-бот запущен...")
    app.run_polling(allowed_updates=["message"], drop_pending_updates=True)

if __name__ == "__main__":
    main()
