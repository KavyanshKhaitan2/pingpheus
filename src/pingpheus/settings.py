import logging
import os
from functools import partial

from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from tortoise.config import AppConfig, DBUrlConfig, TortoiseConfig
from tortoise.contrib.fastapi import RegisterTortoise

load_dotenv()

logger = logging.getLogger("app")


DEBUG = os.environ["DEBUG"].lower().strip() in ['true', 'on', 'yes', '1', 'enabled']

# SLACK

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

XOXC_USER_TOKEN = os.environ["XOXC_USER_TOKEN"]
XOXD_USER_TOKEN = os.environ["XOXD_USER_TOKEN"]

app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

# DATABASE

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("WARNING: No database URL found! Defaulting to a local SQLite DB")
    DATABASE_URL = "sqlite://db.sqlite3"

TORTOISE_ORM = TortoiseConfig(
    connections={"default": DBUrlConfig(url=os.getenv("DB_URL", DATABASE_URL))},
    apps={
        "models": AppConfig(
            models=["pingpheus.models"],
            default_connection="default",
            migrations="pingpheus.migrations",
        )
    },
)

register_orm = partial(
    RegisterTortoise,
    config=TORTOISE_ORM,
)

# Logging
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)