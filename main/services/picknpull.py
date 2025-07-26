import requests

def get_makes():
    url = "https://www.picknpull.com/api/vehicle/makes"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching makes: {response.status_code}")
        return []
    
def get_models(make):
    url = f"https://www.picknpull.com/api/vehicle/makes/{make}/models"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching models for make {make}: {response.status_code}")
        return []

def fetch_vehicle_details(vin):
    """Fetch vehicle details from picknpull using VIN."""
    try:
        url = f"https://www.picknpull.com/api/vehicle/{vin}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["vehicle"]
        else:
            return None
    except Exception as e:
        return None

def search_inventory(make, model):
    try:
        results = []
        url = f"https://www.picknpull.com/api/vehicle/search?&makeId={make}&modelId=0{model}&year=&distance=10&zip=43207&language=english"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            data = data[0]
            if 'vehicles' in data:
                cars = data['vehicles']
                for car in cars:
                    car_data = {
                        'location': car['locationName'],
                        'year': int(car['year']),
                        'make': car['make'].upper(),
                        'model': car['model'].upper(),
                        'vin': car['vin'],
                        'stock_num': car['barCodeNumber'],
                        'row': car['row'],
                        'date': car['dateAdded'],
                        'image_url': car['imageName']
                    }   

                    details = fetch_vehicle_details(car['vin'])
                    car_data["trim"] = details.get("trim", "Unknown") if details else "Unknown"
                    car_data["engine"] = details.get("engine", "Unknown") if details else "Unknown"
                    car_data["transmission"] = details.get("transmission", "Unknown") if details else "Unknown"
                    car_data["color"] = details.get("color", "Unknown") if details else "Unknown"

                    results.append(car_data)

            else:
                print(f"No vehicles found for make {make} and model {model}.")

        else:
            print(f"Error fetching inventory: {response.status_code}")

        return results

    except Exception as e:
        print(f"Error searching inventory: {e}")
        return results