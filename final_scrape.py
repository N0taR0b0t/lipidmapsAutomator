import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ANSI escape codes for colors
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Set up output file
headers = ['LMSD Examples', 'LM_ID', 'Common Name', 'Systematic Name', 'Main Class', 'Sub Class', 'Mass', 'Formula']
with open('final_out.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)

# Configure Selenium
options = webdriver.ChromeOptions()
options.add_argument("--disable-headless")
browser = webdriver.Chrome(options=options)
base_url = "https://www.lipidmaps.org"

# Load and deduplicate LMSD Examples
unique_lmsd = []
seen = set()
with open('examples.csv', 'r', encoding='utf-8') as examples_file:
    examples_reader = csv.DictReader(examples_file)
    for row in examples_reader:
        lm_id = row['LMSD Examples']
        if lm_id not in seen:
            seen.add(lm_id)
            unique_lmsd.append(lm_id)

# Custom expected condition for table detection
def table_loaded(driver):
    css_element = driver.find_elements(By.CSS_SELECTOR, "#mainContent > div > div > div > div.w-full.overflow-x-auto.text-base")
    if css_element:
        return css_element[0]
    xpath_element = driver.find_elements(By.XPATH, "//*[@id='mainContent']/div/div/div/div[1]")
    if xpath_element:
        return xpath_element[0]
    return False

consecutive_failures = 0

for lm_id in unique_lmsd:
    target_url = f"{base_url}{lm_id}"
    print(f"Processing {lm_id}...")

    try:
        browser.get(target_url)
        # Wait up to 5 seconds for table
        element = WebDriverWait(browser, 5).until(table_loaded)
        consecutive_failures = 0  # Reset counter on success
        
        # Extract data from the table
        table = element.find_element(By.TAG_NAME, 'table')
        data_rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(:first-child)')

        for row in data_rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) < 7:
                continue

            try:
                row_lm_id = cols[0].find_element(By.TAG_NAME, 'a').text.strip()
            except:
                row_lm_id = 'N/A'

            data = [
                lm_id,  # Ensure LMSD Example ID is included
                row_lm_id,
                cols[1].text.strip(),
                cols[2].text.strip(),
                cols[3].text.strip(),
                cols[4].text.strip(),
                cols[5].text.strip(),
                cols[6].text.strip()
            ]

            with open('final_out.csv', 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(data)

    except Exception as e:
        print(f"{YELLOW}Warning: Could not load data for {lm_id} after 5 seconds. Skipping.{RESET}")
        consecutive_failures += 1
        
        if consecutive_failures >= 3:
            print(f"{RED}Error: 3 consecutive failures. Exiting.{RESET}")
            browser.quit()
            exit(1)
        continue

browser.quit()
print("Data extraction completed. Check final_out.csv.")