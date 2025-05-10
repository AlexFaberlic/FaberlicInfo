import json
import os
from background import keep_alive #импорт функции для поддержки работоспособности
import pip
pip.main(['install', 'pytelegrambotapi'])
import telebot
from telebot.types import BotCommand


# Get the bot token from environment variable
token = os.getenv("TELEGRAM_BOT_TOKEN", "")

bot = telebot.TeleBot(token)

# @bot.message_handler(content_types=['text'])
# def get_text_message(message):
#   bot.send_message(message.from_user.id,message.text)
# # echo-функция, которая отвечает на любое текстовое сообщение таким же текстом   

commands = [
    BotCommand("1rub", "Подарок за 1 рубль"),
    BotCommand("20_26", "Скидка до 26%"),
    BotCommand("order", "Оформить заказ"),
    BotCommand("delivery", "Выбрать доставку"),
    BotCommand("change", "Изменить заказ"),
    BotCommand("terms", "Сроки доставки"),
    BotCommand("earn", "Хочу зарабатывать"),
    BotCommand("feedback", "Как писать в 'Обратную связь'"),
]

bot.set_my_commands(commands)

# Predefined responses for each command
responses = {
    "1rub": "🎁 Подарок за 1 рубль — узнайте, как получить!",
    "20_26": "🔖 Скидка до 26% — воспользуйтесь выгодными предложениями!",
    "order": "🛒 Как оформить заказ — подробная инструкция.",
    "delivery": "🚚 Выбор доставки — все способы доставки.",
    "change": "✏️ Изменение заказа — пошаговое руководство.",
    "terms": "⏳ Сроки доставки — когда ждать заказ?",
    "earn": "💰 Хочу зарабатывать — узнайте больше о возможностях.",
    "feedback": "✍️ Обратная связь — как написать в поддержку."
}

# Load JSON data from a file
with open("videos.json", "r", encoding="utf-8") as file:
    data = json.load(file)

welcome_message = """
📹 *Помощник клиента Фаберлик - обучающие видео*
Нажмите на кнопку Меню в нижней части экрана и выберите из списка обучающее видео.
"""
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(commands=list(responses.keys()))
def command_handler(message):
    """Handles multiple commands in a single function"""
    send_video(message)

def send_video(message):
    video_id = message.text[1:]
    caption = responses.get(video_id)
    video = find_video_by_id(video_id)
    if video is not None:
        video_code = video["video_code"]
        description = video["description"]
    else:
        video_code = None
        description = f"🔍 Не найдено видео с кодом: {video_id}"

    bot.send_message(message.chat.id, 
                     description,
                     disable_notification=True)
    if video_code is not None:
        video_url = f"https://drive.google.com/uc?export=download&confirm=t&id={video_code}"
        bot.send_video(message.chat.id, 
                       video_url, 
                       caption=caption, 
                       disable_notification=True)
    
# Function to find a video by ID
def find_video_by_id(video_id):
    for video in data["videos"]:
        if video["id"] == video_id:
            return video
    return None  # If not found
    
keep_alive()#запускаем flask-сервер в отдельном потоке
bot.polling(non_stop=True, interval=0) #запуск бота