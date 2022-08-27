import os
from pathlib import Path
from pytube import YouTube, Search
from pytube.exceptions import RegexMatchError
import telebot
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .routers import streams
from dotenv import load_dotenv, find_dotenv
from .utils.youtube_helpers import donwload_by_url, download_mp4 

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

@bot.message_handler(commands=["search"])
def donwload_by_url(message):
    file_path = download_mp4(message)
    bot.send_audio(message.chat.id, audio=open(file_path, 'rb'))
    os.remove(file_path)

@bot.message_handler(content_types=['text'])
def search_by_text(message):
    try:
        file_path = donwload_by_url(message.text)
        bot.send_audio(message.chat.id, audio=open(file_path, 'rb'))
        os.remove(file_path)
    except:
        bot.send_message(message.chat.id, "Wrong url")


bot.polling()
