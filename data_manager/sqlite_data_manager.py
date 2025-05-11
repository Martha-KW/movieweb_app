"""
SQLite Data Manager implementation for movie database application.
Handles all database operations using SQLAlchemy ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from data_manager.data_manager_interface import DataManagerInterface
from models import Base, User, Movie
import logging
import os


class SQLiteDataManager(DataManagerInterface):
    """Manages database operations for the movie web application."""
    def __init__(self, db_url=None):
        """
               Initialize the database connection.

               Args:
                   db_url (str): Optional database URL. If None, uses:
                       - ':memory:' for testing (when TESTING=true)
                       - 'sqlite:///data/movies.db' for production
               """
        if db_url is None:
            if os.environ.get('TESTING') == 'true':
                db_url = "sqlite:///:memory:"  # In-Memory for Tests
            else:
                db_url = "sqlite:///data/movies.db"  # real DB
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)  # Session-Instance


    def get_all_users(self):
        """Retrieve all users from the database.
           Returns: List[User]: All user objects in the database
        """
        session = self.Session()
        try:
            return session.query(User).all()
        finally:
            session.close()


    def get_user_movies(self, user_id):
        """Get all movies for a specific user.
           Args: user_id (int): ID of the user
           Returns:
           List[Movie]: Movies associated with the user or empty list if not found
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.movies
            return []
        finally:
            session.close()


    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID.
               Args: user_id (int): User ID to search for
               Returns: User: The user object or None if not found
        """
        session = self.Session()
        try:
            return session.query(User).filter_by(id=user_id).first()
        finally:
            session.close()


    def get_user_by_username(self, username):
        """Find a user by their username.
               Args: username (str): Username to search for
               Returns: User: User object or None if not found
        """
        session = self.Session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()


    def movie_exists(self, user_id, title):
        """Check if a movie already exists for a user
                Args: user_id (int): ID of the user
                      title (str): Movie title to check
                Returns: bool: True if movie exists, False otherwise
        """
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
        """Retrieve a movie by its ID
                Args: movie_id (int): ID of the movie
                Returns: Movie: Movie object or None if not found
        """
        session = self.Session()
        try:
            return session.query(Movie).filter_by(id=movie_id).first()
        finally:
            session.close()


    def add_user(self, username):
        """Add a new user to the database.
                Args: username (str): Name of the user to add
                Returns: int: ID of the newly created user or None on failure
        """
        session = self.Session()  # create a local session
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
            session.close()


    def add_movie(self, title, director=None, year=None, rating=None, user_id=None,
                  genre=None, plot=None, comment=None, writer=None, actors=None,
                  runtime=None):
        """Add a new movie to the database.
               Args:
                   title (str): Title of the movie
                   director (str, optional): Director of the movie
                   year (int, optional): Release year
                   rating (float, optional): Rating (limited to 0.0-10.0)
                   user_id (int, optional): ID of the user who added the movie
                   genre (str, optional): Genre of the movie
                   plot (str, optional): Plot summary
                   comment (str, optional): User written comment
                   writer (str, optional): Screenwriter(s)
                   actors (str, optional): Main actors
                   runtime (str, optional): movie duration
               """
        session = self.Session()
        try:
            new_movie = Movie(
                title=title,
                director=director,
                writer=writer,
                actors=actors,
                runtime=runtime,
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
        """Delete a movie from the database.
               Args: movie_id (int): ID of the movie to delete
               Returns: bool: True if deletion was successful, False otherwise
        """
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
        """Update movie information.
                Args: movie_id (int): ID of the movie to update
                      updated_data (dict): Dictionary of fields to update
                Returns: bool: True if update was successful, False otherwise
        """
        session = self.Session()
        try:
            movie = session.query(Movie).filter_by(id=movie_id).first()
            if not movie:
                return False

            for key, value in updated_data.items():
                if hasattr(movie, key):
                    setattr(movie, key, value)

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error("Error updating movie: %s", e)
            return False
        finally:
            session.close()


    def get_movie_with_user(self, movie_id):
        """Get a movie along with its associated user data.
                Args: movie_id (int): ID of the movie
                Returns: Movie: Movie object with joined user data or None if not found
        """
        session = self.Session()
        try:
            return session.query(Movie).options(
                joinedload(Movie.user)
            ).filter_by(id=movie_id).first()
        finally:
            session.close()
