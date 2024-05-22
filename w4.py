import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
from pymongo import MongoClient
from datetime import datetime, timezone
import os

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"chromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Define the base URL
base_url = "https://bt-miners.com/collections/crypto-miner-sales/page/"

# Define the number of pages to scrape
total_pages = 11

# Initialize product number
product_number = 1

# List to store all product data
all_products_data = []

# Loop through each page
for page_number in range(1, total_pages + 1):
    # Construct the URL for the current page
    url = base_url + str(page_number) + "/"
    
    # Load the webpage
    browser.get(url)
    time.sleep(5)

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all product blocks
    product_blocks = soup.find_all("div", class_="product-block grid")

    # Define the homepage URL to use as a placeholder
    placeholder_img_url = "No Img url"  # Placeholder URL

    # Iterate through each product block on the current page
    for product_block in product_blocks:
        # Extract image URL
        img_src = product_block.find("img")["src"]
        img_url = img_src if "data:image/svg+xml" not in img_src else placeholder_img_url

        # Extract product URL
        product_url = product_block.find("a", class_="product-image")["href"]

        # Extract product name
        product_name = product_block.find("h3", class_="name").text.strip()

        # Extract product price
        product_price = product_block.find("span", class_="price").text.strip()

        # Create a dictionary for the product info
        product_info = {
            "img_url": img_url,
            "product_url": product_url,
            "product_name": product_name,
            "product_price": product_price
        }

        # Append product info to the list
        all_products_data.append(product_info)
    print(f"{page_number} completed out of {total_pages}")

# Close the browser
browser.quit()


url = mongo_url = os.getenv('MONGO_URL')
db_name =  "web_data"
collection_name = "akMiners"

# Connect to MongoDB Atlas

client = MongoClient(url)

# Select database and collection
db = client[db_name]
collection = db[collection_name]

# Create a document with timestamp and the list of product data
document = {
    "timestamp": datetime.now(timezone.utc),
    "products": all_products_data
}

# Insert document into the collection
collection.insert_one(document)
print("Data inserted into collection sucessfully..")
