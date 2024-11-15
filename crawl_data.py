import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for product list pages
base_url = 'https://hunonic.com/thiet-bi-dien-thong-minh/page/{}/'

# List to store product data
data = []

# Loop through all 10 pages
for page in range(1, 11):
    # Format the page URL
    url = base_url.format(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all product links
    products = soup.find_all('div', class_='product-small box')  # Adjust based on HTML structure
    for product in products:
        # Get the product link
        product_link = product.find('a')['href']

        # Send a request to the individual product page
        product_response = requests.get(product_link)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Extract product information from the individual page
        name = product_soup.find('h1').text.strip()  # Adjust based on actual HTML
        # description = product_soup.find('div', class_='tab-panels').text.strip()  # Adjust as needed
        price = product_soup.find('span', class_='woocommerce-Price-amount amount')

        # Extract price text, handle if price is not found
        price = price.text.strip() if price else 'N/A'
        
        # Extract product information and features, handle if not found
        # product_info = product_info.text.strip() if product_info else 'N/A'
        # features = features.text.strip() if features else 'N/A'
        product_info = ''
        features = ''
        # Append the data
        data.append({
            'Tên sản phẩm': name,
            'Thông tin sản phẩm': product_info,
            'Tính năng': features,
            'Giá': price,

            'Link sản phẩm': product_link
        })

# Create a DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('data_hunonic.xlsx', index=False)

print("Đã hoàn thành cào dữ liệu.")
