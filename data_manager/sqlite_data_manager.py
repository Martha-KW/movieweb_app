from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_manager.data_manager_interface import DataManagerInterface
from models import Base, User, Movie  # falls nicht im Root, Pfad anpassen

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_url="sqlite:///data/movies.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # stellt sicher, dass Tabellen da sind
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_movies(self, user_id):
        session = self.Session()
        movies = session.query(Movie).filter_by(user_id=user_id).all()
        session.close()
        return movies

    def update_user_movie(self, movie_id, updated_data):
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            for key, value in updated_data.items():
                setattr(movie, key, value)
            session.commit()
        session.close()

if __name__ == "__main__":
    manager = SQLiteDataManager()
    for user in manager.get_all_users():
        print(user.username)
