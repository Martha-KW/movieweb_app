from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from data_manager.data_manager_interface import DataManagerInterface
from models import Base, User, Movie
import logging
import os

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_url=None):
        if db_url is None:
            if os.environ.get('TESTING') == 'true':
                db_url = "sqlite:///:memory:"  # In-Memory für Tests
            else:
                db_url = "sqlite:///data/movies.db"  # Normale DB
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)  # Session-Instanz

    def get_all_users(self):
        session = self.Session()
        try:
            return session.query(User).all()
        finally:
            session.close()

    def get_user_movies(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.movies
            return []
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = self.Session()
        try:
            return session.query(User).filter_by(id=user_id).first()
        finally:
            session.close()

    def get_user_by_username(self, username):
        session = self.Session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()

    def movie_exists(self, user_id, title):
        session = self.Session()
        try:
            existing_movie = session.query(Movie).filter_by(
                user_id=user_id,
                title=title
            ).first()
            return existing_movie is not None
        finally:
            session.close()


    def get_movie_by_id(self, movie_id):
        session = self.Session()
        try:
            return session.query(Movie).filter_by(id=movie_id).first()
        finally:
            session.close()

    def add_user(self, username):
        session = self.Session()  # Lokale Session erstellen
        try:
            new_user = User(username=username)
            session.add(new_user)
            session.commit()
            return new_user.id
        except Exception as e:
            session.rollback()
            logging.error("Error adding user: %s", e)
            return None
        finally:
            session.close()  # Session immer schließen

    def add_movie(self, title, director=None, year=None, rating=None, user_id=None,
                  genre=None, plot=None, comment=None, writer=None, actors=None,
                  runtime=None):
        session = self.Session()
        try:
            new_movie = Movie(
                title=title,
                director=director,
                writer=writer,  # Neu
                actors=actors,  # Neu
                runtime=runtime,  # Neu
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
            logging.error("Error adding movie: %s", e)
        finally:
            session.close()

    def delete_movie(self, movie_id):
        session = self.Session()
        try:
            movie = session.query(Movie).filter_by(id=movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logging.error("Error deleting movie: %s", e)
            return False
        finally:
            session.close()


    def update_user_movie(self, movie_id, updated_data):
        session = self.Session()
        try:
            movie = session.query(Movie).filter_by(id=movie_id).first()
            if not movie:
                return False  # Film existiert nicht

            # Nur vorhandene Felder aktualisieren
            for key, value in updated_data.items():
                if hasattr(movie, key):
                    setattr(movie, key, value)

            session.commit()
            return True  # Erfolg
        except Exception as e:
            session.rollback()
            logging.error("Error updating movie: %s", e)
            return False
        finally:
            session.close()

    def get_movie_with_user(self, movie_id):
        session = self.Session()
        try:
            return session.query(Movie).options(
                joinedload(Movie.user)  # Jetzt mit direkt importiertem joinedload
            ).filter_by(id=movie_id).first()
        finally:
            session.close()
