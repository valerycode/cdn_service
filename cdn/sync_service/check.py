import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config


# Add sqlalchemy url
def get_url():
    env_local_path = Path(__file__).parent.parent / ".env.local"
    print(env_local_path)
    load_dotenv(dotenv_path=env_local_path)
    dsn = os.getenv("PG_SYNC_DSN")
    if not dsn:
        raise ValueError(f"Environment variable PG_SYNC_DSN must be set.")
    return dsn


print(get_url())
