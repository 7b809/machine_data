from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
from datetime import datetime, timezone
from selenium import webdriver

import os



# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"chromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Initialize list to store extracted data
products_data = []

# URL base to scrape
base_url = 'https://coinminingcentral.com/collections/all-miners?page='
total_pages = 14 # Specify the total number of pages to scrape

for page_number in range(1, total_pages + 1):
    # Construct the URL for the current page
    url = f"{base_url}{page_number}"

    # Load the webpage
    browser.get(url)
    time.sleep(5)  # Add a delay to allow the page to fully load

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all product items
    product_divs = soup.find_all('div', class_='grid-view-item')

    # Iterate over each product item
    for index, product in enumerate(product_divs, start=(page_number - 1) * len(product_divs) + 1):
        product_info = {}

        # Product URL
        product_url = product.find('a', class_='grid-view-item__link')
        product_info["product_url"] = "https://coinminingcentral.com" + product_url['href'] if product_url else "no data"

        # Image URL
        img_tag = product.find('img', class_='grid-view-item__image')
        product_info["img_url"] = "https:" + img_tag['src'] if img_tag else "no data"

        # Product Name
        product_name_tag = product.find('a', class_='grid-view-item__title')
        product_info["product_name"] = product_name_tag.text.strip() if product_name_tag else "no data"

        # Product Price
        price_regular = product.find('s', class_='product-price__price regular')
        price_sale = product.find('span', class_='product-price__sale')

        if price_sale:
            product_info["product_price"] = price_sale.text.strip()
        elif price_regular:
            product_info["product_price"] = price_regular.text.strip()
        else:
            product_info["product_price"] = "no data"

        # Append to products_data list
        products_data.append({"product_number": index, "product_info": product_info})

    print(f"Page {page_number} completed out of {total_pages}")

# Quit the browser
browser.quit()




url =  os.getenv("MONGO_URL")
db_name =  "web_data"
collection_name = "coinMining"

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
