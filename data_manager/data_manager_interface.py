from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        pass


    @abstractmethod
    def get_user_movies(self, user_id):
        pass


    @abstractmethod
    def movie_exists(self, user_id, title):
        """Check if movie exists for user"""
        pass

    @abstractmethod
    def update_user_movie(self, movie_id, updated_data):
        pass


    @abstractmethod
    def get_user_by_username(self, username):
        """Get user by username"""
        pass
