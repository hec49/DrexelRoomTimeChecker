import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Hardcoded login credentials
#
#
#
# SET THESE TO YOUR DREXEL EMAIL AND PASSWORD FOR LOGGING IN
username = ""
password = ""
#
#
#######################################################################################

# Opening correct file

script_directory = os.path.dirname(os.path.abspath(__file__))
output_course_details = os.path.join(script_directory, "every_class_in_term.txt")

#######################################################################################

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=chrome_options)

# CHANGE THIS LINK TO THE QUARTER YOURE LOOKING THROUGH  VVVVVVVVVVVVVVVVV
# PLEASE EDIT THE TEXT IN THE QUOTES
driver.get("")
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