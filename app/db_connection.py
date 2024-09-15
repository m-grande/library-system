import psycopg2
from psycopg2 import sql

# Configuration for PostgreSQL connection
DATABASE_CONFIG = {
    "dbname": "library_db",
    "user": "michelegrande",
    "host": "localhost",
    "port": "5432",
}


def connect_to_db():
    """Connect to the PostgreSQL database."""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn
