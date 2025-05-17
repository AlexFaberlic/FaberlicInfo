import threading
import telebot
from telebot.types import BotCommand
import json
import os
import pip
import re

pip.main(['install', 'pytelegrambotapi'])

# Get the bot token from environment variable
token = os.getenv("TELEGRAM_BOT_TOKEN", "")

bot = telebot.TeleBot(token)

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
Нажмите на кнопку Меню в нижней части экрана и выберите из списка обучающее видео. Или напишите ключевое слово для поиска, например, <b><u>заказ</u></b>.
"""


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 
                     welcome_message,
                     parse_mode='HTML')


@bot.message_handler(commands=list(responses.keys()))
def command_handler(message):
    """Handles multiple commands in a single function"""
    send_video(message)


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    command_codes = get_command_codes(message.text)
    # Call send_video for each matching code
    for code in command_codes:
        if code in responses:
            message_result_text = responses[code]
            words = message.text.lower().split()
            for word in words:
                message_result_text = re.sub(f'(?i){word}', highlight_match, message_result_text)

            description = f"Команда /{code} - {message_result_text}"
            bot.send_message(message.chat.id,
                             description,
                             parse_mode='HTML',
                             disable_notification=True)
    if command_codes == []:
        not_found_message = f"Слово ''{message.text}'' не найдено"
        bot.send_message(message.chat.id, not_found_message,
                         disable_notification=True)

def highlight_match(match):
    return f'<b><u>{match.group(0)}</u></b>'

def get_command_codes(description_substring):
    words = description_substring.lower().split()
    matching_codes = []
    
    for code, description in responses.items():
        description_lower = description.lower()
        if any(word in description_lower for word in words):
            matching_codes.append(code)
    return matching_codes


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

    bot.send_message(message.chat.id, description, disable_notification=True)
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


def bot_check():
    return bot.get_me()


def bot_runner():
    bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
