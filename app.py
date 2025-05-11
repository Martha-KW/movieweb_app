"""
This is the Flask Backend  of my MovieWeb Application. A web based movie database with
OMDB API and the integration of a deepseek AI movie funfact generator
"""


from flask import abort, flash, Flask, render_template, redirect, url_for, request
from data_manager.sqlite_data_manager import SQLiteDataManager
from dotenv import load_dotenv
import os
import random
import requests

# load the environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-key-für-development')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Initialize the Database
data_manager = SQLiteDataManager('sqlite:///data/movies.db')


def fetch_omdb_data(title):
    """ Fetch movie data from OMDb API.
        Args: title (str): Movie title you can search for
        Returns: a sanitized dict with movie data or None if error occurs.
    """
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}&plot=full"
        response = requests.get(url, timeout=5)
        data = response.json()
        print("OMDB RAW RESPONSE:", data)

        if data.get('Response') == 'False':
            error_msg = data.get('Error', 'API error')
            flash(f"OMDb API: {error_msg}", "warning")
            return None

        raw_data = {
            'title': data.get('Title'),
            'director': data.get('Director'),
            'writer': data.get('Writer'),
            'actors': data.get('Actors'),
            'year': data.get('Year'),
            'rating': data.get('imdbRating'),
            'runtime': data.get('Runtime'),
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
    """Clean and validate data from OMDb API response.
        Args: omdb_data (dict): Raw API response data
        Returns: dict: Sanitized and type-converted movie data
    """
    if not omdb_data:
        return {}

    allowed_fields = {'title', 'director', 'year', 'rating', 'genre', 'plot', 'writer',
                      'actors', 'runtime'}
    sanitized = {k: v for k, v in omdb_data.items() if k in allowed_fields and v is not None}

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
    """Generates the homepage with links to user and database management and a fun fact"""
    random_theme = random.choice(list(themes.keys()))

    # Generate a fun fact
    prompt = f"""Tell ONE surprising fact about movies. Focus on: {themes[random_theme]}.
       - Be specific (mention movie titles/years)
       - Maximum 1 sentence
       - Make it unexpected"""

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
    )

    fact = response.json()["choices"][0]["message"]["content"]

    return render_template('home.html',
                           funfact=fact,
                           current_theme=random_theme)


@app.route("/users")
def list_users():
    """Displays a list of the users in the Database"""
    users = data_manager.get_all_users()
    return render_template("user_select.html", users=users)


@app.route("/user/<int:user_id>")
def user_movies(user_id):
    """Displays the movies a specific user has safed."""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('list_users'))

    movies = data_manager.get_user_movies(user_id)
    return render_template("movie_list.html",
                           user=user,
                           movies=movies,
                           user_id=user_id)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Creates a new user in the database"""
    if request.method == "POST":
        username = request.form["username"].strip()
        # Checks if user already exists, before writing a duplicate
        existing_user = data_manager.get_user_by_username(username)
        if existing_user:
            flash(f"Username '{username}' is already taken!", "error")
            return redirect(url_for('add_user'))

        data_manager.add_user(username)
        return redirect("/")
    return render_template("user_form.html")


@app.route('/add_movie/<int:user_id>', methods=['GET', 'POST'])
def add_movie(user_id):
    """Ads a new movie to the collection of a certain user."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()

        if not title:
            flash("Title cannot be empty!", "error")
            return redirect(url_for('add_movie', user_id=user_id))

        # Check for existing movie before writing a duplicate
        if data_manager.movie_exists(user_id, title):
            flash(f"You already have '{title}' in your collection!", "error")
            return redirect(url_for('add_movie', user_id=user_id))

        omdb_data = fetch_omdb_data(title) or {}
        movie_data = {
            'title': title,
            'director': request.form.get('director') or omdb_data.get('director'),
            'writer': request.form.get('writer') or omdb_data.get('writer'),
            'actors': request.form.get('actors') or omdb_data.get('actors'),
            'runtime': request.form.get('runtime') or omdb_data.get('runtime'),
            'year': request.form.get('year', type=int) or omdb_data.get('year'),
            'rating': request.form.get('rating', type=float) or omdb_data.get('rating'),
            'genre': request.form.get('genre') or omdb_data.get('genre'),
            'plot': request.form.get('plot') or omdb_data.get('plot'),
            'comment': request.form.get('comment', ''),
            'user_id': user_id,
        }

        movie_data = {k: v for k, v in movie_data.items() if v is not None}
        data_manager.add_movie(**movie_data)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/user/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Enables user to update movie details manually. For example adding a comment, change
    the rating or remove typos.
    """
    if request.method == 'POST':
        updated_data = {
            "title": request.form.get("title"),
            "director": request.form.get("director"),
            "year": request.form.get("year", type=int),
            "rating": request.form.get("rating", type=float),
            "genre": request.form.get("genre"),
            "plot": request.form.get("plot"),
            "comment": request.form.get("comment")
        }
        updated_data = {k: v for k, v in updated_data.items() if v is not None}

        success = data_manager.update_user_movie(movie_id, updated_data)
        if not success:
            flash("Movie not found!", "error")
        else:
            flash("Movie updated successfully!", "success")

        return redirect(url_for('user_movies', user_id=user_id))

    movie = data_manager.get_movie_by_id(movie_id)
    if not movie:
        flash("Movie not found!", "error")
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('edit_movie.html', user_id=user_id, movie=movie)


@app.route('/user/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """deletes a movie from the collection of a certain user only."""
    success = data_manager.delete_movie(movie_id)
    if success:
        flash("Movie deleted successfully!", "success")
    else:
        flash("Movie not found!", "error")
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    """shows more details for the movie you clicked on."""
    movie = data_manager.get_movie_with_user(movie_id)  # Nutze die neue Methode
    if not movie:
        flash("Movie not found!", "error")
        return redirect(url_for('home'))

    return render_template('movie_details.html',
                           movie=movie,
                           user=movie.user)  # Jetzt sollte user verfügbar sein

#  Definition for the themes the AI uses for funfact generation
themes = {
    'technology': "Groundbreaking film technologies and their first uses",
    'controversies': "Movie controversies, scandals and censorship battles",
    'bloopers': "Funny on-set accidents and unscripted moments",
    'paranormal': "Unexplained deaths and supernatural occurrences during productions",
    'actor_facts': "Extreme actor transformations for roles",
    'props': "Craziest movie props ever used",
    'mistakes': "Famous continuity errors and movie mistakes",
    'oscars': "Shocking Oscar wins and snubs",
    'budgets': "Insane movie budget facts",
    'locations': "Fascinating filming location stories"
}


@app.route('/funfact/<theme>')
def themed_funfact(theme):
    """Generates themed movie related fun facts using deepseek AI"""
    if theme not in themes:
        abort(404)

    prompt = f"""Tell ONE surprising fact about: {themes[theme]}.
    -Focus on a single specific example 
    -Be specific (mention movie titles/years)
    - Maximum 1 sentences
    -No lists or multiple examples
    - Make it unexpected
    Example: "In 'The Wizard of Oz' (1939), asbestos was used as fake snow"
    """

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8  # More creative facts
        }
    )

    fact = response.json()["choices"][0]["message"]["content"]
    return render_template('funfact.html',
                           funfact=fact,
                           current_theme=theme)


@app.errorhandler(404)
def page_not_found(e):
    """handles 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """handles server errors"""
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True, port=5002)
