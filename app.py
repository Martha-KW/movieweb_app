from flask import Flask, flash, render_template, redirect, url_for, request
from data_manager.sqlite_data_manager import SQLiteDataManager
from dotenv import load_dotenv
import os



app = Flask(__name__)

data_manager = SQLiteDataManager()

load_dotenv()  # Lädt die .env-Datei
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    app.secret_key = 'fallback-key-für-development'

@app.route("/")
def index():
    users = data_manager.get_all_users()
    return render_template("user_select.html", users=users)

@app.route("/user/<int:user_id>")
def user_movies(user_id):
    user = data_manager.get_user_by_id(user_id)
    movies = data_manager.get_user_movies(user_id)
    return render_template("movie_list.html", user_id=user_id, movies=movies)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        data_manager.add_user(username)
        return redirect("/")  # Zurück zur User-Auswahl
    return render_template("user_form.html")


@app.route('/add_movie/<int:user_id>', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = int(request.form['year'])
        rating = float(request.form['rating'])
        genre = request.form['genre']
        plot = request.form['plot']
        comment = request.form['comment']

        data_manager.add_movie(title, director, year, rating, user_id,
                               genre=genre, plot=plot, comment=comment)

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/user/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'POST':
        # Nur Felder aktualisieren, die im Formular übergeben wurden
        updated_data = {
            "title": request.form.get("title"),
            "director": request.form.get("director"),
            "year": request.form.get("year", type=int),
            "rating": request.form.get("rating", type=float),
            "genre": request.form.get("genre"),
            "plot": request.form.get("plot"),
            "comment": request.form.get("comment")
        }
        # None-Werte entfernen (Felder, die nicht aktualisiert werden sollen)
        updated_data = {k: v for k, v in updated_data.items() if v is not None}

        success = data_manager.update_user_movie(movie_id, updated_data)
        if not success:
            flash("Movie not found!", "error")  # Roter Alert
        else:
            flash("Movie updated successfully!", "success")  # Grüner Alert

        return redirect(url_for('user_movies', user_id=user_id))

    # GET-Request: Formular mit aktuellen Daten anzeigen
    movie = data_manager.get_movie_by_id(movie_id)
    if not movie:
        flash("Movie not found!", "error")  # Roter Alert
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('edit_movie.html', user_id=user_id, movie=movie)

if __name__ == "__main__":
    app.run(debug=True)
