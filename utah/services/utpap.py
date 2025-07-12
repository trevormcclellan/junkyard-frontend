import requests
from flask import jsonify
from bs4 import BeautifulSoup

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