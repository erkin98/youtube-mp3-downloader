from fastapi import APIRouter, Request, BackgroundTasks, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import os
import tempfile
from app.config import settings
from app.services.youtube import YouTubeService

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.BASE_PATH / "templates"))

def cleanup(path: str):
    """Deletes the temporary file."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass

@router.get("/streams")
async def get_streams_page(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "url": "Enter a url"}
    )

@router.post("/streams")
async def download_stream(request: Request, background_tasks: BackgroundTasks, url: str = Form(...)):
    if not url or "youtu" not in url:
         return templates.TemplateResponse(
            "index.html", {"request": request, "error": "Check the url"}
        )
    
    try:
        # Use a temporary directory for the download
        temp_dir = tempfile.gettempdir()
        file_path = YouTubeService.download_audio(url, output_path=temp_dir)
        filename = os.path.basename(file_path)
        
        # Schedule cleanup after response is sent
        background_tasks.add_task(cleanup, file_path)
        
        return FileResponse(file_path, filename=filename, media_type="audio/mpeg")
        
    except ValueError:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": "Invalid URL"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": f"Error: {str(e)}"}
        )
