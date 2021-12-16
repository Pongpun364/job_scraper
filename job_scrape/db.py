
from sqlalchemy import create_engine
from sqlalchemy import inspect

from  conf import  get_settings

settings = get_settings()

conn = create_engine(settings.db_connection_str)


def verify_table_exists(table_name):
    ins = inspect(conn)
    ret = ins.dialect.has_table(conn.connect(),table_name)
    return ret