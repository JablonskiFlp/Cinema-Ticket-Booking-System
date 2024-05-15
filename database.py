from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
import os
import datetime

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(db_connection_string,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                       }})


def time_formatting(data):
    reference_date = np.datetime64('1970-01-01')

    def format_time(delta):
        seance_time = delta + reference_date
        return f"{seance_time.hour:02d}:{seance_time.minute:02d}"

    return data['start_time'].apply(format_time)


def load_movies_from_db(movie_ids):
    with engine.connect() as conn:
        movie_ids_str = ','.join(map(str, movie_ids))

        sql_query = f"SELECT * FROM movies WHERE movie_id IN ({movie_ids_str})"
        movies = pd.read_sql_query(sql_query, conn)

    # Ścieżka do folderu images
    folder_path = '../static/images/'

    # Dodanie ścieżki do plakatów do danych o filmach
    movies['poster'] = folder_path + movies['poster']

    return movies


def get_unique_dates_from_db():
    with engine.connect() as conn:
        # Budowanie zapytania SQL
        sql_query = "SELECT DISTINCT movie_date FROM Seances"
        movie_dates = pd.read_sql_query(sql_query, conn)
        return movie_dates


def load_seances_from_db(date=None):
    with engine.connect() as conn:
        # Budowanie zapytania SQL
        sql_query = "SELECT * FROM Seances WHERE 1=1"  # Zawsze prawdziwe warunki, aby łatwo dodawać inne filtry
        if date:
            sql_query += f" AND movie_date = '{date}'"

        # Pobieranie danych z bazy danych na podstawie zbudowanego zapytania
        seances = pd.read_sql_query(sql_query, conn)
        seances['start_time'] = time_formatting(seances)
        return seances


def load_movie_from_db(title):
    movies = load_movies_from_db()
    return movies[movies.title == title]


def load_seances_for_movie_from_db(id):
    with engine.connect() as conn:
        sql_query = pd.read_sql_query(
            f"SELECT * FROM Seances WHERE movie_id = '{id}'", conn)
        seances = pd.DataFrame(sql_query)
        seances['start_time'] = time_formatting(seances)
        return seances
