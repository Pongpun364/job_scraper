
from sqlalchemy import create_engine
from sqlalchemy import inspect

from .conf import DB_CONNECTION_STR

conn = create_engine(DB_CONNECTION_STR)


def verify_table_exists(table_name):
    ins = inspect(conn)
    ret = ins.dialect.has_table(conn.connect(),table_name)
    return ret