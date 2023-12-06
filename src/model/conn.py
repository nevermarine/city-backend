import psycopg2
from base_models import config


def get_conn():
    conn = psycopg2.connect(
        host=config["PG_HOST"],
        port=config["PG_PORT"],
        database=config["PG_DB"],
        user=config["PG_USER"],
        password=config["PG_PASS"],
    )
    conn.autocommit = True
    return conn
