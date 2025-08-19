import os
import telebot

TOKEN = os.getenv("TOKEN")  # Токен берем из переменных окружения
if not TOKEN:
    raise ValueError("❌ Не найден TOKEN! Добавь его в Railway Variables.")

bot = telebot.TeleBot(TOKEN)

# Сервисные сообщения (смена фото, названия, закрепы и т.д.)
@bot.message_handler(content_types=[
    "new_chat_photo", "delete_chat_photo",
    "new_chat_title", "pinned_message"
])
def delete_service_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        print(f"🗑 Удалено системное сообщение в чате {message.chat.id}")
    except Exception as e:
        print("Ошибка при удалении:", e)

print("✅ Бот запущен и работает...")
bot.infinity_polling()
