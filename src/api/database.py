from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import get_settings

settings = get_settings()


@contextmanager
def get_db_connection() -> Generator:
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            cursor_factory=RealDictCursor,
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


## @breif Executa query
#  @param query SQL
#  @param params Parâmetros para a query
def execute_query(query: str, params: tuple) -> list:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


## @breif Executa query ONE
#  @param query SQL
#  @param params Parâmetros para a query
def execute_one(query: str, params: tuple) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
