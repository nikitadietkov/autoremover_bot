import os
import telebot
import json
import random
from datetime import datetime

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден!")

bot = telebot.TeleBot(TOKEN)

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

@bot.message_handler(commands=["addSize"])
def add_size(message):
    user_id = str(message.from_user.id)
    username = message.from_user.first_name or "Безымянный"

    today = datetime.now().strftime("%Y-%m-%d")

    # Проверка, добавлял ли пользователь сегодня
    if user_id in sizes and sizes[user_id].get("last_update") == today:
        bot.reply_to(message, "😅 Сегодня ты уже добавлял размер, приходи завтра!")
        return

    # Рандомное число 0.5–5.0 см
    growth = round(random.uniform(0.5, 5.0), 1)

    if user_id not in sizes:
        sizes[user_id] = {"name": username, "size": 0, "last_update": ""}

    sizes[user_id]["size"] += growth
    sizes[user_id]["last_update"] = today
    sizes[user_id]["name"] = username

    save_data()

    comment = random.choice(funny_comments)
    emoji = get_emoji(sizes[user_id]["size"])
    title = get_title(sizes[user_id]["size"])

    bot.reply_to(
        message,
        f"{emoji} {username}, сегодня твой карандаш вырос на {growth} см!\n"
        f"Итого: {sizes[user_id]['size']:.1f} см.\n"
        f"🏅 Титул: {title}\n\n"
        f"{comment}"
    )

@bot.message_handler(commands=["showStat"])
def show_stat(message):
    if not sizes:
        bot.reply_to(message, "📉 Пока нет статистики.")
        return

    # Сортировка по размеру
    stats = sorted(sizes.items(), key=lambda x: x[1]["size"], reverse=True)

    text = "📊 Статистика размеров карандашей:\n\n"
    for i, (user_id, data) in enumerate(stats, start=1):
        emoji = get_emoji(data["size"])
        title = get_title(data["size"])
        text += f"{i}. {emoji} {data['name']} — {data['size']:.1f} см ({title})\n"

    bot.reply_to(message, text)

# Отключаем Webhook, чтобы можно было использовать polling
bot.remove_webhook()

print("Бот запущен...")
bot.infinity_polling()


