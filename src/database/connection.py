import sqlite3


class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "connection"):
            self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("tiktok.db")
        return self.connection


db_connection = DatabaseConnection().get_connection()
