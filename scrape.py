import shutil
import time
import glob
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

with open('processed_chunks.txt', 'w', newline='', encoding='utf-8') as file:
    file.write('')

# Set path to manually installed ChromeDriver
CHROME_DRIVER_PATH = '/opt/homebrew/bin/chromedriver'
BASE_URL = "https://www.lipidmaps.org/resources/tools/bulk-structure-search/create?database=LMSD"

# Configure driver options
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Initialize WebDriver
service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 60)  # Increased timeout to 60 seconds

# Constants
MAX_LINES_PER_SUBMISSION = 499  # Website limit

def process_chunk(chunk):
    """Process a single chunk of m/z values."""
    try:
        # Wait for the page to be fully loaded
        wait.until(EC.presence_of_element_located((By.ID, 'mass')))
        wait.until(EC.presence_of_element_located((By.ID, 'submitBtn')))

        # Handle mass input with proper newline preservation
        mass_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mass"]')))

        # Clear existing content using JavaScript
        driver.execute_script("arguments[0].value = '';", mass_input)

        # Insert values with proper newline handling
        driver.execute_script(f"""
            arguments[0].value = `{chunk}`;
            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
        """, mass_input)

        # Verify the input was successful
        current_value = driver.execute_script("return arguments[0].value", mass_input)
        current_lines = [line.strip() for line in current_value.split('\n') if line.strip()]

        print(f"Processing chunk with {len(current_lines)} entries")

        if len(current_lines) != len(chunk.split('\n')):
            print("Warning: Entry count mismatch in chunk")
        else:
            print("Chunk input verified successfully")

        # Set tolerance using the dropdown
        tol_select = Select(wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tol"]'))))
        tol_select.select_by_visible_text('+/- 0.0005 m/z')

        # Define locators for each checkbox using CSS selectors
        checkbox_locators = [
            (By.ID, 'negative_ion'),
            (By.CSS_SELECTOR, 'input[type="checkbox"][value="FA"]'),
            (By.CSS_SELECTOR, 'input[type="checkbox"][value="GL"]'),
            (By.CSS_SELECTOR, 'input[type="checkbox"][value="GP"]'),
            (By.CSS_SELECTOR, 'input[type="checkbox"][value="SP"]'),
            (By.CSS_SELECTOR, 'input[type="checkbox"][value="ST"]')
        ]

        # Iterate through the list and click each checkbox if not already selected
        for by, locator in checkbox_locators:
            checkbox = wait.until(EC.element_to_be_clickable((by, locator)))
            if not checkbox.is_selected():
                checkbox.click()
                print(f"Checkbox {locator} selected")
            else:
                print(f"Checkbox {locator} already selected")

        # Submit form using the button locator
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
        submit_button.click()
        print("Form submitted successfully")

        # Wait for next page and click results link
        results_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="job-status-text"]/div/a')))
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="job-status-text"]/div/a'))).click()

        time.sleep(4) #Wait to ensure download is ready

        tsv_files = glob.glob(os.path.expanduser('~/Downloads/*.tsv'))

        # Sort files by modification time and get the most recent one
        most_recent_tsv = max(tsv_files, key=os.path.getmtime)

        # Move the most recent .tsv file to the destination directory
        destination = '/Users/matias/Library/Mobile Documents/com~apple~CloudDocs/Work/LipidMaps/downloads'
        shutil.move(most_recent_tsv, destination)

        # Wait for results to process
        time.sleep(3)  # Increased wait time

        # Navigate back to the base URL for the next chunk
        print("Navigating back to search page...")
        driver.get(BASE_URL)
        time.sleep(2)  # Give the page time to load

    except Exception as e:
        print(f"Error processing chunk: {str(e)}")
        driver.get(BASE_URL)
        raise

# Load processed chunks (if any)
processed_chunks = set()
try:
    with open('processed_chunks.txt', 'r') as f:
        processed_chunks = set(int(x.strip()) for x in f.readlines())
except FileNotFoundError:
    pass

try:
    # Navigate to the target page
    driver.get(BASE_URL)

    # Load and sanitize m/z values
    with open('mz.txt', 'r') as f:
        mz_values = [line.strip() for line in f if line.strip()]

    # Split into chunks
    chunks = ['\n'.join(mz_values[i:i + MAX_LINES_PER_SUBMISSION])
              for i in range(0, len(mz_values), MAX_LINES_PER_SUBMISSION)]

    print(f"Total entries: {len(mz_values)}")
    print(f"Number of chunks: {len(chunks)}")

    # Process each chunk
    for i, chunk in enumerate(chunks, 1):
        if i in processed_chunks:
            print(f"Skipping already processed chunk {i}")
            continue
        try:
            print(f"\nProcessing chunk {i} of {len(chunks)}")
            process_chunk(chunk)
            # Save progress
            with open('processed_chunks.txt', 'a') as f:
                f.write(f"{i}\n")
        except Exception as e:
            print(f"Failed to process chunk {i}: {str(e)}")
            continue

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    driver.quit()

#Let's run extract_urls.py here