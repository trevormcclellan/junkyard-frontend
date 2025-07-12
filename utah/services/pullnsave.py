import requests, re
from bs4 import BeautifulSoup

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
    
def search_pullnsave_inventory(make, model, location):
    try:
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
        print(e)
        return []