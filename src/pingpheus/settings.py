import os
from functools import partial

from dotenv import load_dotenv
from tortoise.config import AppConfig, DBUrlConfig, TortoiseConfig
from tortoise.contrib.fastapi import RegisterTortoise

load_dotenv()

# SLACK

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]


# DATABASE

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("WARNING: No database URL found! Defaulting to a local SQLite DB")
    DATABASE_URL = "sqlite://db.sqlite3"

TORTOISE_ORM = TortoiseConfig(
    connections={"default": DBUrlConfig(url=os.getenv("DB_URL", DATABASE_URL))},
    apps={
        "models": AppConfig(
            models=["pingpheus.models"],
            default_connection="default",
            migrations="migrations",
        )
    },
)

register_orm = partial(
    RegisterTortoise,
    config=TORTOISE_ORM,
)