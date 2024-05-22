import time
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

# Base URL for product pages
base_url = "https://xonmining.com/products/all-miners/page/"


total_pages = 11

product_number = 1
# Initialize an empty list to store all product data
all_products_data = []

# Loop through each page
for page_number in range(1, total_pages+1):  # Assuming 11 pages
    # Construct the URL for the current page
    url = base_url + str(page_number) + "/"

    # Load the webpage
    browser.get(url)
    time.sleep(5)  # Let the page load, adjust as needed

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <li> elements with class "product"
    product_list = soup.find_all("li", class_="ast-grid-common-col")

    # Initialize product number for sequential numbering
    

    # Loop through each <li> element
    for product in product_list:
        # Extract relevant information
        img_url = product.find("img")["src"] if product.find("img") else "no data"
        product_url = product.find("a", class_="woocommerce-LoopProduct-link")["href"] if product.find("a", class_="woocommerce-LoopProduct-link") else "no data"
        product_name = product.find("h2", class_="woocommerce-loop-product__title").text.strip() if product.find("h2", class_="woocommerce-loop-product__title") else "no data"
        product_price = product.find("span", class_="price").text.strip() if product.find("span", class_="price") else "no data"

        # Append the extracted data to the list
        all_products_data.append({
            
            "product_number": product_number,
            "product_info": {
                "img_url": img_url,
                "product_url": product_url,
                "product_name": product_name,
                "product_price": product_price
            }
        })

        # Increment product number for sequential numbering
        product_number += 1
    print(f"{page_number} completed out of {total_pages}")


# Close the browser
browser.quit()


url =os.getenv('MONGO_URL')

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
    "products": all_products_data
}

# Insert document into the collection
collection.insert_one(document)
print("Data inserted into collection sucessfully..")
