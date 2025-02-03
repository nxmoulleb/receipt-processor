import json
import jsonschema
from jsonschema import validate
import uuid
from flask import *
from datetime import datetime
import math

app = Flask(__name__)

schema = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'retailer', 'purchaseDate', 'purchaseTime', 'items', 'total'
    ],
    'properties': {
        'retailer': {'type': 'string'},
        'purchaseDate': {'type': 'string', 'pattern': '^\d{4}-\d{2}-\d{2}$'},
        'purchaseTime': {'type': 'string', 'pattern': '^\d{2}:\d{2}$'},
        'items': {
            'type': 'array', 
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'shortDescription': {'type': 'string'},
                    'price': {'type': 'string', 'pattern': '^\\d+\\.\\d{2}$'}
                }
            }},
        'total': {'type': 'string', 'pattern': '^\\d+\\.\\d{2}$'}
    }
}

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid date format or non-existent date.')

def validate_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        raise ValueError('Invalid time format or non-existent time.')

def get_points(json):
    total = 0
    for char in json['retailer']:
        if char.isalnum():
            total += 1

    total_cost = float(json['total'])

    if total_cost % 1 == 0:
        total += 50
    
    if total_cost % .25 == 0:
        total += 25

    total += 5* (len(json['items']) // 2)

    for item in json['items']:
        if len(item['shortDescription'].strip()) % 3 == 0:
            total += math.ceil(float(item['price']) * .2)
    
    if(int(json['purchaseDate'].split('-')[-1]) % 2 == 1):
        total += 6
    
    hour_purchased = int(json['purchaseTime'].split(':')[0])
    if(14 <= hour_purchased < 16):
        total += 10

    return total


@app.route('/receipts/process', methods=['POST'])
def handle_process():
    receipt = request.get_json()
    try:
        jsonschema.validate(instance=receipt, schema=schema)
        validate_date(receipt['purchaseDate'])
        validate_time(receipt['purchaseTime'])
    except jsonschema.exceptions.ValidationError as ex:
        abort(Response('The receipt is invalid.', 400))
    except ValueError as ex:
        abort(Response('The receipt is invalid.', 400))
    
    id = str(uuid.uuid4())
    points = get_points(receipt)
    db[id] = points

    return jsonify({'id': id})

@app.route('/receipts/<id>/points')
def handle_points(id):
    points = db.get(id)
    if points is None:
        abort(Response('No receipt found for that ID.', 404))
    return jsonify({'points': db[id]})

if __name__ == '__main__':
    db = {}
    app.run(host='0.0.0.0', port=8080, debug=True)