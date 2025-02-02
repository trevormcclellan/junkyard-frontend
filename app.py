from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re

load_dotenv()

app = Flask(__name__)

# MongoDB connection details
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_COLLECTION_NAME_TEARAPART = os.getenv('MONGO_COLLECTION_NAME_TEARAPART')
MONGO_COLLECTION_NAME_UTPAP = os.getenv('MONGO_COLLECTION_NAME_UTPAP')
MONGO_COLLECTION_NAME_PULLNSAVE = os.getenv('MONGO_COLLECTION_NAME_PULLNSAVE')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection_tearapart = db[MONGO_COLLECTION_NAME_TEARAPART]
collection_utpap = db[MONGO_COLLECTION_NAME_UTPAP]
collection_pullnsave = db[MONGO_COLLECTION_NAME_PULLNSAVE]

# Tear-A-Part
def fetch_tearapart_nonce():
    url = "https://tearapart.com/used-auto-parts/inventory/"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', {'id': 'sif_plugin js frontend main-js-extra'})
    script_content = script_tag.string

    nonce_match = re.search(r'sif_ajax_nonce":"(\w+)"', script_content)
    return nonce_match.group(1) if nonce_match else None

def get_makes_from_tearapart():
    url = "https://tearapart.com/wp-admin/admin-ajax.php"

    # Payload for the POST request
    payload = {
        "action": "sif_get_makes",
        "sif_verify_request": fetch_tearapart_nonce(),
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        makes = []
        for option in soup.find_all('option'):
            makes.append({'value': option.get('value'), 'text': option.text.strip()})
        return makes
    else:
        return []
    
def get_models_from_tearapart(make):
    url = "https://tearapart.com/wp-admin/admin-ajax.php"

    # Payload for the POST request
    payload = {
        "action": "sif_update_models",
        "sif_verify_request": fetch_tearapart_nonce(),
        "make": make,
        "state": "0"
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        models = [{'value': '', 'text': 'Any'}]
        for option in soup.find_all('option'):
            models.append({'value': option.get('value'), 'text': option.text.strip()})
        return models
    else:
        return []

def search_tearapart_inventory(make, model):
    url = "https://tearapart.com/wp-admin/admin-ajax.php"

    # Payload for the POST request
    payload = {
        "sif_form_field_store": "SALT LAKE CITY",
        "sif_form_field_make": f"{make}",
        "makes-sorting-order": "0",
        "models-sorting-order": "0",
        "action": "sif_search_products",
        "sif_verify_request": fetch_tearapart_nonce(),
        "sorting[key]": "iyear",
        "sorting[state]": "0",
        "sorting[type]": "int"
    }

    if model:
        payload["sif_form_field_model"] = f"{model}"

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Check for HTTP errors
        results = []

        data = response.json()  # Attempt to parse JSON response
        if 'products' in data:
            cars = data['products']
            for car in cars:
                year = int(car['iyear'])
                model = (car['model'] or car['hol_model']).upper()
                color = car['color']
                vin = car['vin'].strip()
                stock_num = car['stocknumber']
                reference = car['reference']
                row = car['vehicle_row']
                date = car['yard_date']
                image_url = car['image_url'].strip().split('"')[1]  # Extract image URL from HTML string

                car_data = {
                    "year": year,
                    "model": model,
                    "color": color,
                    "vin": vin,
                    "stock_num": stock_num,
                    "reference": reference,
                    "row": row,
                    "date": date,
                    "image": image_url
                }
                results.append(car_data)
            return results

    except Exception as e:
        return []

# Pull N Save
# ----------------
def get_makes_from_pullnsave():
    url = "https://pullnsave.com/wp-admin/admin-ajax.php"

    payload = "action=getMakes"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        makes = []
        for option in soup.find_all('option'):
            makes.append({'value': option.get('value'), 'text': option.text.strip()})
        return makes
    else:
        return []
    
def get_models_from_pullnsave(make):
    url = "https://pullnsave.com/wp-admin/admin-ajax.php"

    payload = f"Form=searchVehicleForm&Year=0&endYear=0&Make={make}&action=getModels"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        models = []
        for option in soup.find_all('option'):
            models.append({'value': option.get('value'), 'text': option.text.strip()})
        return models
    else:
        return []
    
def search_pullnsave_inventory(make, model, location=None):
    try:
        if yard_name == 'pullnsave':
            url = "https://pullnsave.com/wp-admin/admin-ajax.php"

            payload = f"makes={make}&models={model}&years=0&endYears=0&store={location}&beginDate=&endDate=&action=getVehicles"
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'class': 'table', 'id': 'vehicletable1'})
                rows = table.find('tbody').find_all('tr')

                results = []
                for row in rows:
                    # Get all the columns in the row
                    cols = row.find_all('td')

                    # Extract the image URL
                    img_tag = cols[0].find('img')
                
                    # Extract the image URL from the 'src' attribute
                    if img_tag and 'src' in img_tag.attrs:
                        image = img_tag['src']
                    else:
                        image = None  # Handle case where no image is found

                    # Extract text from each column and strip any extra whitespace
                    col_data = [col.text.strip() for col in cols]
                    if col_data:
                        year = int(col_data[1])
                        model = col_data[2].upper()
                        date = col_data[3]
                        row = col_data[4]
                        yard_name = col_data[5]
                        color = col_data[6]
                        stock_num = col_data[7]
                        vin = col_data[8]

                        car_data = {
                            "yard": location,
                            "year": year,
                            "model": model,
                            "color": color,
                            "vin": vin,
                            "stock_num": stock_num,
                            "row": row,
                            "date": date,
                            "image": image
                        }
                        results.append(car_data)
                return results
            else:
                return []
    except Exception as e:
        return []

