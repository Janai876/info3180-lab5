"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

import os
import psycopg2
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_wtf.csrf import generate_csrf
from flask import Flask, jsonify, request, send_file, send_from_directory
from .forms import MovieForm
from app.models import Movie

app = Flask(__name__)

# load environment variables from .env if it exists
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Som3$ec5etK*y')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# routing for the application
@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()})

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/movies', methods=['POST'])
def movies():
    form = MovieForm()

    if form.validate_on_submit():
        res = request.form

        image_file = form.poster.data
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        conn = psycopg2.connect(
            host="localhost",
            database="labfinal",
            user=os.environ.get('DATABASE_USERNAME', 'postgres'),
            password=os.environ.get('DATABASE_PASSWORD')
        )
        cur = conn.cursor()

        movie_data = {
            'title': res['title'],
            'description': res['description'],
            'poster': str(image_path),
            'created_at': str(datetime.now())
        }

        cur.execute("""
            INSERT INTO movies (title, description, poster, created_at)
            VALUES (%(title)s, %(description)s, %(poster)s, %(created_at)s);
        """, movie_data)

        conn.commit()
        cur.close()
        conn.close()

        msg = {
            "message": "Movie successfully added",
            "title": res['title'],
            "poster": filename,
            "description": res['description']
        }

        return jsonify(msg)
    else:
        errors = form_errors(form)
        return jsonify({'errors': errors})

@app.route('/api/v1/posters/<uploaddir>/<filename>')
def get_movie(uploaddir, filename):
    uploads_dir = app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(os.getcwd(), uploads_dir), filename)

@app.route('/api/v1/movies', methods=['GET'])
def list_movies():
    uploads_dir = app.config['UPLOAD_FOLDER']
    posters = get_posters()
    movies = Movie.query.all()

    movie_list = []
    for movie in movies:
        movie_dict = {
            'id': movie.id,
            'title': movie.title,
            'description': movie.description,
            'poster': "/api/v1/posters/" + str(movie.poster)
        }
        movie_list.append(movie_dict)

    return jsonify({'movies': movie_list})

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return jsonify(message="404 Not Found"), 404

def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            )
            error_messages.append
