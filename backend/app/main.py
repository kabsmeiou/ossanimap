import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from contextlib import asynccontextmanager

from app.services.pack_generator import PackGenerationError
from app.api.routes import packs, anime, stats, health, job
from app.redis.jobs import stats_updater

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start the bg task on loop
    task = asyncio.create_task(stats_updater())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
# TODO. fix logs
# TODO. caching for external api calls
# TODO. a single create_pack queue to avoid multiple requests of the same anime at the same time
app = FastAPI(
    title="ossanimap",
    description="osu! beatmapset packager that aggregates ranked/loved osu! beatmaps into downloadable packages grouped by anime name",
    version="0.1.0",
    lifespan=lifespan
)

origins = [
    "https://ossanimap.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(packs.router)
app.include_router(anime.router)
app.include_router(stats.router)
app.include_router(health.router)
app.include_router(job.router)

@app.exception_handler(PackGenerationError)
async def pack_generation_error_handler(request, exc: PackGenerationError):
    logger.error(f"Pack generation error: {exc}")
    return JSONResponse(
        status_code=400,  # or map based on exc.code
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code,
            "anime": exc.anime_name,
        },
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
