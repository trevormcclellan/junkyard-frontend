import requests, re
from bs4 import BeautifulSoup

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