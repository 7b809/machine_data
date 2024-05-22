from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"chromedriver"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

  
# Function to extract product information from HTML
def extract_product_info(html):
    product_info = {}

    img_tag = html.find("img", class_="attachment-medium_large")
    product_info["img_url"] = img_tag["src"] if img_tag else "No Data"

    product_link = html.find("a", class_="product-image-link")
    product_info["product_url"] = product_link["href"] if product_link else "No Data"

    product_name = html.find("h3", class_="wd-entities-title")
    product_info["product_name"] = product_name.text.strip() if product_name else "No Data"

    price_span = html.find("span", class_="price")
    product_info["product_price"] = price_span.text.strip() if price_span else "No Data"

    return product_info

# Load HTML content
base_url = "https://apextomining.com/shop/page/1/?orderby=price-desc&per_page=24&shop_view=grid&per_row=4"

# Base URL for product pages


total_pages = 10

# Initialize an empty list to store all product data
all_products_data = []


for page_number in range(1, total_pages+1):  # Assuming 11 pages
    url = base_url + str(page_number) + "/"


    # Load the webpage
    browser.get(url)
    time.sleep(10)

        # Get the HTML content of the page
    html_content = browser.page_source
    with open("index.html",'w',encoding='utf-8') as f:
        f.write(html_content)

        # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all product divs
    product_divs = soup.find_all("div", class_="wd-product")

    # Extract product information and save in a list
    product_list = []

    for i, product_div in enumerate(product_divs, start=1):
        product_info = extract_product_info(product_div)
        product_list.append({"product_number": i, "product_info": product_info})
    
    all_products_data.append(product_list)
    page_number += 1

    print(f"{page_number} completed out of {total_pages}")





# Close the browser
browser.quit()


url =  os.getenv('MONGO_URL')
db_name =  "web_data"
collection_name = "apexto"

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
