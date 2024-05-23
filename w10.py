from pymongo import MongoClient
from datetime import datetime, timezone
from selenium import webdriver

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import json

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"chromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Load the webpage
link = "https://asicmarketplace.com/shop/?orderby=menu_order"
browser.get(link)

# Get the HTML content of the page
html_content = browser.page_source

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Close the browser
browser.quit()

# Initialize list to store product data
products_data = []

# Find all product items
product_items = soup.find_all('li', class_='product')

# Iterate through product items
for index, item in enumerate(product_items, start=1):
    product_info = {}
    product_info['product_number'] = index

    # Extract product URL
    product_link = item.find('a', class_='woocommerce-LoopProduct-link')
    product_info['product_info'] = {}
    product_info['product_info']['product_url'] = product_link['href'] if product_link else 'no data'

    # Extract image URL
    product_image = item.find('img')
    product_info['product_info']['img_url'] = product_image['src'] if product_image else 'no data'

    # Extract product name
    product_name = item.find('h2', class_='woocommerce-loop-product__title')
    product_info['product_info']['product_name'] = product_name.get_text() if product_name else 'no data'

    # Extract product price
    product_price = item.find('span', class_='price')
    product_info['product_info']['product_price'] = product_price.get_text().strip() if product_price else 'no data'

    # Append product data to the list
    products_data.append(product_info)





url =  os.getenc("MONGO_URL")
db_name =  "web_data"
collection_name = "asicMarket"

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
