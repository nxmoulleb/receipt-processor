import json
import jsonschema
from jsonschema import validate
import uuid
from flask import *
import math

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

schema = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'retailer', 'purchaseDate', 'purchaseTime', 'items', 'total'
    ],
    'properties': {
        'retailer': {'type': 'string'},
        'purchaseDate': {'type': 'string'},
        'purchaseTime': {'type': 'string'},
        'items': {
            'type': 'array', 
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'shortDescription': {'type': 'string'},
                    'price': {'type': 'string'}
                }
            }},
        'total': {'type': 'string'}
    }
}

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
    if(hour_purchased >= 14 and hour_purchased < 16):
        total += 10

    return total


@app.route('/receipts/process', methods=['POST'])
def handle_process():
    id = str(uuid.uuid4())
    points = 0
    receipt = request.get_json()
    try:
        jsonschema.validate(instance=receipt, schema=schema)
        
        points = get_points(receipt)

        db[id] = points
        return json.dumps({'id': id})
    except jsonschema.exceptions.ValidationError as ex:
        error_message = 'The receipt is invalid.'
        abort(Response(error_message, 400))

@app.route('/receipts/<id>/points')
def handle_points(id):
    if(not id in db):
        error_message = 'No receipt found for that ID.'
        abort(Response(error_message, 404))
    return json.dumps({'points': db[id]})

if __name__ == '__main__':
    db = {}
    app.run()