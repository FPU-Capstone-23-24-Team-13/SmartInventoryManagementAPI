#from flask import Flask, render_template, send_from_directory, make_response, request
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import make_engine, get_session, Item, Location, Sensor
from psycopg2.errors import ForeignKeyViolation, NotNullViolation
from sqlalchemy.exc import IntegrityError
import database as db
import util

app = Flask(__name__)
CORS(app, origins=['http://localhost:63343', 'http://localhost:80', 'http://localhost:443'])
'''
code 1: Entry missing attribute and thus could not be updated
code 2: Entry could not be created with incomplete entries
code 3: Entry not found with key
code 4: Foreign Key does not exist
code 5: Invalid entry submitted for object creation
'''
'''
Create Database session
'''
def create_session():
    engine = make_engine("LRH_db")
    return get_session(engine)

'''
Returns a list of all SKUs from database
'''
@app.route("/item/", methods=['GET'])
def get_item_list():
    session = create_session()
    items = session.query(Item).all()
    session.close()
    skus = [item.sku for item in items]
    endpoints = [f"/item/{sku}" for sku in skus]
    return_arr = [{'sku': sku, 'endpoint': endpoint} for sku, endpoint in zip(skus, endpoints)]
    return jsonify(return_arr)
'''
Returns information about the item corresponding to a specific SKU
'''
@app.route("/item/<sku>", methods=['GET'])
def get_item_info(sku):
    session = create_session()
    item = session.query(Item).filter_by(sku=sku).first()
    session.close()
    if item:
        item_info = {
            'sku': item.sku,
            'name': item.name,
            'description': item.description,
            'reorder_threshold': item.reorder_threshold,
            'count': item.count,
            'location_id': item.location_id
        }
        return jsonify(item_info)
    return jsonify({'message': f'Item not found with sku {sku}',
                    'code': 3})
'''
Edits the database with information from request
'''
@app.route("/item/<sku>", methods=['POST'])
def edit_item_info(sku):
    data = request.json
    session = create_session()
    item = session.query(Item).filter_by(sku=sku).first()
    output = jsonify({'message': 'Some Default Message'})
    if item:
        columns = Item.__table__.columns
        column_keys = [column.key for column in columns]
        for key, value in data.items():
            if key in column_keys:
                setattr(item, key, value)
            else:
                session.close()
                return jsonify({'message': f'Item has no attribute {key} and thus could not be updated',
                                'code': 1})
        session.commit()
        output = jsonify({'message': f'Item has been updated with values.',
                          'data': data,
                          'code': 0})
    else:
        try:
            item = Item(**data)
            session.add(item)
            output = jsonify({'message:': f'sku: {data['sku']} was successfully created',
                              'datafields': data,
                              'code': 0})
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if isinstance(e.orig, ForeignKeyViolation):
                output = jsonify({'message': 'Foreign Key Violation occurred: location does not yet exist. ',
                              'code': 4})
            elif isinstance(e.orig, NotNullViolation):
                columns = Item.__table__.columns
                missing_required = [column.key for column in columns if column.key not in data.keys() and not column.nullable]
                output = jsonify({'message': 'Item could not be created with incomplete entries: ',
                                  'missing required columns': missing_required,
                                  'code': 2}), 400
        except Exception as e:
            session.rollback()
            output = jsonify({'message': 'Item could not be created because of invalid entry.',
                              'code': 5})
    session.close()
    return output

'''
Returns a list of all sensors from database
'''
@app.route("/sensor/", methods=['GET'])
def get_sensor_list():
    session = create_session()
    sensors = session.query(Sensor).all()
    session.close()
    sensor_ids = [sensor.sensor_id for sensor in sensors]
    endpoints = [f"/sensor/{sensor_id}" for sensor_id in sensor_ids]
    return_arr = [{'sensor_id': sensor_id, 'endpoint': endpoint} for sensor_id, endpoint in zip(sensor_ids, endpoints)]
    return jsonify(return_arr)
'''
Returns information about the sensor corresponding to a specific id
'''
@app.route("/sensor/<sensor_id>", methods=['GET'])
def get_sensor_info(sensor_id):
    session = create_session()
    sensor = session.query(Sensor).filter_by(sensor_id=sensor_id).first()
    if sensor is not None and sensor.sku is not None:
        item_obj = session.query(Item).filter_by(sku=sensor.sku).first()
        endpoint = f"/item/{item_obj.sku}"
        item = {'sku': item_obj.sku, 'endpoint': endpoint}

    else:
        item = None

    session.close()
    if sensor:
        sensor_info = {
            'sensor_id': sensor.sensor_id,
            'item': item
        }
        return jsonify(sensor_info)
    return jsonify({'message': f'Sensor not found with sensor_id {sensor_id}',
                    'code': 3})
