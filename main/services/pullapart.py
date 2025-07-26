import requests
import json

def get_makes():
    url = "https://inventoryservice.pullapart.com/Make/"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching makes: {response.status_code}")
        return []
    
def get_models(make, location):
    url = f"https://inventoryservice.pullapart.com/Model/OnYard?locations={location}&makeID={make}"

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

def fetch_vehicle_image(vehicle):
    """Fetch vehicle image """
    try:
        locID = vehicle["locID"]
        ticketID = vehicle["ticketID"]
        lineID = vehicle["lineID"]
        url = f"https://imageservice.pullapart.com/img/retrieveimage/?locID={locID}&ticketID={ticketID}&lineID={lineID}&programID=35&imageIndex=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["webPath"]
        else:
            return None
    except Exception as e:
        return None

def fetch_vehicle_details(vehicle):
    """Fetch extended vehicle details."""
    try:
        locID = vehicle["locID"]
        ticketID = vehicle["ticketID"]
        lineID = vehicle["lineID"]
        url = f"https://inventoryservice.pullapart.com/VehicleExtendedInfo/{locID}/{ticketID}/{lineID}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        return None

def search_inventory(make, model, location):
    try:
        results = []
        url = "https://inventoryservice.pullapart.com/Vehicle/Search"

        # Payload for the POST request
        payload = json.dumps({
            "Locations": [int(location)],
            "MakeID": make,
            "Models": [model] if model else [],
            "Years": []
        })

        headers = {
            'content-type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        cars = []
        if response.status_code == 200:
            data = response.json()
            for resp_location in data:
                if 'exact' in resp_location:
                    cars.extend(resp_location['exact'])

            for car in cars:
                car_data = {
                    "location": car.get("locName"),
                    "location_id": car.get("locID"),
                    "year": car.get("modelYear"),
                    "make": car.get("makeName"),
                    "model": car.get("modelName"),
                    "vin": car.get("vin"),
                    "stock_num": car.get("vinID"),
                    "row": car.get("row"),
                    "date": car.get("dateYardOn"),
                    "image": fetch_vehicle_image(car),
                }

                details = fetch_vehicle_details(car)
                if details:
                    car_data["trim"] = details["trim"] if details["trim"] else None
                    car_data["engine"] = str(details["engineSize"]) + "L " + details["engineBlock"] + str(details["engineCylinders"]) if details["engineBlock"] else None
                    car_data["transmission"] = str(details["transSpeeds"]) + " speed " + details["transType"] if details["transType"] else None
                    car_data["color"] = details["color"] if details["color"] else None
                    car_data["style"] = details["style"] if details["style"] else None

                results.append(car_data)

        else:
            print(f"Error searching inventory: {response.status_code}")

        return results

    except Exception as e:
        print(f"Error searching inventory: {e}")
        return results