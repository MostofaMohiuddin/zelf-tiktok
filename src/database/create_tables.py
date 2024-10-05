from src.database.connection import db_connection


class SqlTables:
    def __init__(self, conn):
        self.conn = conn

    def create_tables(self):
        print("Creating tables")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hashtag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                challenge_id INTEGER,
                video_count INTEGER,
                view_count INTEGER,
                last_fetched_cursor TEXT,
                has_more BOOLEAN
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tiktok_unique_id TEXT NOT NULL,
                sec_uid TEXT NOT NULL,
                follower_count INTEGER,
                following_count INTEGER,
                video_count INTEGER,
                like_count INTEGER
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS video (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tiktok_video_id TEXT NOT NULL,
                hashtag_id INTEGER,
                keyword_id INTEGER,
                author_username TEXT,
                author_id INTEGER,
                comment_count INTEGER,
                like_count INTEGER,
                view_count INTEGER,
                video_url TEXT,
                description TEXT,
                FOREIGN KEY (hashtag_id) REFERENCES hashtag(id),
                FOREIGN KEY (author_id) REFERENCES user(id)
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keyword (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                search_id TEXT,
                last_fetched_cursor TEXT,
                has_more BOOLEAN
            );
            """
        )
        self.conn.commit()
        cursor.close()
        print("Tables created")


def run():
    SqlTables(db_connection).create_tables()


if __name__ == "__main__":
    run()
