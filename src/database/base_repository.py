import sqlite3


class BaseRepository:
    def __init__(self):
        self.db_path = "tiktok.db"

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query, params=()):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                result = [dict(row) for row in result]
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.lastrowid

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def execute_many_query(self, query, params=()):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.executemany(query, params)

            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                result = [dict(row) for row in result]
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.lastrowid

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def execute_query_one(self, query, params=()):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if query.strip().lower().startswith("select"):
                result = cursor.fetchone()
                result = dict(result) if result else None
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.lastrowid

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
