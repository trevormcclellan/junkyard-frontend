from flask import Blueprint, render_template, request, jsonify
from config import *
from .services import lkq
from pymongo import MongoClient
import requests

main_bp = Blueprint('main', __name__, template_folder='templates')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection_jacks = db[MONGO_COLLECTION_NAME_JACKS]
collection_lkq = db[MONGO_COLLECTION_NAME_LKQ]
collection_picknpull = db[MONGO_COLLECTION_NAME_PICKNPULL]
collection_pullapart = db[MONGO_COLLECTION_NAME_PULLAPART]
collection_upullandsave = db[MONGO_COLLECTION_NAME_UPULLANDSAVE]

@main_bp.route('/')
def index():
    return render_template('main/index.html',
        cars_jacks=list(collection_jacks.find()),
        cars_lkq=list(collection_lkq.find()),
        cars_picknpull=list(collection_picknpull.find()),
        cars_pullapart=list(collection_pullapart.find()),
        cars_upullandsave=list(collection_upullandsave.find())
    )

@main_bp.route('/junkyard/<yard_name>', methods=['GET'])
def junkyard_page(yard_name):
    # makes = get_makes_from_api(yard_name)
    # Initially, models will be empty until a make is selected
    makes = []
    models = []
    return render_template(f'main/{yard_name}.html', yard_name=yard_name, makes=makes, models=models, results=[])

@main_bp.route('/api/search', methods=['GET'])
def search_inventory():
    results = []
    yard_name = request.args.get('yard_name')
    if yard_name == 'lkq':
        query = request.args.get('query')
        location = request.args.get('location')
        results = lkq.search_inventory(query, location)

    else:
        make = request.args.get('make')
        model = request.args.get('model')
        location = request.args.get('location') if 'location' in request.args else None
    # Fetch inventory search results
    # results = search_inventory_from_api(make, model, yard_name, location)
    return jsonify({'results': results})
