from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import time
from datetime import datetime
from pymongo import MongoClient
import os

# Function to initialize the browser instance
def initialize_browser():
    # Set up Chrome options and service
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    chrome_driver_path = r"chromedriver"
    chrome_service = ChromeService(executable_path=chrome_driver_path)

    # Create a new instance of the Chrome webdriver
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return browser

# Function to get the total number of pages
def get_total_pages(url, browser):
    browser.get(url)
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    result_count = soup.find('p', class_='woocommerce-result-count').text
    total_products = int(result_count.split('of')[-1].split()[0].replace(',', ''))
    items_per_page = 12  # Assuming each page displays 12 products
    total_pages = (total_products + items_per_page - 1) // items_per_page
    return total_pages

# Function to scrape data from a single page
def scrape_page(url, browser):
    browser.get(url)
    time.sleep(5)  # Add a delay of 10 seconds
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    products = soup.select('ul.products li')
    page_data = {}
    for i, product in enumerate(products, start=1):
        title = product.select_one('h2.woocommerce-loop-product__title').text
        image = product.select_one('div.astra-shop-thumbnail-wrap img')['src']
        price_span = product.select_one('span.price')
        
        # Extract price range
        price_range = price_span.select('.woocommerce-Price-amount')
        if len(price_range) == 2:
            deleted_price_amount = price_range[0].text.strip()
            current_price_amount = price_range[1].text.strip()
        else:
            deleted_price_amount = None  # Set deleted price to None if not found
            current_price_amount = price_span.text.strip()  # Extract current price from span
        
        page_data[f'product {i}'] = {
            'title': title,
            'image': image,
            'deleted_price': deleted_price_amount,
            'current_price': current_price_amount
        }
    return page_data

# MongoDB Atlas connection parameters
mongo_url = os.getenv('MONGO_URL')
db_name = "web_data"
collection_name = "cooldragon_website"

# Connect to MongoDB Atlas
client = MongoClient(mongo_url)
db = client[db_name]
collection = db[collection_name]

# URL of the webpage to scrape
base_url = 'https://cooldragon.com.cn/product-category/miners/'
browser = initialize_browser()
num_pages = get_total_pages(base_url, browser)

# List to store all products data
all_products_data = {}

# Variable to keep track of the total product count
product_count = 0

# Iterate over each page and scrape data
for page_number in range(1, num_pages + 1):
    url = f'{base_url}page/{page_number}?orderby=price'
    page_data = scrape_page(url, browser)
    
    # Update product count and merge page data into all products data
    for key, value in page_data.items():
        product_count += 1
        all_products_data[f'product {product_count}'] = value
    
    print(f'Page {page_number} completed out of {num_pages}')

# Add timestamp to the aggregated data
all_products_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Insert the aggregated data into MongoDB
collection.insert_one(all_products_data)

print(f'Successfully saved data from {num_pages} pages to MongoDB Atlas')

# Quit the browser after scraping
browser.quit()
