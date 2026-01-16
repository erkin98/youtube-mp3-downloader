import telebot
import os
import tempfile
import logging
from app.config import settings
from app.services.youtube import YouTubeService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not settings.API_KEY:
    logger.warning("API_KEY not set. Bot will not function correctly.")
    # For refactoring purposes, we allow import, but execution will fail if key missing.
    bot = None
else:
    bot = telebot.TeleBot(settings.API_KEY)

    @bot.message_handler(commands=["start"])
    def greet(message) -> None:
        bot.send_message(message.chat.id, "Enter the url and enjoy")

    @bot.message_handler(commands=["search"])
    def search(message) -> None:
        try:
            query = message.text.split('search')[-1].strip()
        except IndexError:
             bot.send_message(message.chat.id, "Please provide a search query")
             return

        if not query:
            bot.send_message(message.chat.id, "Please provide a search query")
            return
            
        bot.send_message(message.chat.id, f"Searching for: {query}...")

        try:
            temp_dir = tempfile.gettempdir()
            file_path = YouTubeService.search_and_download_audio(query, output_path=temp_dir)
            
            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio=audio)
                
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Search error: {e}")
            bot.send_message(message.chat.id, "Could not find or download video.")

    @bot.message_handler(content_types=['text'])
    def handle_text(message) -> None:
        if "youtu" in message.text:
            bot.send_message(message.chat.id, "Downloading...")
            try:
                temp_dir = tempfile.gettempdir()
                file_path = YouTubeService.download_audio(message.text, output_path=temp_dir)
                
                with open(file_path, 'rb') as audio:
                    bot.send_audio(message.chat.id, audio=audio)
                
                os.remove(file_path)
            except Exception as e:
                 logger.error(f"Download error: {e}")
                 bot.send_message(message.chat.id, "Error processing URL.")
        else:
            bot.send_message(message.chat.id, "Please send a valid YouTube URL.")

if __name__ == "__main__":
    if bot:
        logger.info("Starting bot polling...")
        bot.polling()
    else:
        logger.error("Bot not initialized. Check API_KEY.")
