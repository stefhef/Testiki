import sqlalchemy
import databases
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

DATABASE_URL = "sqlite:///db/test.db"
Base: DeclarativeMeta = declarative_base()
db = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

