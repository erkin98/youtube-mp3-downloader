from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import FileResponse
from ..utils.youtube_helpers import donwload_by_url
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
        if form["url"] :
            try:
                file_path = donwload_by_url(form["url"])
                background_tasks.add_task(cleanup, file_path)
            except:
                return templates.TemplateResponse(
                    "index.html", {"request": request, "error": "Check the url"}
                )
        else:
            return templates.TemplateResponse(
                "index.html", {"request": request, "error": "Check the url"}
            )

    return FileResponse(file_path, filename=file_path)
