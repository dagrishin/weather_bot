import sqlite3


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS geolocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                UNIQUE(chat_id, name)
            )
        ''')
        self.conn.commit()

    def add_location(self, chat_id, name, latitude, longitude):
        self.cursor.execute('''
            INSERT OR REPLACE INTO geolocations (chat_id, name, latitude, longitude)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, name, latitude, longitude))
        self.conn.commit()

    def get_locations_by_chat_id(self, chat_id):
        self.cursor.execute('''
            SELECT id, name, latitude, longitude FROM geolocations WHERE chat_id = ?
        ''', (chat_id,))
        return self.cursor.fetchall()

    def delete_location(self, location_id):
        self.cursor.execute('''
            DELETE FROM geolocations WHERE id = ?
        ''', (location_id,))
        self.conn.commit()
