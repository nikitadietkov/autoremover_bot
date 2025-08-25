import os
import telebot
import json
import random
from datetime import datetime
from telebot import types

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден!")

bot = telebot.TeleBot(TOKEN)

# 👑 Укажи свой Telegram ID
ADMIN_ID = 123456789   # <<< сюда вставь свой ID

bot.set_my_commands([
    types.BotCommand("addsize", "Добавить размер (раз в день)"),
    types.BotCommand("showstat", "Показать статистику"),
    types.BotCommand("help", "Список команд"),
    types.BotCommand("start", "Запустить бота заново"),
    types.BotCommand("setsize", "🔑 (Админ) Установить размер пользователю"),
    types.BotCommand("addbonus", "🔑 (Админ) Добавить бонус к размеру"),
    types.BotCommand("reset", "🔑 (Админ) Сбросить пользователя"),
])

DATA_FILE = "sizes.json"

# Загружаем данные
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sizes = json.load(f)
else:
    sizes = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sizes, f, ensure_ascii=False, indent=2)

# Рандомные фразы
funny_comments = [
    "⚡ Карандаш точится сам по себе!",
    "😏 Линейка уже трещит по швам!",
    "🔥 Осторожно, скоро в потолок упрётся!",
    "📐 Тебе пора покупать пенал побольше...",
    "🚀 Этот карандаш готов к полётам!",
    "😂 Да его уже можно на чертёжной доске использовать!",
]

def get_emoji(size):
    if size < 10:
        return "🍼"
    elif size < 20:
        return "😏"
    elif size < 30:
        return "🔥"
    else:
        return "🚀"

def get_title(size):
    if size < 10:
        return "Новичок"
    elif size < 20:
        return "Ученик линейки"
    elif size < 30:
        return "Повелитель карандашей"
    else:
        return "Легенда XXL"

HELP_TEXT = (
    "📖 Доступные команды:\n\n"
    "/addsize — добавить себе +0.5–10 см (раз в день)\n"
    "/showstat — показать рейтинг карандашей\n"
    "/help — список команд\n"
)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Привет! Это бот для измерения карандашей.\n"
        "Каждый день можно увеличивать свой карандаш.\n\n" + HELP_TEXT
    )

@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.reply_to(message, HELP_TEXT)

@bot.message_handler(commands=["addsize"])
def add_size(message):
    user_id = str(message.from_user.id)
    username = (message.from_user.username or "").lower()
    display_name = message.from_user.first_name or "Безымянный"

    today = datetime.now().strftime("%Y-%m-%d")

    if user_id in sizes and sizes[user_id].get("last_update") == today:
        bot.reply_to(message, "😅 Сегодня ты уже добавлял размер, приходи завтра!")
        return

    growth = round(random.uniform(0.5, 10.0), 1)

    if user_id not in sizes:
        sizes[user_id] = {
            "name": display_name,
            "username": username,
            "size": 0,
            "last_update": ""
        }

    sizes[user_id]["size"] += growth
    sizes[user_id]["last_update"] = today
    sizes[user_id]["name"] = display_name
    sizes[user_id]["username"] = username  # Обновим username на случай изменения

    save_data()

    comment = random.choice(funny_comments)
    emoji = get_emoji(sizes[user_id]["size"])
    title = get_title(sizes[user_id]["size"])

    bot.reply_to(
        message,
        f"{emoji} {display_name}, сегодня твой карандаш вырос на {growth} см!\n"
        f"Итого: {sizes[user_id]['size']:.1f} см.\n"
        f"🏅 Титул: {title}\n\n"
        f"{comment}\n\n"
        "👉 Подсказка: напиши /showstat, чтобы увидеть рейтинг!"
    )

@bot.message_handler(commands=["showstat"])
def show_stat(message):
    if not sizes:
        bot.reply_to(message, "📉 Пока нет статистики.")
        return

    stats = sorted(sizes.items(), key=lambda x: x[1]["size"], reverse=True)

    text += f"{i}. {emoji} {data.get('name')} (@{data.get('username', 'нет')}) -- {data['size']:.1f} см ({title}){crown}\n"
    for i, (user_id, data) in enumerate(stats, start=1):
        emoji = get_emoji(data["size"])
        title = get_title(data["size"])
        crown = " 👑" if i == 1 else ""
        text += f"{i}. {emoji} {data['name']} — {data['size']:.1f} см ({title}){crown}\n"

    text += "\n👉 Подсказка: используй /addsize, чтобы прокачать свой карандаш!"
    bot.reply_to(message, text)

# 🔑 АДМИН КОМАНДЫ
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

def get_key_by_username(username):
    # Приводим к нижнему регистру для устойчивости к регистру
    username = username.lower()
    for key in sizes:
        if sizes[key].get("username", "").lower() == username:
            return key
    return None

@bot.message_handler(commands=["setsize"])
def admin_setsize(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ Эта команда доступна только админу!")

    try:
        _, tag, new_size = message.text.split()
        tag = tag.lstrip("@").lower()
        new_size = float(new_size)

        key = get_key_by_username(tag)
        if not key:
            return bot.reply_to(message, f"⚠ Пользователь @{tag} не найден.")

        sizes[key]["size"] = new_size
        save_data()
        bot.reply_to(message, f"✅ Размер пользователя @{tag} установлен на {new_size} см.")
    except:
        bot.reply_to(message, "⚠ Использование: /setsize @username размер")

@bot.message_handler(commands=["addbonus"])
def admin_addbonus(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ Эта команда доступна только админу!")

    try:
        _, tag, bonus = message.text.split()
        tag = tag.lstrip("@").lower()
        bonus = float(bonus)

        key = get_key_by_username(tag)
        if not key:
            return bot.reply_to(message, f"⚠ Пользователь @{tag} не найден.")

        sizes[key]["size"] += bonus
        save_data()
        bot.reply_to(message, f"🎁 Пользователю @{tag} добавлено {bonus} см!")
    except:
        bot.reply_to(message, "⚠ Использование: /addbonus @username число")

@bot.message_handler(commands=["reset"])
def admin_reset(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ Эта команда доступна только админу!")

    try:
        _, tag = message.text.split()
        tag = tag.lstrip("@").lower()

        key = get_key_by_username(tag)
        if not key:
            return bot.reply_to(message, f"⚠ Пользователь @{tag} не найден.")

        sizes[key]["size"] = 0
        sizes[key]["last_update"] = ""
        save_data()
        bot.reply_to(message, f"♻ Прогресс пользователя @{tag} сброшен!")
    except:
        bot.reply_to(message, "⚠ Использование: /reset @username")

# Отключаем Webhook, чтобы можно было использовать polling
bot.remove_webhook()
print("Бот запущен...")
bot.infinity_polling()
