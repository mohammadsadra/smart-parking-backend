from flask import Flask, jsonify, make_response, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, true
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
import uuid
import paho.mqtt.client as paho
from paho import mqtt


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid) + str(client))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global lastCardIdReceived
    global lastUserId
    global turnOn
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # print("message received ", str(msg.payload.decode("utf-8")))
    # print("message topic=", msg.topic)
    # print("message qos=", msg.qos)
    # print("message retain flag=", msg.retain)

    if msg.topic == 'ipark/park1':
        print("its about park1")
        if str(msg.payload.decode("utf-8")) == '1':
            cap = update_parking_capacity(-1, 1)
            print("park1 is filled")
            client.publish("ipark/getMessage", payload=str(cap), qos=1)
        elif str(msg.payload.decode("utf-8")) == '0':
            cap = update_parking_capacity(1, 1)
            client.publish("ipark/getMessage", payload=str(cap), qos=1)
            print('park1 is free')




    # if msg.topic == 'ipark/park1':
    #     print('park status updated!')
    #     if str(lastCardIdReceived) == str(msg.payload) and turnOn:
    #         client.publish("smartoffice/light", payload="0.0", qos=1)
    #         turnOn = False
    #
    #     lastCardIdReceived = int(msg.payload)
    # if msg.topic == 'smartoffice/guid':
    #     print('guid updated')
    #     lastUserId = str(msg.payload).split("'")[1]
    #     turnOn = True


# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("ipark", "Roghaye99")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("8f8cd509697c4a1082e038331baa9680.s2.eu.hivemq.cloud", 8883)


# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("ipark/#", qos=1)

# a single publish, this can also be done in loops, etc.


# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start(run in background and doesn't block traffic) and loop_stop
client.loop_start()









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
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)