'''
Edits the database with information from request
'''
@app.route("/sensor/<sensor_id>", methods=['POST'])
def edit_sensor_info(sensor_id):
    data = request.json
    session = create_session()
    sensor = session.query(Sensor).filter_by(sensor_id=sensor_id).first()
    output = jsonify({'message': 'Some Default Message'})
    if sensor:
        columns = Sensor.__table__.columns
        column_keys = [column.key for column in columns]
        for key, value in data.items():
            if key in column_keys:
                setattr(sensor, key, value)
            else:
                session.close()
                return jsonify({'message': f'Sensor has no attribute {key} and thus could not be updated',
                                'code': 1})
        session.commit()
        output = jsonify({'message': f'Sensor has been updated with values.',
                          'data': data,
                          'code': 0})
    else:
        try:
            sensor = Sensor(**data)
            session.add(sensor)
            output = jsonify({'message:': f'sensor_id: {data['sensor_id']} was successfully created',
                              'datafields': data,
                              'code': 0})
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if isinstance(e.orig, ForeignKeyViolation):
                output = jsonify({'message': 'Foreign Key Violation occurred: Item does not yet exist. ',
                                  'code': 4})
            elif isinstance(e.orig, NotNullViolation):
                columns = Sensor.__table__.columns
                missing_required = [column.key for column in columns if
                                    column.key not in data.keys() and not column.nullable]
                output = jsonify({'message': 'Sensor could not be created with incomplete entries.',
                                  'missing required columns': missing_required,
                                  'code': 2}), 400
        except Exception as e:
            session.rollback()
            output = jsonify({'message': 'Item could not be created because of invalid entry.',
                              'code': 5})
    session.close()
    return output

'''
Returns a list of all locations from database
'''
@app.route("/location/", methods=['GET'])
def get_location_list():
    session = create_session()
    locations = session.query(Location).all()
    session.close()
    locations_data = [
        {
            'location_id': location.location_id,
            'storeroom_name': location.storeroom_name,
            'shelf_name': location.shelf_name
        } for location in locations
    ]
    return jsonify(locations_data)
'''
Returns information about the location corresponding to a specific location_id
'''
@app.route("/location/<location_id>", methods=['GET'])
def get_location_info(location_id):
    session = create_session()
    location = session.query(Location).filter_by(location_id=location_id).first()
    if location:
        items = [item.sku for item in location.items]
        location_info = {
            'location_id': location.location_id,
            'storeroom_name': location.storeroom_name,
            'shelf_name': location.shelf_name,
            'items': items,
        }
        output = jsonify(location_info)
    else:
        output = jsonify({'message': f'Location not found with location_id {location_id}',
                    'code': 3})
    session.close()
    return output
'''
Edits the database with information from request
'''
@app.route("/location/<location_id>", methods=['POST'])
def edit_location_info(location_id):
    data = request.json
    session = create_session()
    location = session.query(Location).filter_by(location_id=location_id).first()
    output = jsonify({'message': 'Some Default Message'})
    if location:
        columns = Location.__table__.columns
        column_keys = [column.key for column in columns]
        for key, value in data.items():
            if key in column_keys:
                setattr(location, key, value)
            else:
                session.close()
                return jsonify({'message': f'Location has no attribute {key} and thus could not be updated',
                                'code': 1})
        session.commit()
        output = jsonify({'message': f'Location has been updated with values.',
                          'data': data,
                          'code': 0})
    else:
        try:
            item = Location(**data)
            session.add(item)
            output = jsonify({'message:': f'location_id: {data['location_id']} was successfully created',
                              'datafields': data,
                              'code': 0})
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if isinstance(e.orig, ForeignKeyViolation):
                output = jsonify({'message': 'Foreign Key Violation occurred: Items do not yet exist. ',
                              'code': 4})
            elif isinstance(e.orig, NotNullViolation):
                columns = Location.__table__.columns
                missing_required = [column.key for column in columns if column.key not in data.keys() and not column.nullable]
                output = jsonify({'message': 'Location could not be created with incomplete entries.',
                                  'missing required columns': missing_required,
                                  'code': 2}), 400
        except Exception as e:
            session.rollback()
            output = jsonify({'message': 'Item could not be created because of invalid entry.',
                              'code': 5})
    session.close()
    return output
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)