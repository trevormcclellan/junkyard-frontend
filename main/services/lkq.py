import requests
from bs4 import BeautifulSoup

YARD_IDS = {
    "dayton": "1257",
    "cincinnati": "1253",
}

def fetch_page(page, query, location):
    yard = location.lower()
    if yard not in YARD_IDS:
        return None
    yard_id = YARD_IDS[yard]

    url = f"https://www.pyp.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx?page={page}&filter={query}&store={yard_id}"
    payload = {}
    headers = {
        'referer': f'https://www.pyp.com/inventory/{yard}-{yard_id}/?search={query}'
    }

    response = requests.get(url, headers=headers, params=payload)
    if response.status_code != 200:
        return None
    return response.text

def search_inventory(query, location):
    try:
        results = []
        page_num = 1

        while True:
            page = fetch_page(page_num, query, location)
            page_num += 1
            if not page:
                break
            soup = BeautifulSoup(page, 'html.parser')
            rows = soup.find_all('div', {'class': 'pypvi_resultRow'})

            if rows:
                for row in rows:
                    car_data = { "location": location }
                    # Extract the year and model from the row
                    ymm_tag = row.find('a', {'class': 'pypvi_ymm'})
                    if ymm_tag:
                        # Get all the text, join with spaces to remove HTML artifacts like <wbr>
                        ymm_text = ' '.join(ymm_tag.stripped_strings)  # E.g. '2014 MERCEDES-BENZ GL450'
                        parts = ymm_text.split(maxsplit=2)

                        if len(parts) == 3:
                            year, make, model = parts
                            car_data['year'] = int(year)
                            car_data['make'] = make.upper()
                            car_data['model'] = model.upper()

                    # Get all the details in the row with the class 'pypvi_detailItem'
                    details = row.find_all('div', {'class': 'pypvi_detailItem'})
                    for detail in details:
                        for b_tag in detail.find_all('b'):
                            key = b_tag.get_text(strip=True).rstrip(':')
                            
                            # Value is usually a direct sibling
                            value = ''
                            next_node = b_tag.next_sibling

                            # If value is plain text (string or NavigableString)
                            while next_node and (next_node.name is None or next_node.name == 'br'):
                                if isinstance(next_node, str):
                                    value += next_node.strip()
                                next_node = next_node.next_sibling

                            # Special case: "Available" uses a <time> tag
                            if key == "Available":
                                time_tag = b_tag.find_next('time')
                                if time_tag and time_tag.has_attr('datetime'):
                                    value = time_tag['datetime']
                                elif time_tag:
                                    value = time_tag.get_text(strip=True)

                            # Store in dictionary
                            if key == "Color":
                                car_data['color'] = value
                            elif key == "VIN":
                                car_data['vin'] = value
                            elif key == "Stock #":
                                car_data['stock_num'] = value
                            elif key == "Available":
                                car_data['date'] = value
                            elif key == "Section":
                                car_data['section'] = value
                            elif key == "Row":
                                car_data['row'] = value
                            elif key == "Space":
                                car_data['space'] = value

                    # Extract the main image URL from the row
                    main_image = row.find('a', {'class': 'pypvi_image'})

                    # Extract all image URLs from the row
                    image_urls = [ main_image['href'] ] if main_image else []
                    images_div = row.find('div', {'class': 'pypvi_images'})
                    if images_div:
                        image_urls += [a['href'] for a in images_div.find_all('a', href=True)]
                    if image_urls:
                        car_data['image_urls'] = image_urls

                    # Add the car data to results
                    if car_data:
                        results.append(car_data)

            end = soup.find('div', {'class': 'pypvi_end'})
            if end:
                break

        return results
    except Exception as e: 
        print(f"Error fetching LKQ inventory: {e}")
        return []