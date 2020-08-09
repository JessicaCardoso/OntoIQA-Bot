import psycopg2

from .db_util import DbUtil


from .user import User


class UserDao:
    def __init__(self, database: DbUtil):
        self._db = database

    def add_user(self, user: User):
        try:
            sql_insert_query = (
                "INSERT INTO users (id, first_name) VALUES (%s, %s);"
            )
            self._db.execute(
                sql_insert_query, (user.user_id, user.first_name),
            )
            self._db.commit()
            count = self._db.cursor.rowcount
            print(count, "Record inserted successfully into users table")
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into User table", error)

    def get_user_by_id(self, user_id: int) -> (bool, User):
        user = User()
        user_exists = False
        statement = f"SELECT * FROM users WHERE id={user_id};"
        try:
            self._db.execute(statement)
            self._db.commit()
            result = self._db.fetchone()
            user_exists = result is not None
            if result:
                user.user_id = result[0]
                user.first_name = result[1]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while fetching data from PostgreSQL", error)
        return user_exists, user

    def update_user(self, user: User):
        try:
            sql_update_query = (
                "UPDATE users SET first_name = %s WHERE id = %s;"
            )

            self._db.execute(
                sql_update_query, (user.first_name, user.user_id),
            )
            self._db.commit()
            count = self._db.cursor.rowcount
            print(count, "Record Updated successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)
