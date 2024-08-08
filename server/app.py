#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        scientists_list = [scientist.to_dict(rules=['-missions',]) for scientist in Scientist.query.all()]
        return scientists_list, 200
    elif request.method == 'POST':
        try:
            scientist = Scientist(
                name = request.json.get('name'),
                field_of_study = request.json.get('field_of_study')
            )
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 201
        except ValueError:
            return {'errors': ['validation errors']}, 400

    
@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()
    if not scientist:
        return {'error': 'Scientist not found'}, 404
    elif request.method == 'GET':
        return scientist.to_dict(), 200
    elif request.method == 'PATCH':
        try:
            for attr in request.json:
                setattr(scientist, attr, request.json.get(attr))
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 202
        except ValueError:
            return {'errors': ['validation errors']}, 400
    elif request.method == 'DELETE':
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204
    
@app.route('/planets')
def planets():
    planets_list = [planet.to_dict(rules=['-missions',]) for planet in Planet.query.all()]
    return planets_list, 200
    
@app.route('/missions', methods=['GET', 'POST'])
def missions():
    if request.method == 'GET':
        missions_list = [mission.to_dict() for mission in Mission.query.all()]
        return missions_list, 200
    elif request.method == 'POST':
        try:
            mission = Mission(
                name = request.json.get('name'),
                scientist_id = request.json.get('scientist_id'),
                planet_id = request.json.get('planet_id')
            )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except ValueError:
            return {'errors': ['validation errors']}, 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
