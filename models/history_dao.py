import psycopg2

from .db_util import DbUtil

from .history import History


class HistoryDao:
    def __init__(self, database: DbUtil):
        self._db = database

    def add_history(self, user_id: int, history: History):
        try:
            sql_insert_query = (
                "INSERT INTO user_history(user_id, bot_id) "
                "VALUES (%s, %s) RETURNING id;"
            )
            self._db.execute(sql_insert_query, (user_id, history.bot_id))
            self._db.commit()
            count = self._db.cursor.rowcount
            print(
                count, "Record inserted successfully into user_history table"
            )
            return self._db.cursor.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Failed to insert record into History table", error)
            return None

    def get_history_by_id(self, history_id: int) -> History:
        history = History()
        statement = f"SELECT * FROM user_history WHERE id={history_id};"
        try:
            self._db.execute(statement)
            self._db.commit()
            rs = self._db.fetchone()
            if rs:
                history.id = rs[0]
                history.bot_id = rs[1]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while fetching data from PostgreSQL", error)
        return history

    def get_history_by_user_id(self, user_id: int) -> list:
        chat_history = list()
        statement = f"SELECT * FROM user_history WHERE user_id = {user_id};"
        try:
            self._db.execute(statement)
            self._db.commit()
            user_history = self._db.fetchall()
            for row in user_history:
                history = History(id=row[0], bot_id=row[1])
                chat_history.append(history)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while fetching data from PostgreSQL", error)
        return chat_history
