import sqlmodel

from src.model.base_models import config

engine = sqlmodel.create_engine(config["PG_CONN_STR"], echo=True)
