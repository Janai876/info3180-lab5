# Import required modules
from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import psycopg2
from flask_wtf.csrf import CSRFProtect

# Initialize the Flask app
app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Create a SQLAlchemy instance
db = SQLAlchemy(app)

# Create a Migrate instance to handle database migrations
migrate = Migrate(app, db)

# Load environment variables from .env file
load_dotenv()

# Connect to the PostgreSQL database using psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="labfinal",
    user=os.environ.get('DATABASE_USERNAME', 'postgres'),
    password=os.environ.get('DATABASE_PASSWORD')
)

# Create a cursor object to execute SQL queries
with conn.cursor() as cur:
    # Create a 'movies' table if it doesn't already exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            poster VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
    """)
    # Commit changes to the database
    conn.commit()

# Close the cursor and connection objects
cur.close()
conn.close()

# Import the app's views
from app import views
