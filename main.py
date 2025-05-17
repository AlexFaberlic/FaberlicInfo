import bot
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    if bot.bot_check():
        return "I'm alive and bot is checked"
    else:
        print("Problems with bot")

app.run(host='0.0.0.0', port=80)