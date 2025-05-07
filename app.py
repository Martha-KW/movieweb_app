from flask import Flask, render_template
from data_manager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
data_manager = SQLiteDataManager()

@app.route('/')
def index():
    users = data_manager.get_all_users()
    return render_template('index.html', users=users)

@app.route('/user/<int:user_id>')
def user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user_id=user_id, movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
