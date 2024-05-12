from flask import Flask, render_template
from database import engine, load_movies_from_db, load_seances_from_db
import pandas as pd
import numpy as np
import os
import datetime
# , jsonify, request
# from database import engine, load_jobs_from_db, add_application_to_db, load_job_from_db
# from sqlalchemy import text

app = Flask(__name__)
seances = load_seances_from_db()
movies = load_movies_from_db()

folder_path = 'static/images'  # Ścieżka do folderu images
image_files = os.listdir(folder_path)  # Pobieranie listy plików z folderu
data = [os.path.join(folder_path, file)
        for file in image_files]  # Tworzenie listy ścieżek do plików
data.sort(key=str.lower)
movies = movies.sort_values(
    by="title"
)  # dopasowanie kolumn odpowiedniego plakatu do odpowiedniego filmu
movies['poster'] = data  # dodanie kolumny z ścieżkami do plakatów
reference_date = np.datetime64('1970-01-01')

# stworzyc slownik z kluczem jako nazwa filmu oryginalna a wartosci to lista przechowujaca zdjecia

def format_time(delta):
  seance_time = delta + reference_date
  return f"{seance_time.hour:02d}:{seance_time.minute:02d}"


# Zastosowanie funkcji na kolumnie 'start_time'
seances['start_time'] = seances['start_time'].apply(format_time)

@app.route("/")
def hello_world():
  return render_template("home.html", movies = movies, seances = seances)

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
