import psycopg2
import os

# Get the environment, defaults to "production"
ENV = os.getenv("ENV", "production")

# Database configuration for production and test
DATABASE_CONFIG = {
    "production": {
        "dbname": "library_db",
        "user": "michele",
        "host": "localhost",
        "port": "5432",
    },
    "test": {
        "dbname": "library_test_db",
        "user": "michele",
        "host": "localhost",
        "port": "5432",
    }
}

def connect_to_db():
    """Connect to the correct PostgreSQL database based on environment."""
    config = DATABASE_CONFIG.get(ENV)

    if not config:
        raise ValueError(f"Invalid environment: {ENV}")
    
    # Safety check: ensure tests don't accidentally use the production database
    if ENV == "test" and "pytest" not in os.getenv("_", ""):
        raise RuntimeError("Attempting to run tests outside of pytest.")

    conn = psycopg2.connect(**config)
    return conn