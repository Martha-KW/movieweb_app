from flask import Flask, render_template, redirect, url_for, request

from data_manager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
data_manager = SQLiteDataManager()

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



if __name__ == "__main__":
    app.run(debug=True)
