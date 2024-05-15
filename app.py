from flask import Flask, render_template, request
from database import load_movie_from_db, load_seances_for_movie_from_db, engine, load_movies_from_db, load_seances_from_db, get_unique_dates_from_db
import os
# , jsonify, request
# from database import engine, load_jobs_from_db, add_application_to_db, load_job_from_db
# from sqlalchemy import text

app = Flask(__name__)

# stworzyc slownik z kluczem jako nazwa filmu oryginalna a wartosci to lista przechowujaca zdjecia


@app.route("/")
def hello_world():
  selected_date = request.args.get('date')

  movie_dates = get_unique_dates_from_db()
  if not selected_date:
    selected_date = "2024-06-22"

  seances = load_seances_from_db(date=selected_date)
  movies = load_movies_from_db(seances.movie_id.unique())
  movie_genres = get_movie_genres(movies, seances)

  print(selected_date)
  return render_template("home.html",
                         movies=movies,
                         seances=seances,
                         movie_dates=movie_dates,
                         selected_date=selected_date,
                         movie_genres=movie_genres)


def get_movie_genres(movies, seances):
  genre_lists = [
      movie_genre.split(' / ') for movie_genre in movies['movie_genre'].values
  ]
  combined_list = []
  for sublist in genre_lists:
    combined_list.extend(sublist)
  return list(set(combined_list))


@app.route("/movie/<title>")
def show_job(title):
  movie = load_movie_from_db(title)
  id = movie.movie_id.values[0]
  seances = load_seances_for_movie_from_db(id)
  if not title:
    return "Not Found", 404
  return render_template('movie_info.html', movie=movie, seances=seances)


if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
