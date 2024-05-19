from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse
from pymongo import MongoClient

def extract_store_name(url):
    domain = urlparse(url).netloc
    store_name = domain.split('.')[1] if 'www' in domain else domain.split('.')[0]
    return store_name.capitalize()

def extract_table_data(link, browser):
    # Load the webpage
    browser.get(link)

    # Get the HTML content of the page
    html_content = browser.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'id': 'datatable_opportunities'})

    rows = []
    for tr in table.find('tbody').find_all('tr'):
        cells = tr.find_all('td')
        row = {}
        for i, cell in enumerate(cells):
            if cell.find('a'):
                link = cell.find('a')['href']
                store_name = extract_store_name(link)
                row['Store'] = store_name
                row['URL'] = link
            else:
                header_text = table.find('thead').find_all('th')[i].text.strip()
                row[header_text] = cell.text.strip()
        rows.append(row)
    
    cleaned_rows = []
    for row in rows:
        cleaned_row = {
            "Store": row.get("Store", "Shop"),
            "URL": row.get("URL", "")
        }
        cleaned_rows.append(cleaned_row)
    
    return cleaned_rows

# Load the JSON file containing the URLs
with open('machine_data.json', 'r') as f:
    miner_data = json.load(f)
    miner_data = miner_data[0:2]

# Set up Chrome options and service
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
chrome_driver_path = r"C:\Users\HP PC\Downloads\temprory\btc\btc_code\chromedriver-win64\chromedriver.exe"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Connect to MongoDB (replace "mongodb://username:password@host:port/" with your MongoDB URL)
mongo_url = os.environ.get('MONGODB_URI')
client = MongoClient(mongo_url)

# Access or create a MongoDB database named 'web_data'
db = client['web_data']

# Access or create a MongoDB collection named 'all_websites'
collection = db['all_websites']

# Iterate through each URL and extract the data
for index, miner in enumerate(miner_data, start=1):
    link = miner['link']
    table_data = extract_table_data(link, browser)
    
    for entry in table_data:
        url = entry['URL']
        # Check if the URL already exists in the collection
        if not collection.find_one({"URL": url}):
            # Insert the entry into the collection if it's not already present
            collection.insert_one(entry)
    
    print(f"URL {index} completed: {link}")

print("Data has been saved to MongoDB collection 'all_websites' in database 'web_data'")
