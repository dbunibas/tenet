import logging

from fastapi import FastAPI, Request

from src.api.ConfigSingleton import ConfigSingleton
from src.api.routers import Resource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
config = ConfigSingleton()
tenet = FastAPI()


@tenet.middleware("http")
async def logging_middleware(request: Request, call_next):
    log.info(f"--- REQUEST RECEIVED: [{request.method}] {request.url}")
    return await call_next(request)


tenet.include_router(Resource.tenetResource)
