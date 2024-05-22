from pymongo import MongoClient
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import json
import time
import os

# Function to scrape product data from a single page
def scrape_product_data(url, product_number):
    # Set up Chrome options and service
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    chrome_driver_path = r"chromedriver"
    chrome_service = ChromeService(executable_path=chrome_driver_path)

    # Create a new instance of the Chrome webdriver
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # Load the webpage
    browser.get(url)

    # Get the HTML content of the page
    html_content = browser.page_source

    # Close the browser
    browser.quit()
    time.sleep(5)

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    product_grid = soup.find('ul', {'id': 'product-grid'})
    products = product_grid.find_all('li', {'class': 'grid__item'})

    product_list = []

    for idx, product in enumerate(products, start=product_number):
        product_info = {}
        
        # Extracting product URL
        product_url_tag = product.find('a', {'class': 'full-unstyled-link'})
        product_url = product_url_tag['href'] if product_url_tag else "no data"
        product_info['product_url'] = f"https://nhash.net{product_url}" if product_url != "no data" else "no data"
        
        # Extracting image URL
        img_tag = product.find('img')
        img_url = img_tag['src'] if img_tag else "no data"
        product_info['img_url'] = img_url
        
        # Extracting product name
        product_name_tag = product.find('h3', {'class': 'card__heading'})
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "no data"
        product_info['product_name'] = product_name
        
        # Extracting product price
        price_tag = product.find('span', {'class': 'price-item--sale'})
        if not price_tag:
            price_tag = product.find('span', {'class': 'price-item--regular'})
        product_price = price_tag.get_text(strip=True) if price_tag else "no data"
        product_info['product_price'] = product_price
        
        # Append to the product list
        product_list.append({
            "product_number": idx,
            "product_info": product_info
        })

    return product_list

# URL base to scrape
base_url = 'https://nhash.net/collections/all?page='
product_number = 1
all_products = []
total_pages = 3  # Specify the total number of pages to scrape

for page_number in range(1, total_pages + 1):
    # Construct the URL for the current page
    url = base_url + str(page_number)

    # Scrape the product data
    products_data = scrape_product_data(url, product_number)
    
    # Update product_number for the next page
    product_number += len(products_data)
    
    # Extend the all_products list with the current page's data
    all_products.extend(products_data)
    
    print(f"Page {page_number} completed out of {total_pages}")


url =  os.getenv("MONGO_URL")
db_name =  "web_data"
collection_name = "nhash"

# Connect to MongoDB Atlas
client = MongoClient(url)

# Select database and collection
db = client[db_name]
collection = db[collection_name]

# Create a document with timestamp and the list of product data
document = {
    "timestamp": datetime.now(timezone.utc),
    "products": all_products
}

# Insert document into the collection
collection.insert_one(document)
print("Data inserted into collection successfully.")
