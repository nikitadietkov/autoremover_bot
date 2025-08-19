import telebot

TOKEN = "8313689826:AAHLlcgQkVNogy0Z223_MhWu8KClyqBRexg"
bot = telebot.TeleBot(TOKEN)

# Обрабатываем все сервисные сообщения
@bot.message_handler(content_types=[
    "new_chat_photo", "delete_chat_photo",
    "new_chat_title", "pinned_message"
])
def delete_service_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print("Ошибка при удалении:", e)

bot.polling(none_stop=True)
