import requests
from bs4 import BeautifulSoup
from django.shortcuts import render


def get_content(product):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Language': 'en-US',
        'Referer': 'https://www.jumia.com.ng/',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
    })


    try:
        response = session.get(f'https://www.jumia.com.ng/catalog/?q={product}', timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return ""


def home(request):
    product_info_list = []

    if 'product' in request.GET:
        product = request.GET.get('product')
        print(product)
        html_content = get_content(product)

        if html_content:  # Check if content was fetched successfully
            soup = BeautifulSoup(html_content, 'html.parser')

            product_items = soup.find_all('article', class_='prd _fb col c-prd')
            if product_items:
                for item in product_items:
                    name_tag = item.find('h3', class_='name')
                    price_tag = item.find('div', class_='prc')
                    img_c_div = item.find('div', class_='img-c')
                    img_tag = img_c_div.find('img', class_='img') if img_c_div else None
                    stars_div = item.find('div', class_='stars _s')
                    rating_div = stars_div.find('div', class_='in') if stars_div else None

                    if name_tag and price_tag and img_tag and rating_div:
                        name = name_tag.text.strip()
                        price = price_tag.text.strip()
                        img_url = img_tag.get('data-src', '') if img_tag else ''

                        style_attribute = rating_div.get('style', '')
                        width_value = style_attribute.split(':')[1].replace('%', '').strip() if ':' in style_attribute else '0'
                        rating = f'{float(width_value) / 20:.1f}' if width_value.isdigit() else '0.0'

                        product_info = {
                            'name': name,
                            'price': price,
                            'image_url': img_url,
                            'rating': rating
                        }
                        product_info_list.append(product_info)
            else:
                print("No products found.")

    return render(request, 'core/home.html', {'product_info_list': product_info_list})
