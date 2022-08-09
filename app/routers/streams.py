from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse,FileResponse,StreamingResponse
from pytube import YouTube
from io import BytesIO



BASE_PATH = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))
router = APIRouter()

@router.get("/streams", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "url": "Enter a url"})


@router.post("/streams/{url}")
async def read_users(request: Request):
    if request.method == "POST": 
        form = await request.form()
        if form["url"]: 
            buffer = BytesIO() # Declaring the buffer
            url = YouTube(form["url"]) # Getting the URL
            audio = url.streams.filter(mime_type="audio/mp4", abr = '48kbps', only_audio = True).first() # Store the video into a variable
            file_path = audio.download(filename=f'{audio.title}.mp3')
            buffer.seek(0)
    return FileResponse(file_path, filename=file_path)

