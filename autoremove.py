import os
import telebot

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден!")

bot = telebot.TeleBot(TOKEN)

# Отключаем Webhook, чтобы можно было использовать polling
bot.remove_webhook()

@bot.message_handler(content_types=[
    "new_chat_photo", "delete_chat_photo",
    "new_chat_title", "pinned_message"
])
def delete_service_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        print(f"Удалено сообщение в чате {message.chat.id}")
    except Exception as e:
        print("Ошибка:", e)

print("Бот запущен...")
bot.infinity_polling()
