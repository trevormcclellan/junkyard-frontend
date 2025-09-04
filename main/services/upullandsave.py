import requests
import json

def get_makes():
    url = "https://upullandsave.com/wp-admin/admin-ajax.php"

    payload = "action=yardsmart_integration&api_call=getMakes&params%5Byear%5D=false"
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching makes: {response.status_code}")
        return []
    
def get_models(make, location):
    url = "https://upullandsave.com/wp-admin/admin-ajax.php"

    payload = f"action=yardsmart_integration&api_call=getModels&params%5Byard_id%5D={location}&params%5Byear%5D=false&params%5Bmake%5D={make}"
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching models: {response.status_code}")
        return []

def fetch_page(req_start, req_length, make, model, location):
    url = "https://upullandsave.com/wp-admin/admin-ajax.php"

    # Payload for the POST request
    payload = f"draw=1&columns%5B0%5D%5Bdata%5D=false&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=year&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=make&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=model&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=stock_number&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=color&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=yard_row&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=date_set&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=vin&columns%5B9%5D%5Bname%5D=&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=8&order%5B0%5D%5Bdir%5D=desc&order%5B0%5D%5Bname%5D=&start={req_start}&length={req_length}&search%5Bvalue%5D=&search%5Bregex%5D=false&action=yardsmart_integration&api_call=getInventoryDatatablesArray&params%5Byard_id%5D={location}&params%5Byear%5D=false&params%5Bmake%5D={make}&params%5Bmodel%5D={model}&params%5Blog%5D=true"
    headers = {
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Return JSON response directly

    except Exception as e:
        print(f"Error: Request failed - {e}")

def fetch_vehicle_details(vin):
    """Fetch vehicle details from NHTSA API using VIN."""
    try:
        nhtsa_api_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
        response = requests.get(nhtsa_api_url)
        if response.status_code == 200:
            data = response.json()
            series = data['Results'][0]['Series']
            return series
        else:
            print(f"Failed to fetch vehicle details for VIN {vin}.")
            return None
    except Exception as e:
        print(f"Error fetching vehicle details for VIN {vin}: {str(e)}")
        return None

def search_inventory(make, model, location):
    try:
        results = []
        cars = []
        first_page_length = 10  # Number of records to fetch per page
        if not model:
            model = "false"
        data = fetch_page(0, first_page_length, make, model, location)

        if 'data' in data:
            cars = data['data']
        else:
            print(f"Error: 'data' key not found in the response: {data}")
            return []

        records_total = data.get('recordsTotal', 0)
        if records_total > first_page_length:
            data = fetch_page(first_page_length, records_total - first_page_length, make, model, location)
            if 'data' in data:
                cars.extend(data['data'])
            else:
                print(f"Error: 'data' key not found in the response: {data}")
                return []


        # Iterate through each car in the response
        for car in cars:
            try:
                year = int(car['year'])
                car_make = (car['make']).upper()
                car_model = (car['model']).upper()
                vin = car['vin']
                stock_num = car['stock_number']
                color = car['color']
                row = car['yard_row']
                date = car['date_set']
                image_url = car['images'][0]['url'] if car['images'] else None
                image_urls = [image['url'] for image in car['images']] if car['images'] else []
                    
                car_data = {
                    "year": year,
                    "make": car_make,
                    "model": car_model,
                    "vin": vin,
                    "stock_num": stock_num,
                    "color": color,
                    "row": row,
                    "date": date,
                    "image": image_url,
                    "image_urls": image_urls
                }

                if len(vin) == 17:  # Check if VIN is 17 characters
                    series = fetch_vehicle_details(vin)
                    if series:
                        car_data['series'] = series
                    
                results.append(car_data)

            except ValueError:
                # Handle cases where conversion to int fails
                print(f"Skipping row with invalid data: {car}")

        return results

    except Exception as e:
        print(f"An error occurred in U Pull & Save: {e}")