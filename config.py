import os
import contextlib

import sqlalchemy
from ormar import OrmarConfig
from sqlalchemy.engine import Engine
from databases import Database

from cafeto import App
from cafeto.staticfiles import StaticFiles

DATABASE_URL = os.getenv("DATABASE_URL")

engine: Engine = sqlalchemy.create_engine(DATABASE_URL)

database: Database = Database(DATABASE_URL)

base_ormar_config: OrmarConfig = OrmarConfig(
    metadata=sqlalchemy.MetaData(),
    database=database,
    engine=engine
)

@contextlib.asynccontextmanager
async def lifespan(app):  # pragma: no cover
    await database.connect()
    yield
    await database.disconnect()
    

app: App = App(
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
