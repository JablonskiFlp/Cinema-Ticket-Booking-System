from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from database import load_movie_from_db, load_seances_for_movie_from_db, engine, load_movies_from_db, load_seances_from_db, get_unique_dates_from_db, load_seance_from_db, load_room_from_db, load_reservations_for_movie_from_db
import os
# , jsonify, request
# from database import engine, load_jobs_from_db, add_application_to_db, load_job_from_db
# from sqlalchemy import text

app = Flask(__name__)


# seances = load_seances_from_db(date="2024-06-22")
# movies = load_movies_from_db(seances.movie_id.unique())
# genre = "akcja"
# print([ genre in g for g in movies.movie_genre.values ])
@app.route("/")
def hello_world():
  selected_date = request.args.get('date')
  genre = request.args.get('genre')

  movie_dates = get_unique_dates_from_db()
  if not selected_date:
    selected_date = "2024-06-22"

  seances = load_seances_from_db(date=selected_date)
  movies = load_movies_from_db(seances.movie_id.unique())
  movie_genres = get_movie_genres(movies, seances)

  if genre:
    movies = movies[[genre in g for g in movies.movie_genre.values]]
  return render_template("home.html",
                         movies=movies,
                         seances=seances,
                         movie_dates=movie_dates,
                         selected_date=selected_date,
                         movie_genres=movie_genres,
                         genre=genre)


def get_movie_genres(movies, seances):
  combined_list = []
  for sublist in movies.movie_genre:
    combined_list.extend(sublist)
  return list(set(combined_list))


def generate_seat_map(room_map):
  rows, seats = room_map.split(':')
  start_row, end_row = rows.split('-')
  start_seat, end_seat = seats.split('-')

  seat_map = []
  for row in range(ord(start_row), ord(end_row) + 1):
    for seat in range(int(start_seat), int(end_seat) + 1):
      seat_map.append(f"{chr(row)}{seat}")

  return seat_map


@app.route("/movie/<movie_id>")
def show_info(movie_id):
  movie = load_movie_from_db(movie_id)
  if not movie_id:
    return "Not Found", 404
  return render_template('movie_info.html', movie=movie)


@app.route("/booking/<seance_id>")
def booking(seance_id):
  seance = load_seance_from_db(seance_id)
  movie = load_movie_from_db(seance.movie_id)
  room = load_room_from_db(seance.room_number.values[0])
  seat_map = generate_seat_map(room.room_map.values[0])
  rezerwacje = load_reservations_for_movie_from_db(seance_id)
  reserved_seats = []
  for rezerwacja in rezerwacje.seats.values:
    rs = rezerwacja.split(',')
    reserved_seats.extend(rs)
  if not seance_id:
    return "Not Found", 404
  return render_template('booking.html',
                         seance=seance,
                         movie=movie,
                         room=room,
                         seat_map=seat_map,
                         reserved_seats=reserved_seats)

@app.route('/reserve_tickets', methods=['POST'])
def reserve_tickets():
  seance_id = request.form.get('seance_id')
  email = request.form.get('email')
  selected_seats = request.form.get('selected_seats')
  ticket_count = request.form.get('ticket_count')
  total_price = request.form.get('total_price')
  with engine.connect() as conn:
    query = text(
        f"INSERT INTO rezerwacje (seance_id, ticket_amount, full_prize, seats, email) VALUES ( {seance_id}, {ticket_count}, {total_price}, '{selected_seats}', '{email}')"
    )
    conn.execute(query)
    conn.commit()
  print(seance_id, email, selected_seats, ticket_count, total_price)

  return render_template('confirmation.html',
                         seance_id=seance_id,
                         email=email,
                         selected_seats=selected_seats,
                         ticket_count=ticket_count,
                         total_price=total_price)


if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