class SavedParking(db.Model):
    __tablename__ = 'SavedParking'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    parking_id = Column(Integer, ForeignKey('Parking.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)

class Reservation(db.Model):
    __tablename__ = 'Reservation'
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    parking_id = Column(Integer, ForeignKey('Parking.id'), nullable=False)
    user = Column(Integer, ForeignKey('User.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    paid = Column(Boolean, nullable=True)
    status = Column(String, nullable=True)

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
        all = []
        for item in parkings:
            all.append({
                'id':item.id,
                'guid': item.guid,
                'name': item.name,
                'description': item.description,
                'address': item.address,
                'city': item.city,
                'phone': item.phone,
                'total_capacity': item.total_capacity,
                'free_capacity': item.free_capacity,
                'reserved_capacity': item.reserved_capacity,
                'reserved_free_capacity': item.reserved_free_capacity,
                'latitude': item.latitude,
                'longitude': item.longitude,
                'cost': item.cost,
                'working_hours': item.working_hours,
                'working_days': item.working_days,
                'picture': item.picture,
                'owner_id': item.owner_id
            })

    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp

    resp = make_response(jsonify({'allParking': all}), 200)
    return resp

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


def update_parking_capacity(capacity, parking_id):
    parking = Parking.query.filter_by(id=parking_id).first()
    send_capacity = parking.free_capacity + capacity
    parking.free_capacity = send_capacity
    db.session.commit()
    print('parking capacity updated : ', send_capacity)
    return send_capacity




##################################################################
#####################        USER    #####################
##################################################################
@app.route("/user/getall", methods=['GET'])
def get_all_user():
    try:
        users = User.query.all()
        all = []
        for item in users:
            all.append({
                'id': item.id,
                'guid': item.guid,
                'name': item.name,
                'email': item.email,
                'phone': item.phone,
                'address': item.address,
                'city': item.city,
                'role': item.role
            })

    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp

    resp = make_response(jsonify({'allUser': all}), 200)
    return resp

@app.route("/user/loginregister", methods=['POST'])
def login_register():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user != None:
            if user.password == data['password']:
                return jsonify(
                    {'register': False, 'login': True, 'user': {
                    'id': user.id,
                    'guid': user.guid,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'city': user.city,
                    'role': user.role
                    }})
            else:
                return jsonify({'register': False, 'login': False})
        else:
            new = User(
                guid=str(uuid.uuid4()),
                name='',
                email=data['email'],
                password=data['password'],
                phone='',
                address='',
                city='Tehran',
                role='Normal'
            )
            db.session.add(new)
            db.session.commit()
            user = User.query.filter_by(email=data['email']).first()
            return jsonify({'register': True, 'login': True,  'user': {
                'id': user.id,
                'guid': user.guid,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'city': user.city,
                'role': user.role
            }})
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

@app.route("/savedlocation/add", methods=['POST'])
def add_saved_location():
    try:
        data = request.get_json()
        userSavedLocation = SavedLocation(
            guid=data['guid'],
            user_id=data['user_id'],
            name=data['name'],
            address=data['address'],
            city=data['city'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        db.session.add(userSavedLocation)
        db.session.commit()
        return jsonify({'message': 'UserSavedLocation added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


##################################################################
#####################        RESERVATION    #####################
##################################################################
# @app.route("/reservation/getall", methods=['GET'])
# def get_all_reservation():
#     try:
#         reservations = Reservation.query.all()
#         result = Reservation.dump(reservations)
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({'error': str(e)})
#
@app.route("/reservation/get/<id>", methods=['GET'])
def get_reservation(id):
    try:
        reservation = Reservation.query.filter_by(id=id).first()

    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp

    resp = make_response(jsonify({'value': {
        'id': reservation.id,
        'guid': reservation.guid,
        'parking_id': reservation.parking_id,
        'user': reservation.user,
        'start_time': reservation.start_time,
        'end_time': reservation.end_time,
        'cost': reservation.cost,
        'paid': reservation.paid,
        'status': reservation.status
    }}), 200)
    return resp

@app.route("/reservation/add", methods=['POST'])
def add_reservation():
    try:
        guid = str(uuid.uuid4())
        data = request.get_json()
        reservation = Reservation(
            guid=guid,
            parking_id=data['parking_id'],
            user=data['user'],
            start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S.%f'),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S.%f'),
            cost=data['cost'],
            paid=False,
            status='رزرو شده'
        )
        park = Parking.query.filter_by(id=data['parking_id']).first()
        if park.free_capacity - 1 < 0:
            return jsonify({'message': 'capacity is full!'})
        park.free_capacity = park.free_capacity - 1
        db.session.add(reservation)
        db.session.commit()

        newReservation = Reservation.query.filter_by(guid=data['guid']).first()

        return jsonify({'value': {
            'id': reservation.id,
            'guid': reservation.guid,
            'parking_id': reservation.parking_id,
            'user': reservation.user,
            'start_time': reservation.start_time,
            'end_time': reservation.end_time,
            'cost': reservation.cost,
            'paid': reservation.paid,
            'status': reservation.status
        }})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route("/reservation/delete/<id>", methods=['DELETE'])
def delete_reservation(id):
    try:
        reservation = Reservation.query.filter_by(id=id).first()
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'message': 'Reservation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reservation/getUserReservations/<userid>", methods=['GET'])
def get_user_reservations(userid):
    try:
        reservations = Reservation.query.filter_by(user=userid).all()
        all = []
        for item in reservations:
            all.append(
                {
                    'id': item.id,
                    'guid': item.guid,
                    'parking_id': item.parking_id,
                    'user': item.user,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'cost': item.cost,
                    'paid': item.paid,
                    'status': item.status
                })

        return jsonify({'all':all})
    except Exception as e:
        return jsonify({'error': str(e)})



# @app.route("/reservation/update", methods=['PUT'])
# def update_reservation():
#     try:
#         data = request.get_json()
#         reservation = Reservation.query.filter_by(guid=data['guid']).first()
#         reservation.parking_id = data['parking_id']
#         reservation.user_id = data['user_id']
#         reservation.start_time = data['start_time']
#         reservation.end_time = data['end_time']
#         reservation.status = data['status']
#         db.session.commit()
#         return jsonify({'message': 'Reservation updated successfully'})
#     except Exception as e:
#         return jsonify({'error': str(e)})
#
# @app.route("/reservation/delete/<id>", methods=['DELETE'])
# def delete_reservation(id):
#     try:
#         reservation = Reservation.query.filter_by(guid=id).first()
#         db.session.delete(reservation)
#         db.session.commit()
#         return jsonify({'message': 'Reservation deleted successfully'})
#     except Exception as e:
#         return jsonify({'error': str(e)})


##################################################################
#####################        CARS    #####################
##################################################################
