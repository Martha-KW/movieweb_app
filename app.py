from flask import flash, Flask, render_template, redirect, url_for, request
from data_manager.sqlite_data_manager import SQLiteDataManager
from dotenv import load_dotenv
import os
import requests


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    app.secret_key = 'fallback-key-für-development'
data_manager = SQLiteDataManager()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')


def fetch_omdb_data(title):
    """Holt und bereinigt Daten von der OMDb API."""
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get('Response') == 'False':
            error_msg = data.get('Error', 'API error')
            flash(f"OMDb API: {error_msg}", "warning")
            return None

        # Rohdaten bereinigen
        raw_data = {
            'title': data.get('Title'),
            'director': data.get('Director'),
            'year': data.get('Year'),
            'rating': data.get('imdbRating'),
            'genre': data.get('Genre'),
            'plot': data.get('Plot')
        }
        return sanitize_omdb_data(raw_data)

    except requests.exceptions.RequestException as e:
        flash("Could not connect to OMDb API. Using manual input only.", "warning")
        return None
    except ValueError as e:
        flash("Invalid API response format.", "error")
        return None

def sanitize_omdb_data(omdb_data):
    """Entfernt nicht-whitelistete Felder und konvertiert Typen."""
    if not omdb_data:
        return {}

    allowed_fields = {'title', 'director', 'year', 'rating', 'genre', 'plot'}
    sanitized = {k: v for k, v in omdb_data.items() if k in allowed_fields and v is not None}

    # Typkonvertierung
    if 'year' in sanitized:
        try:
            sanitized['year'] = int(sanitized['year'])
        except (ValueError, TypeError):
            sanitized['year'] = None

    if 'rating' in sanitized:
        try:
            sanitized['rating'] = float(sanitized['rating'])
        except (ValueError, TypeError):
            sanitized['rating'] = None

    return sanitized

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
        title = request.form.get('title', '').strip()

        # Validierung
        if not title:
            flash("Title cannot be empty!", "error")
            return redirect(url_for('add_movie', user_id=user_id))  # Korrigierter Redirect

        omdb_data = fetch_omdb_data(title) or {}
        movie_data = {
            'title': title,
            'director': request.form.get('director') or omdb_data.get('director'),
            'year': request.form.get('year', type=int) or omdb_data.get('year'),
            'rating': request.form.get('rating', type=float) or omdb_data.get('rating'),
            'genre': request.form.get('genre') or omdb_data.get('genre'),
            'plot': request.form.get('plot') or omdb_data.get('plot'),
            'comment': request.form.get('comment', ''),
            'user_id': user_id
        }

        # None-Werte bereinigen
        movie_data = {k: v for k, v in movie_data.items() if v is not None}
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":

    app.run(debug=True)
