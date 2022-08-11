import os
from pathlib import Path
from io import BytesIO
from pytube import YouTube
from pytube.exceptions import RegexMatchError

import telebot
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .routers import streams
from dotenv import load_dotenv, find_dotenv

import logging

# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)
app = FastAPI()

app.include_router(streams.router)
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

load_dotenv(find_dotenv(find_dotenv(os.path.join(BASE_PATH, '.env'))))
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

@app.get("/", response_class=RedirectResponse)
async def redirect_stream():
    return RedirectResponse("/streams")


@bot.message_handler(commands=["start"])
def greet(message):
    bot.send_message(message.chat.id, "Enter the url and enjoy")


@bot.message_handler(content_types=['text'])
def hello(message):
    if "youtu" in message.text:
        buffer = BytesIO()  # Declaring the buffer
        try:
            url = YouTube(message.text)  # Getting the URL
            audio = url.streams.filter(
                mime_type="audio/mp4", abr="48kbps", only_audio=True
            ).first()  # Store the video into a variable
            file_path = audio.download()
            buffer.seek(0)
            bot.send_audio(message.chat.id, audio=open(file_path, 'rb'))
            os.remove(file_path)
            
        except RegexMatchError:
            bot.send_message(message.chat.id, "Wrong url")
    else:
        bot.send_message(message.chat.id, "Wrong url")
        


bot.polling()
