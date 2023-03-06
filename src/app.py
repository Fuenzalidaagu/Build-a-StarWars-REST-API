"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

people_list = [{'id': 1, 'name': 'Luke Skywalker'}, {'id': 2, 'name': 'Leia Organa'}]
planets_list = [{'id': 1, 'name': 'Tatooine'}, {'id': 2, 'name': 'Alderaan'}]

users_list = [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}]
user_favorites = {'planets': [1], 'people': [2]}

@app.route('/people', methods=['GET'])
def get_people():
    return jsonify(people_list)

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    people_info = next((p for p in people_list if p['id'] == people_id), None)
    if not people_info:
        raise NotFound(f"La people con id {people_id} no existe.")
    return jsonify(people_info)

@app.route('/planets', methods=['GET'])
def get_planets():
    return jsonify(planets_list)

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet_info = next((p for p in planets_list if p['id'] == planet_id), None)
    if not planet_info:
        raise NotFound(f"El planet con id {planet_id} no existe.")
    return jsonify(planet_info)

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users_list)

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    return jsonify(user_favorites)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet_info = next((p for p in planets_list if p['id'] == planet_id), None)
    if not planet_info:
        raise NotFound(f"El planet con id {planet_id} no existe.")
    if planet_id in user_favorites['planets']:
        raise BadRequest(f"El planet con id {planet_id} ya es un favorito.")
    user_favorites['planets'].append(planet_id)
    return jsonify(success=True)

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    people_info = next((p for p in people_list if p['id'] == people_id), None)
    if not people_info:
        raise NotFound(f"La people con id {people_id} no existe.")
    if people_id in user_favorites['people']:
        raise BadRequest(f"La people con id {people_id} ya es un favorito.")
    user_favorites['people'].append(people_id)
    return jsonify(success=True)

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    if planet_id not in user_favorites['planets']:
        raise BadRequest(f"El planet con id {planet_id} no es un favorito.")
    user_favorites['planets'].remove(planet_id)
    return jsonify(success=True)

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    if people_id not in user_favorites['people']:
        raise BadRequest(f"La people con id {people_id} no es un favorito.")
    user_favorites['people'].remove(people_id)
    return jsonify(success=True)


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
