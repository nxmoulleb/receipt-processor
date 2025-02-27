import jsonschema
import uuid
from flask import *
from datetime import datetime
import math

app = Flask(__name__)

# Schema for schema validation of the json
schema = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'retailer', 'purchaseDate', 'purchaseTime', 'items', 'total'
    ],
    'properties': {
        'retailer': {'type': 'string', 'pattern': '^[\\w\\s\\-&]+$'},
        'purchaseDate': {'type': 'string'},
        'purchaseTime': {'type': 'string'},
        'items': {
            'type': 'array', 
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'shortDescription': {'type': 'string', 'pattern': '^[\\w\\s\\-]+$'},
                    'price': {'type': 'string', 'pattern': '^\\d+\\.\\d{2}$'}
                }
            }},
        'total': {'type': 'string', 'pattern': '^\\d+\\.\\d{2}$'}
    }
}

def validate_date(date_str):
    """
    Validates the date string.

    Args:
        date_str (str): Date string in the format 'YYYY-MM-DD'.

    Raises:
        ValueError: If the date string is in an invalid format or represents a date that doesnt exist.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid date format or non-existent date.')


def validate_time(time_str):
    """
    Validates the time string.

    Args:
        time_str (str): Time string in the format 'HH:MM'.

    Raises:
        ValueError: If the time string is in an invalid format or represents a time that doesnt exist.
    """
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        raise ValueError('Invalid time format or non-existent time.')


def get_points(json):
    """
    Calculates the points for a receipt based on the rules given.

    Args:
        json (dict): Receipt JSON object.

    Returns:
        int: Total points calculated.
    """

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
    """
    Validates the receipt JSON using the schema, calculates points, and stores the result.

    Returns:
        Response: JSON response containing the ID for the receipt or an error message.
    """

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
    """
    Retrieves the points for a given receipt ID.

    Args:
        id (str): ID of the receipt.

    Returns:
        Response: JSON response containing the number of points or an error message.
    """

    points = db.get(id)
    if points is None:
        abort(Response('No receipt found for that ID.', 404))
    return jsonify({'points': db[id]})


if __name__ == '__main__':
    db = {}
    app.run(host='0.0.0.0', port=8080, debug=True)