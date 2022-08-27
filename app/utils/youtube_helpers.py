from fileinput import filename
import os
from pathlib import Path
from pytube import YouTube, Search


def download_mp4(text: str) -> Path:
    search = Search(text.text.split('search')[-1])
    res = search.results[0].streams.filter(
                mime_type="audio/mp4", abr="48kbps", only_audio=True
            ).first()
    file_path = res.download()
    return file_path

def donwload_by_url(text: str) -> Path:
    if "youtu" in text:
        try:
            url = YouTube(text)  # Getting the URL
            audio = url.streams.filter(
                mime_type="audio/mp4", abr="48kbps", only_audio=True
            ).first()  # Store the video into a var
            file_path = audio.download(filename=f"{audio.title}.mp3")
        except:
            return "Wrong url"
        return file_path