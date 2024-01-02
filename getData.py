import os
import csv
from datetime import datetime
import time
import configparser
import zipfile
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set the path to the Chrome executable
# Define the directory path and URLs for Chrome and Chromedriver
chrome_directory = 'c:/tmp/chrome'
chrome_exe_path = 'c:/tmp/chrome/chrome-win64/chrome.exe'  # Modify this path as needed
chrome_url = 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.92/win64/chrome-win64.zip'

# Check if the Chrome directory exists, and if not, create it
if not os.path.exists(chrome_directory):
    os.makedirs(chrome_directory)

# Check if Chrome.exe and Chromedriver.exe exist in the directory
if not os.path.exists(os.path.join(chrome_exe_path)):
    # Download and extract Chrome
    chrome_response = requests.get(chrome_url)
    with zipfile.ZipFile(BytesIO(chrome_response.content), 'r') as zip_ref:
        zip_ref.extractall(chrome_directory)

# Set the URL of the website
url = 'https://www.mrcooper.com/servicing/overview'

current_directory = os.getcwd()
csv_file_path = os.path.join(current_directory, 'equity.csv')

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_exe_path  # Specify Chrome executable path
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (optional)

config_path = 'config.ini'

if not os.path.exists(config_path):
    # If config.ini doesn't exist, prompt the user for credentials
    username_input = input("Enter your username: ")
    password_input = input("Enter your password: ")

    # Create config.ini with user-provided credentials
    config = configparser.ConfigParser()
    config['Credentials'] = {'username': username_input,
                             'password': password_input}
    
    with open(config_path, 'w') as configfile:
        config.write(configfile)

# Load credentials from config file
config = configparser.ConfigParser()
config.read(config_path)  # Update with your config file path

username_value = config.get('Credentials', 'username')
password_value = config.get('Credentials', 'password')

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the website
    driver.get(url)

    # Set your login credentials
    username = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "signInName")))
    password = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "password")))

    # Enter the username and password
    username.send_keys(username_value)
    password.send_keys(password_value)

    # Submit the login form
    password.send_keys(Keys.RETURN)

    # Wait for a few seconds for the page to load after login (you may need to adjust the timing)
    time.sleep(10)

    try:
        # Find the equity with the data you want to scrape (by class name in this case)
        equity_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'estimate-section__equity__content')))
        equity = equity_element.text
    except Exception as e:
        print(f"Error retrieving equity: {e}")
        equity = ''  # Set equity to blank in case of an error
    
    try:
        home_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'estimate-section__home__content')))
        home = home_element.text
    except Exception as e:
        print(f"Error retrieving home value: {e}")
        home = ''  # Set home value to blank in case of an error
    
    try:
        principal_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'principal-balance-value')))
        principal = principal_element.text
    except Exception as e:
        print(f"Error retrieving principal remaining: {e}")
        principal = ''  # Set principal remaining to blank in case of an error

    # Create or update the CSV file
    data = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), equity, home, principal]

    # Check if the CSV file already exists
    if os.path.exists(csv_file_path):
        # Read the existing data
        with open(csv_file_path, 'r', newline='') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
        
        # Shift existing rows down and insert the new data at row 2
        rows.insert(1, data)
        
        # Update the existing CSV file with the shifted data
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)
    else:
        # Create a new CSV file and write the data
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write column headers
            csv_writer.writerow(['Date', 'Equity', 'Home_Value', 'Principal_Remaining'])
            # Write the data to the CSV file
            csv_writer.writerow(data)

    print(f'Data saved to {csv_file_path}')

finally:
    # Close the browser
    driver.quit()
