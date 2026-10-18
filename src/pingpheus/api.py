from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from tortoise.contrib.fastapi import tortoise_exception_handlers

from . import models, settings


@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncGenerator[None]:
    async with settings.register_orm(api):
        # db connected
        yield
        # app teardown
    # db connections closed

# Initialize Slack app and request handler
app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)
handler = SlackRequestHandler(app)

api = FastAPI(
    lifespan=lifespan,
    exception_handlers=tortoise_exception_handlers(),
)
# api.include_router(users_router, prefix="")

@api.post("/slack/events")
async def endpoint(req: Request):
    return await handler.handle(req)

@app.message("hello")
def handle_message(message, say):
    say(f"Hi <@{message['user']}>!")
