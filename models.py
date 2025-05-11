"""
Database Models for Movie Web Application
Defines SQLAlchemy ORM models for users and movies with their relationships.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """The user model represents registrated application users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    movies = relationship("Movie", back_populates="user")


class Movie(Base):
    """Movie model that represenst movies and coordinated data in the users collection."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    director = Column(String)
    writer = Column(String)
    actors = Column(String)
    year = Column(Integer)
    rating = Column(Float, CheckConstraint('rating >= 0 AND rating <= 10'))
    genre = Column(String)
    runtime = Column(String)
    plot = Column(Text)
    comment = Column(Text)

    user = relationship("User", back_populates="movies")
