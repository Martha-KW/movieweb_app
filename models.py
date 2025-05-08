
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    movies = relationship("Movie", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
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
