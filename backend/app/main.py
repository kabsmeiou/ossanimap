from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import packs, anime, stats

app = FastAPI(
    title="ossanimap",
    description="osu! beatmapset packager that aggregates ranked/loved osu! beatmaps into downloadable packages grouped by anime name",
    version="0.1.0"
)

origins = [
    "http://localhost",
    "http://localhost:5173",
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