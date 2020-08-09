import psycopg2
from psycopg2 import Error

import pandas as pd
import os
import pathlib

_ROOT = pathlib.Path(__file__).parent.absolute()


class DbUtil:
    def __init__(self):
        # print(os.getenv("PG_PASSWORD"))
        self._connection = psycopg2.connect(
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
            database=os.getenv("PG_DATABASE"),
        )
        self._cursor = self._connection.cursor()

    def __enter__(self):
        with open(os.path.join(_ROOT, "schema.sql"), "r") as f:
            # cria as tabelas no banco de dados
            self.cursor.execute(f.read())
            self.commit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()
        print("PostgreSQL connection is closed")

    @property
    def connection(self):
        return self._connection

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def get_table_as_df(self, tb_name):
        sql = f"select * from {tb_name};"
        return pd.read_sql_query(sql, self._connection)

    def check_tb_exists(self, tb_name, schema_name="public"):
        sql = f"SELECT to_regclass('{schema_name}.{tb_name}');"
        self.cursor.execute(sql)
        return self.fetchone()[0] is not None
