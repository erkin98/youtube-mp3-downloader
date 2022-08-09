from fastapi import Request, FastAPI
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse

from .routers import streams

app = FastAPI()


app.include_router(streams.router)
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))



@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

