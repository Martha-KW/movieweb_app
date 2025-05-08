from flask import Flask, flash, render_template, redirect, url_for, request
from data_manager.sqlite_data_manager import SQLiteDataManager
from dotenv import load_dotenv
import requests
import os

load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

app = Flask(__name__)

data_manager = SQLiteDataManager()

load_dotenv()  # Lädt die .env-Datei
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    app.secret_key = 'fallback-key-für-development'

# app.py
import requests
from flask import flash


def fetch_omdb_data(title):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        response = requests.get(url, timeout=5)  # Timeout nach 5 Sekunden
        data = response.json()

        # API-Fehler abfangen (z.B. zu viele Requests)
        if data.get('Response') == 'False':
            error_msg = data.get('Error', 'API error')
            flash(f"OMDb API: {error_msg}", "warning")
            return None

        return {
            'title': data.get('Title'),
            'director': data.get('Director'),
            'year': int(data.get('Year')) if data.get('Year') else None,
            'rating': float(data.get('imdbRating')) if data.get('imdbRating') else None
        }

    except requests.exceptions.RequestException as e:
        flash("Could not connect to OMDb API. Using manual input only.", "warning")
        return None
    except ValueError as e:
        flash("Invalid API response format.", "error")
        return None


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/users")
def list_users():
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
        # In deiner add_movie/update_movie Route
        title = request.form.get('title', '').strip()

        # Validierung
        if not title:
            flash("Title cannot be empty!", "error")
            return redirect(url_for('add_movie_form'))
        if len(title) > 100:
            flash("Title too long (max 100 characters)", "error")
            return redirect(...)
        if not all(c.isalnum() or c.isspace() for c in title):
            flash("Only letters, numbers and spaces allowed", "error")
            return redirect(...)

        omdb_data = fetch_omdb_data(title) or {}

        # Rating sicher parsen
        rating_input = request.form.get('rating', '')
        try:
            rating = float(rating_input) if rating_input else omdb_data.get('rating')
        except ValueError:
            flash("Invalid rating format! Use numbers like 7.5", "error")
            return redirect(url_for('add_movie', user_id=user_id))

        movie_data = {
            'title': title,
            'director': request.form.get('director') or omdb_data.get('director'),
            'year': int(request.form['year']) if request.form.get('year') else omdb_data.get('year'),
            'rating': rating,  # Verwende den geparsten Wert
            'genre': request.form.get('genre') or omdb_data.get('genre'),
            'plot': request.form.get('plot') or omdb_data.get('plot'),
            'comment': request.form.get('comment', ''),
            'user_id': user_id
        }

        data_manager.add_movie(**movie_data)
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


@app.route('/user/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    success = data_manager.delete_movie(movie_id)  # Methode wird im nächsten Schritt erstellt
    if success:
        flash("Movie deleted successfully!", "success")
    else:
        flash("Movie not found!", "error")
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)
