from typing import Union

from fastapi import FastAPI

from app.api.routes import packs, anime

app = FastAPI(
    title="ossanimap",
    description="osu! beatmapset packager that aggregates ranked/loved osu! beatmaps into downloadable packages grouped by anime name",
    version="0.1.0"
)

app.include_router(packs.router)
app.include_router(anime.router)

@app.get("/")
def read_root() -> Union[dict, str]:
    return {"Hello": "World"}