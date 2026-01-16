from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import streams

app = FastAPI()

app.include_router(streams.router)

@app.get("/", response_class=RedirectResponse)
async def redirect_stream() -> RedirectResponse:
    return RedirectResponse("/streams")
