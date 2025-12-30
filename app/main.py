from typing import Union

from fastapi import FastAPI

from app.api.routes import beatmaps

app = FastAPI()

app.include_router(beatmaps.router)

@app.get("/")
def read_root() -> Union[dict, str]:
    return {"Hello": "World"}