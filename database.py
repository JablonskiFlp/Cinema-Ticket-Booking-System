from sqlalchemy import create_engine, text
import os
import pandas as pd

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(db_connection_string,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                       }})

def load_movies_from_db():
    with engine.connect() as conn:
        sql_query = pd.read_sql_query("SELECT * FROM movies", conn)
        return pd.DataFrame(sql_query)

def load_seances_from_db():
    with engine.connect() as conn:
        sql_query = pd.read_sql_query("SELECT * FROM Seances", conn)
        return pd.DataFrame(sql_query)
load_seances_from_db()