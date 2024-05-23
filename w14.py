import time
from pymongo import MongoClient
from datetime import datetime, timezone

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = rchromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Initialize list to store extracted data
products_data = []

# Base URL to scrape
base_url = 'https://www.viperatech.com/product-category/bitcoin-mining-hardware/asics/page/'
total_pages =11  # Specify the total number of pages to scrape

for page_number in range(1, total_pages + 1):
    # Construct the URL for the current page
    url = f"{base_url}{page_number}/"

    # Load the webpage
    browser.get(url)
    time.sleep(5)  # Add a delay to allow the page to fully load

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all product elements
    product_elements = soup.select('ul.products.columns-3 li.product')

    # Iterate over the products and extract the required information
    for index, product in enumerate(product_elements, start=(page_number - 1) * len(product_elements) + 1):
        product_info = {}
        
        # Extract product URL
        product_url_tag = product.select_one('a.woocommerce-LoopProduct-link')
        product_info['product_url'] = product_url_tag['href'] if product_url_tag else 'no data'
        
        # Extract image URL
        img_tag = product_url_tag.find('img') if product_url_tag else None
        product_info['img_url'] = img_tag['src'] if img_tag else 'no data'
        
        # Extract product name
        product_name_tag = product.select_one('h2.woocommerce-loop-product__title')
        product_info['product_name'] = product_name_tag.get_text(strip=True) if product_name_tag else 'no data'
        
        # Extract product price
        product_price_tag = product.select_one('span.woocommerce-Price-amount')
        product_info['product_price'] = product_price_tag.get_text(strip=True) if product_price_tag else 'no data'
        
        # Append product information to the list with product number
        products_data.append({
            "product_number": index,
            "product_info": product_info
        })

    print(f"Page {page_number} completed out of {total_pages}")


# Close the browser
browser.quit()




url = os.getenv("MONGO_URL")
db_name =  "web_data"
collection_name = "vipera"

# Connect to MongoDB Atlas
client = MongoClient(url)

# Select database and collection
db = client[db_name]
collection = db[collection_name]

# Create a document with timestamp and the list of product data
document = {
    "timestamp": datetime.now(timezone.utc),
    "products": products_data
}

# Insert document into the collection
collection.insert_one(document)
print("Data inserted into collection successfully.")
