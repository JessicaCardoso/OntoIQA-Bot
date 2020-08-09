import psycopg2
import psycopg2.extras
import datetime
from .db_util import DbUtil
from .turn import Turn


class TurnDao:
    def __init__(self, database: DbUtil):
        self._db = database

    def get_turn_by_id(self, turn_id: int) -> Turn:
        turn = Turn()
        statement = f"SELECT * FROM turns WHERE id={turn_id};"
        try:
            self._db.execute(statement)
            self._db.commit()
            result = self._db.fetchone()
            if result:
                turn.id = result[0]
                turn.message_id = result[1]
                # history_id = result[2]
                turn.user_text = result[3]
                turn.bot_text = result[4]
                turn.answer_confidence = result[5]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while fetching data from PostgreSQL", error)
        return turn

    def add_turn(self, history_id: int, turn: Turn) -> int:
        try:
            sql_insert_query = (
                "INSERT INTO turns(message_id, history_id, "
                "user_text, bot_text, bot_answer_score, created_at) "
                "VALUES (%s, %s, %s, %s, %s, TIMESTAMP %s) RETURNING id;"
            )
            self._db.execute(
                sql_insert_query,
                (
                    turn.message_id,
                    history_id,
                    turn.user_text,
                    turn.bot_text,
                    turn.answer_confidence,
                    datetime.datetime.now(),  # data-hora atual
                ),
            )
            self._db.commit()
            count = self._db.cursor.rowcount
            print(count, "Record inserted successfully into Turns table")
            return self._db.cursor.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Failed to insert record into Turns table", error)
            return None

    def update_turn(self, turn: Turn):
        try:
            sql_update_query = (
                "UPDATE turns SET message_id = %s, "
                "user_text = %s, bot_text = %s, bot_answer_score = %s "
                "WHERE id = %s;"
            )

            self._db.execute(
                sql_update_query,
                (
                    turn.message_id,
                    turn.user_text,
                    turn.bot_text,
                    turn.answer_confidence,
                    turn.id,
                ),
            )
            self._db.commit()
            count = self._db.cursor.rowcount
            print(count, "Record Updated successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)

    def add_suggestions(self, turn_id: int, suggestions: list):
        try:
            sql_insert_query = (
                "INSERT INTO suggestions(turn_id, suggestion_text) VALUES %s"
            )
            suggestions_rows = [(turn_id, text) for text in suggestions]
            psycopg2.extras.execute_values(
                self._db.cursor, sql_insert_query, suggestions_rows
            )
            self._db.commit()
            count = self._db.cursor.rowcount
            print(count, "Record inserted successfully into Suggestions table")
        except (Exception, psycopg2.DatabaseError) as error:
            print(
                "Failed to insert multiple records into Suggestions table",
                error,
            )
