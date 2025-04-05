from fastapi import FastAPI
from src.models.HTTPResponse import ResponseModel
from src.routes import images, enhancer
from contextlib import asynccontextmanager
from src.models.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(images.router, prefix="/api/v1")
app.include_router(enhancer.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    return ResponseModel(data=None, code=200, message="Hello World!")
