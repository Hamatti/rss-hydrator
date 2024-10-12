import sqlite3


class Database:
    def connect(self):
        self.connection = sqlite3.connect("cache.db")
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    def query_url(self, url):
        self.connect()
        prepared_sql = "SELECT url, content FROM entries WHERE url = :url"

        result = self.cursor.execute(prepared_sql, {"url": url}).fetchall()
        self.disconnect()

        return result

    def add_url(self, url, content):
        self.connect()
        prepared_sql = "INSERT INTO entries VALUES (:url, :content)"

        self.cursor.execute(prepared_sql, {"url": url, "content": content})
        self.connection.commit()

        print("db::added url to db")
        self.disconnect()

        return True
