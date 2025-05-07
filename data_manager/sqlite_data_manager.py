import sqlite3
from data_manager.data_manager_interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_path="data/movies.db"):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_users(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        connection.close()
        return users

    def get_user_movies(self, user_id):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row  # defines that the data is a dict -< blueprint

        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM movies WHERE user_id = ?
        """, (user_id,))

        movies = cursor.fetchall()
        connection.close()
        return movies

    def update_user_movie(self, movie_id, updated_data):
        pass  # specify later, too

if __name__ == "__main__":
    manager = SQLiteDataManager()
    users = manager.get_all_users()
    for user in users:
        print(user)
