from flask import Blueprint, render_template, request, jsonify
from config import *
from .services import tearapart, pullnsave, utpap
from pymongo import MongoClient
import requests

utah_bp = Blueprint('utah', __name__, template_folder='templates')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection_tearapart = db[MONGO_COLLECTION_NAME_TEARAPART]
collection_utpap = db[MONGO_COLLECTION_NAME_UTPAP]
collection_pullnsave = db[MONGO_COLLECTION_NAME_PULLNSAVE]

def get_makes_from_api(yard_name):
    if yard_name == 'tearapart':
        return tearapart.get_makes_from_tearapart()
    elif yard_name == 'pullnsave':
        return pullnsave.get_makes_from_pullnsave()
    elif yard_name == 'utpap':
        return utpap.get_modelmap_from_utpap()

def get_models_from_api(make, yard_name):
    if yard_name == 'tearapart':
        return tearapart.get_models_from_tearapart(make)
    elif yard_name == 'pullnsave':
        return pullnsave.get_models_from_pullnsave(make)

def search_inventory_from_api(make, model, yard_name, location=None):
    if yard_name == 'tearapart':
        return tearapart.search_tearapart_inventory(make, model)
    elif yard_name == 'pullnsave':
        return pullnsave.search_pullnsave_inventory(make, model, location)
    elif yard_name == 'utpap':
        return utpap.search_utpap_inventory(make, model)

@utah_bp.route('/')
def index():
    return render_template('utah/index.html',
        cars_tearapart=list(collection_tearapart.find()),
        cars_utpap=list(collection_utpap.find()),
        cars_pullnsave=list(collection_pullnsave.find())
    )

@utah_bp.route('/api/images/pullnsave/<stock_num>/<yard>', methods=['GET'])
def pullnsave_image(stock_num, yard):
    # Return the number of images for the given stock number
    url = f"https://app.pullnsaveapp.com/v1/Vehicles/Images/StockId/{stock_num}-{yard}/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else 0
        return jsonify({"count": count})

    else:
        return jsonify({"error": "Failed to fetch images"}), 500
        
@utah_bp.route('/junkyard/<yard_name>', methods=['GET'])
def junkyard_page(yard_name):
    makes = get_makes_from_api(yard_name)
    # Initially, models will be empty until a make is selected
    models = []
    return render_template(f'utah/{yard_name}.html', yard_name=yard_name, makes=makes, models=models, results=[])

@utah_bp.route('/api/models', methods=['GET'])
def get_models():
    make = request.args.get('make')
    yard_name = request.args.get('yard_name')
    # Fetch and return models based on selected make
    models = get_models_from_api(make, yard_name)
    return jsonify({'models': models})

@utah_bp.route('/api/search', methods=['GET'])
def search_inventory():
    make = request.args.get('make')
    model = request.args.get('model')
    yard_name = request.args.get('yard_name')
    location = request.args.get('location') if 'location' in request.args else None
    # Fetch inventory search results
    results = search_inventory_from_api(make, model, yard_name, location)
    return jsonify({'results': results})