# UTPAP
def get_modelmap_from_utpap():
    url = f"https://utpap.com/search-inventory_orem.php"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the script tag containing the modelMap JavaScript variable
        script_tag = soup.find('script', text=lambda text: text and 'var modelMap' in text)

        if script_tag:
            # Extract the modelMap JavaScript object using regex or string manipulation
            script_content = script_tag.string.strip()
            # Extract the modelMap object using the known JavaScript variable assignment format
            start_index = script_content.find('var modelMap = ') + len('var modelMap = ')
            end_index = script_content.find('};', start_index) + 1
            model_map_js = script_content[start_index:end_index]
            
            model_map = eval(model_map_js)  # Parse the JS object into a Python dictionary

            # Return the model map to the frontend
            return model_map
        else:
            return jsonify({"error": "Model map not found in the HTML response."}), 404
    else:
        return jsonify({"error": f"Failed to fetch data, status code: {response.status_code}"}), 500

def search_utpap_inventory(make, model):
    url = f"https://utpap.com/search-inventory_orem.php?make={make}&model={model}"
    print(url)
    payload = {}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'resultsTable', 'id': 'cars-table'})
    results = []

    if table:
        # Find all rows in the table
        rows = table.find_all('tr')
        
        for row in rows:
            # Get all the columns in the row
            cols = row.find_all('td')
            # Extract text from each column and strip any extra whitespace
            col_data = [col.text.strip() for col in cols]
            if col_data:
                year = int(col_data[0])
                model = col_data[2].upper()
                stock_num = col_data[3]
                engine = col_data[4]
                # color = col_data[4]
                row = col_data[5]
                date = col_data[6]
                image = f"https://utpap.com/Orem-inventory-photos/{stock_num}.jpeg"

                car_data = {
                    "year": year,
                    "model": model,
                    "engine": engine,
                    # "color": color,
                    "stock_num": stock_num,
                    "row": row,
                    "date": date,
                    "image": image
                }
                results.append(car_data)
        return results
    else:
        return []

def get_makes_from_api(yard_name):
        if yard_name == 'tearapart':
            return get_makes_from_tearapart()
        elif yard_name == 'pullnsave':
            return get_makes_from_pullnsave()
        elif yard_name == 'utpap':
            return get_modelmap_from_utpap()

def get_models_from_api(make, yard_name):
    if yard_name == 'tearapart':
        return get_models_from_tearapart(make)
    elif yard_name == 'pullnsave':
        return get_models_from_pullnsave(make)

def search_inventory_from_api(make, model, yard_name, location=None):
    if yard_name == 'tearapart':
        return search_tearapart_inventory(make, model)
    elif yard_name == 'pullnsave':
        return search_pullnsave_inventory(make, model, location)
    elif yard_name == 'utpap':
        return search_utpap_inventory(make, model)

@app.route('/')
def index():
    # Fetch data from MongoDB collections
    cars_tearapart = list(collection_tearapart.find())
    cars_utpap = list(collection_utpap.find())
    cars_pullnsave = list(collection_pullnsave.find())
    
    return render_template('index.html', cars_tearapart=cars_tearapart, cars_utpap=cars_utpap, cars_pullnsave=cars_pullnsave)

@app.route('/junkyard/<yard_name>', methods=['GET'])
def junkyard_page(yard_name):
    makes = get_makes_from_api(yard_name)
    # Initially, models will be empty until a make is selected
    models = []
    return render_template(f'{yard_name}.html', yard_name=yard_name, makes=makes, models=models, results=[])

@app.route('/api/models', methods=['GET'])
def get_models():
    make = request.args.get('make')
    yard_name = request.args.get('yard_name')
    # Fetch and return models based on selected make
    models = get_models_from_api(make, yard_name)
    return jsonify({'models': models})

@app.route('/api/search', methods=['GET'])
def search_inventory():
    make = request.args.get('make')
    model = request.args.get('model')
    yard_name = request.args.get('yard_name')
    location = request.args.get('location') if 'location' in request.args else None
    # Fetch inventory search results
    results = search_inventory_from_api(make, model, yard_name, location)
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
