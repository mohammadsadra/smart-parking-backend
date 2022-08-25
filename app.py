from flask import Flask, jsonify, make_response, request

import time
# import paho.mqtt.client as paho
# from paho import mqtt
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, true
from flask_restful import Api, Resource
from flask_cors import CORS
from sqlalchemy.orm import backref
from datetime import datetime, timedelta
# import jwt
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint


# Swagger configs
SWAGGER_URL = ''
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={
    'app_name': "i-Park API"
})

app = Flask(__name__)

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

CORS(app)
cors = CORS(app, resource={
    r"/*": {
        "origins": "*"
    }
})
api = Api(app)
pv_key = 'NTNv7j0TuYARvmNMmWXo6fKvM4o6nv/aUi9ryX38ZH+L1bkrnD1ObOQ8JAUmHCBq7Iy7otZcyAagBLHVKvvYaIpmMuxmARQ97jUVG16Jkpkp1wXOPsrF9zwew6TpczyHkHgX5EuLg2MeBuiT/qJACs1J0apruOOJCg/gOtkjB4c='
app.config['SECRET_KEY'] = pv_key
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.curdir, 'localServer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Parking(db.Model):
    __tablename__ = 'Parking'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    name = Column(String, nullable=False)
    description = Column(String(100))
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    free_capacity = Column(Integer, nullable=False)
    reserved_capacity = Column(Integer, nullable=False)
    reserved_free_capacity = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    working_hours = Column(String, nullable=False)
    working_days = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('User.id'), nullable=False)

class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=False)
    role = Column(String, nullable=False)

class SavedLocation(db.Model):
    __tablename__ = 'SavedLocation'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    user = Column(Integer, ForeignKey('User.id'), nullable=False)

class SavedParking(db.Model):
    __tablename__ = 'SavedParking'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    parking = Column(Integer, ForeignKey('Parking.id'), nullable=False)
    user = Column(Integer, ForeignKey('User.id'), nullable=False)

