from flask import Flask
from flask_cors import CORS
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy import event

from typing import AsyncGenerator

read_engine = create_async_engine(
    "sqlite+aiosqlite:///yoji.db", pool_pre_ping=True, echo=True
)
write_engine = create_async_engine(
    "sqlite+aiosqlite:///primary_write.db", echo=True, connect_args={"timeout": 30}
)


# Ensure Write Ahead Logging is enabled. This allows multiple reads to happen during a write.
@event.listens_for(read_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


async def get_read_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with read_engine.connect() as conn:
        yield conn


async def get_write_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with write_engine.connect() as conn:
        yield conn


def create_flask_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    # TODO: Check whether Flask actually needs CORS if FastAPI handles API requests
    # CORS(app)

    from app.web import bp as web_bp

    app.register_blueprint(web_bp, url_prefix="/")

    # from app.api import bp as api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    return app
