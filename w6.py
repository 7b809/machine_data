from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import json
import time
from pymongo import MongoClient
from datetime import datetime, timezone

# Function to scrape product data
def scrape_product_data(browser, url, product_number):
    # Load the webpage
    browser.get(url)

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    products = []

    ul = soup.find('ul', {'class': 'S4WbK_ uQ5Uah c2Zj9x H1ux6p', 'data-hook': 'product-list-wrapper'})
    if ul:
        li_items = ul.find_all('li', {'data-hook': 'product-list-grid-item'})
        for li in li_items:
            product_info = {}
            
            # Get product URL
            product_url_tag = li.find('a', {'data-hook': 'product-item-container'})
            product_info['product_url'] = product_url_tag['href'] if product_url_tag else "no data"
            
            # Get product image URL
            img_tag = li.find('img')
            product_info['img_url'] = img_tag['src'] if img_tag else "no data"
            
            # Get product name
            product_name_tag = li.find('h3', {'data-hook': 'product-item-name'})
            product_info['product_name'] = product_name_tag.text.strip() if product_name_tag else "no data"
            
            # Get product price
            product_price_tag = li.find('span', {'data-hook': 'product-item-price-to-pay'})
            product_info['product_price'] = product_price_tag.text.strip() if product_price_tag else "no data"
            
            # Add product data to the list
            products.append({
                'product_number': product_number,
                'product_info': product_info
            })
            product_number += 1
    
    return products, product_number

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"chromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a single instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# URL to scrape
base_url = 'https://www.maximiners.com/all-products?page='
product_number = 1
all_products = []
total_pages = 4

for page_number in range(1, total_pages + 1):
    # Construct the URL for the current page
    url = base_url + str(page_number)

    # Scrape the product data
    products_data, product_number = scrape_product_data(browser, url, product_number)
    
    all_products.extend(products_data)
    
    print(f"Page {page_number} completed out of {total_pages}")

# Close the browser after scraping all pages
browser.quit()

url =  os.getenv('MONGO_URL')
db_name =  "web_data"
collection_name = "xonmining"

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
