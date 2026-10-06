from contextlib import contextmanager
from sqlalchemy import create_engine

from src.config import get_settings


engine = create_engine(get_settings().database_url, pool_pre_ping=True)


@contextmanager
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise
    finally:
        connection.close()
