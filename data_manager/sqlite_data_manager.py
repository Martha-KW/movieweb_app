from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_manager.data_manager_interface import DataManagerInterface
from models import Base, User, Movie

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_url="sqlite:///data/movies.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)  # Session-Instanz

    def get_all_users(self):
        return self.Session.query(User).all()

    def get_user_movies(self, user_id):
        user = self.Session.query(User).filter_by(id=user_id).first()
        if user:
            return user.movies
        return []

    def get_user_by_id(self, user_id):
        return self.Session.query(User).filter_by(id=user_id).first()

    def add_user(self, username):
        try:
            new_user = User(username=username)
            self.Session.add(new_user)
            self.Session.commit()
            return new_user.id
        except Exception as e:
            self.Session.rollback()
            print("Error adding user:", e)
            return None

    def add_movie(self, title, director, year, rating, user_id, genre=None, plot=None,
                  comment=None):
        session = self.Session()
        try:
            new_movie = Movie(
                name=title,  # wichtig: name statt title
                director=director,
                year=year,
                rating=rating,
                user_id=user_id,
                genre=genre,
                plot=plot,
                comment=comment
            )
            session.add(new_movie)
            session.commit()
        except Exception as e:
            session.rollback()
            print("Error adding movie:", e)
        finally:
            session.close()

    def update_user_movie(self, movie_id, updated_data):
        movie = self.Session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            for key, value in updated_data.items():
                setattr(movie, key, value)
            self.Session.commit()
