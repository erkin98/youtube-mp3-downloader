from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import FileResponse
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from io import BytesIO
import os


BASE_PATH = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))
router = APIRouter()


def cleanup(temp_file):
    os.remove(temp_file)


@router.get("/streams")
async def read_item(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "url": "Enter a url"}
    )


@router.post("/streams/{url}")
async def read_users(request: Request, background_tasks: BackgroundTasks):
    if request.method == "POST":
        form = await request.form()
        if form["url"] and "youtu" in form["url"]:
            buffer = BytesIO()  # Declaring the buffer
            try:
                url = YouTube(form["url"])  # Getting the URL
                audio = url.streams.filter(
                    mime_type="audio/mp4", abr="48kbps", only_audio=True
                ).first()  # Store the video into a variable
                file_path = audio.download(filename=f"{audio.title}.mp3")
                buffer.seek(0)
                background_tasks.add_task(cleanup, file_path)
            except RegexMatchError:
                return templates.TemplateResponse(
                    "index.html", {"request": request, "error": "Check the url"}
                )
        else:
            return templates.TemplateResponse(
                "index.html", {"request": request, "error": "Check the url"}
            )

    return FileResponse(file_path, filename=file_path)
