from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from tortoise.contrib.fastapi import tortoise_exception_handlers

from . import settings, views  # noqa
from .settings import app


@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncGenerator[None]:
    async with settings.register_orm(api):
        # db connected
        yield
        # app teardown
    # db connections closed

# Initialize Slack app and request handler

handler = AsyncSlackRequestHandler(app)

api = FastAPI(
    lifespan=lifespan,
    exception_handlers=tortoise_exception_handlers(),
)

@api.post("/slack/events")
async def endpoint(req: Request):
    return await handler.handle(req)
