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
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.movies  # gibt Liste von Movie-Objekten zurück
            return []
        finally:
            session.close()

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
    movies = manager.get_user_movies(1)
    for movie in movies:
        print(movie.name, movie.director)