class Reservation(db.Model):
    __tablename__ = 'Reservation'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    parking_id = Column(Integer, ForeignKey('Parking.id'), nullable=False)
    user = Column(Integer, ForeignKey('User.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    paid = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class Car(db.Model):
    __tablename__ = 'car'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    license_plate = Column(String, nullable=False)
    user = Column(Integer, ForeignKey('User.id'), nullable=False)
    model = Column(String, nullable=True)
    color = Column(String, nullable=True)





# @app.route("/")
# def home():
#     return "Hello, this is ipark server!"


##################################################################
#####################        PARKING   #####################
##################################################################
@app.route("/parking/getall", methods=['GET'])
def get_all_parking():
    try:
        parkings = Parking.query.all()
        result = Parking.dump(parkings)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/parking/get/<id>", methods=['GET'])
def get_parking(id):
    try:
        parking = Parking.query.filter_by(guid=id).first()
        result = Parking.dump(parking)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/parking/add", methods=['POST'])
def add_parking():
    try:
        data = request.get_json()
        parking = Parking(
            guid=data['guid'],
            name=data['name'],
            description=data['description'],
            address=data['address'],
            city=data['city'],
            phone=data['phone'],
            total_capacity=data['total_capacity'],
            free_capacity=data['free_capacity'],
            reserved_capacity=data['reserved_capacity'],
            reserved_free_capacity=data['reserved_free_capacity'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            cost=data['cost'],
            working_hours=data['working_hours'],
            working_days=data['working_days'],
            picture=data['picture'],
            owner_id=data['owner_id']
        )
        db.session.add(parking)
        db.session.commit()
        return jsonify({'message': 'Parking added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/parking/update", methods=['PUT'])
def update_parking():
    try:
        data = request.get_json()
        parking = Parking.query.filter_by(guid=data['guid']).first()
        parking.name = data['name']
        parking.description = data['description']
        parking.address = data['address']
        parking.city = data['city']
        parking.phone = data['phone']
        parking.total_capacity = data['total_capacity']
        parking.free_capacity = data['free_capacity']
        parking.reserved_capacity = data['reserved_capacity']
        parking.reserved_free_capacity = data['reserved_free_capacity']
        parking.latitude = data['latitude']
        parking.longitude = data['longitude']
        parking.cost = data['cost']
        parking.working_hours = data['working_hours']
        parking.working_days = data['working_days']
        parking.picture = data['picture']
        parking.owner_id = data['owner_id']
        db.session.commit()
        return jsonify({'message': 'Parking updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/parking/delete/<id>", methods=['DELETE'])
def delete_parking(id):
    try:
        parking = Parking.query.filter_by(guid=id).first()
        db.session.delete(parking)
        db.session.commit()
        return jsonify({'message': 'Parking deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


##################################################################
#####################        USER    #####################
##################################################################
@app.route("/user/getall", methods=['GET'])
def get_all_user():
    try:
        users = User.query.all()
        result = User.dump(users)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/user/get/<id>", methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(guid=id).first()
        result = User.dump(user)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/user/add", methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        user = User(
            guid=data['guid'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password=data['password'],
            picture=data['picture'],
            role=data['role']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/user/update", methods=['PUT'])
def update_user():
    try:
        data = request.get_json()
        user = User.query.filter_by(guid=data['guid']).first()
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.password = data['password']
        user.picture = data['picture']
        user.role = data['role']
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/user/delete/<id>", methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(guid=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


##################################################################
#####################        RESERVATION    #####################
##################################################################
@app.route("/reservation/getall", methods=['GET'])
def get_all_reservation():
    try:
        reservations = Reservation.query.all()
        result = Reservation.dump(reservations)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/get/<id>", methods=['GET'])
def get_reservation(id):
    try:
        reservation = Reservation.query.filter_by(guid=id).first()
        result = Reservation.dump(reservation)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/getUserReservations/<userid>", methods=['GET'])
def get_user_reservations(userid):
    try:
        reservations = Reservation.query.filter_by(user_id=userid).all()
        result = Reservation.dump(reservations)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/add", methods=['POST'])
def add_reservation():
    try:
        data = request.get_json()
        reservation = Reservation(
            guid=data['guid'],
            parking_id=data['parking_id'],
            user_id=data['user_id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data['status'],
            created_at=data['created_at'],
            paid=data['paid'],
            cost=data['cost']

        )
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'message': 'Reservation added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/update", methods=['PUT'])
def update_reservation():
    try:
        data = request.get_json()
        reservation = Reservation.query.filter_by(guid=data['guid']).first()
        reservation.parking_id = data['parking_id']
        reservation.user_id = data['user_id']
        reservation.start_time = data['start_time']
        reservation.end_time = data['end_time']
        reservation.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Reservation updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/delete/<id>", methods=['DELETE'])
def delete_reservation(id):
    try:
        reservation = Reservation.query.filter_by(guid=id).first()
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'message': 'Reservation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


##################################################################
#####################        CARS    #####################
##################################################################
@app.route("/car/get/<id>", methods=['GET'])
def get_car(id):
    try:
        car = Car.query.filter_by(guid=id).first()
        result = Car.dump(car)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/car/getall", methods=['GET'])
def get_all_car():
    try:
        cars = Car.query.all()
        result = Car.dump(cars)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/car/getUserCar/<userid>", methods=['POST'])
def get_user_car(userid):
    try:
        cars = Car.query.filter_by(user_id=userid).all()
        result = Car.dump(cars)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/car/update", methods=['PUT'])
def update_car():
    try:
        data = request.get_json()
        car = Car.query.filter_by(guid=data['guid']).first()
        car.user_id = data['user_id']
        car.model = data['model']
        car.color = data['color']
        car.plate = data['plate']
        car.picture = data['picture']
        db.session.commit()
        return jsonify({'message': 'Car updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

##################################################################
#####################    UserSavedParking    #####################
##################################################################
@app.route("/savedparking/get/<id>", methods=['GET'])
def get_userSavedParking(id):
    try:
        userSavedParking = SavedParking.query.filter_by(guid=id).first()
        result = SavedParking.dump(userSavedParking)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/savedparking/getallusersavedparking/<userid>", methods=['GET'])
def get_all_userSavedParking(userid):
    try:
        userSavedParking = SavedParking.query.filter_by(user_id=userid).all()
        result = SavedParking.dump(userSavedParking)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/savedparking/add", methods=['POST'])
def add_userSavedParking():
    try:
        data = request.get_json()
        userSavedParking = SavedParking(
            guid=data['guid'],
            user_id=data['user_id'],
            parking_id=data['parking_id']
        )
        db.session.add(userSavedParking)
        db.session.commit()
        return jsonify({'message': 'UserSavedParking added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/savedparking/delete/<id>", methods=['DELETE'])
def delete_userSavedParking(id):
    try:
        userSavedParking = SavedParking.query.filter_by(guid=id).first()
        db.session.delete(userSavedParking)
        db.session.commit()
        return jsonify({'message': 'UserSavedParking deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

##################################################################
#####################     UserSavedLocation  #####################
##################################################################
@app.route("/savedlocation/get/<id>", methods=['GET'])
def get_saved_location(id):
    try:
        userSavedLocation = SavedLocation.query.filter_by(guid=id).first()
        result = SavedLocation.dump(userSavedLocation)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/savedlocation/getallusersavedlocation/<userid>", methods=['GET'])
def get_all_saved_location(userid):
    try:
        userSavedLocation = SavedLocation.query.filter_by(user_id=userid).all()
        result = SavedLocation.dump(userSavedLocation)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})
