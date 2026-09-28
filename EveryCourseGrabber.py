import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#######################################################################################

# Reading login credentials + term link from credentials.txt (see README for format)
# Create a file named credentials.txt in this same folder:
#   line 1 = your Drexel email
#   line 2 = your Drexel password
#   line 3 = the term master schedule link you're searching through

script_directory = os.path.dirname(os.path.abspath(__file__))
credentials_file = os.path.join(script_directory, "credentials.txt")

if not os.path.exists(credentials_file):
    print(f"Error: {credentials_file} not found. Create it with your email on line 1, password on line 2, and the term link on line 3.")
    exit(1)

with open(credentials_file, "r") as file:
    lines = [line.strip() for line in file.readlines()]

if len(lines) < 3 or not lines[0] or not lines[1] or not lines[2]:
    print(f"Error: {credentials_file} must have your email on line 1, password on line 2, and the term link on line 3.")
    exit(1)

username, password, term_link = lines[0], lines[1], lines[2]
#######################################################################################

# Opening correct file

output_course_details = os.path.join(script_directory, "every_class_in_term.txt")

#######################################################################################

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=chrome_options)

# The term master schedule link now comes from line 3 of credentials.txt
driver.get(term_link)
wait = WebDriverWait(driver, 15)


sign_in_button = wait.until(EC.presence_of_element_located((By.NAME, "_eventId_proceed")))
sign_in_button.click()

user_id_field = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
user_id_field.send_keys(username)
user_id_field.send_keys(Keys.RETURN)

wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
password_field = driver.find_element(By.NAME, "passwd")
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)

# Wait for manual 2FA approval
print("Waiting for manual sign-in (approve request or 2FA)...")
while "collegesSubjects" not in driver.current_url:
    time.sleep(0.5)

print("Sign-in successful! Gathering course list links.")

#######################################################################################

#  Gathering major links logic

nav_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a")))
collCode_links = [link.get_attribute("href") for link in nav_links if "/webtms_du/collegesSubjects/" in link.get_attribute("href")]

collected_links = []
for collCode_link in collCode_links:
    driver.get(collCode_link)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    course_list_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/webtms_du/courseList/']")
    for course_link in course_list_links:
        href = course_link.get_attribute("href")
        if href:
            collected_links.append(f"{collCode_link}|{href}")
time.sleep(0.5)

#######################################################################################

# Gathering every class link logic

print("Processing course list links to extract course details.")
collected_course_details = set()
last_collCode = None

for line in collected_links:
    parts = line.split("|", 1)
    if len(parts) == 2:
        collCode, course_list_link = parts
    else:
        print(f"Skipping malformed line: {line}")
        continue

    if last_collCode != collCode:
        driver.get(collCode)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        last_collCode = collCode

    driver.get(course_list_link)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    course_detail_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/webtms_du/courseDetails/']")

    for detail_link in course_detail_links:
        href = detail_link.get_attribute("href")
        if href:
            collected_course_details.add(f"{href}|{collCode}|{course_list_link}")

#######################################################################################

# Save courses to file
os.makedirs(os.path.dirname(output_course_details), exist_ok=True)
with open(output_course_details, "w") as file:
    for link in collected_course_details:
        file.write(link + "\n")

print(f"Saved course details links to {output_course_details}")
driver.quit()
