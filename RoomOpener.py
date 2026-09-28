import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#######################################################################################

# Reading login credentials from credentials.txt (see README for format)
# Create a file named credentials.txt in this same folder:
#   line 1 = your Drexel email
#   line 2 = your Drexel password
#   line 3 = the term master schedule link (used by EveryCourseGrabber.py)

script_directory = os.path.dirname(os.path.abspath(__file__))
credentials_file = os.path.join(script_directory, "credentials.txt")

if not os.path.exists(credentials_file):
    print(f"Error: {credentials_file} not found. Create it with your email on line 1, password on line 2, and the term link on line 3.")
    exit(1)

with open(credentials_file, "r") as file:
    cred_lines = [line.strip() for line in file.readlines()]

if len(cred_lines) < 3 or not cred_lines[0] or not cred_lines[1] or not cred_lines[2]:
    print(f"Error: {credentials_file} must have your email on line 1, password on line 2, and the term link on line 3.")
    exit(1)

username, password = cred_lines[0], cred_lines[1]
#######################################################################################

# Opening correct file

input_file = os.path.join(script_directory, "room_finder.txt")

if not os.path.exists(input_file):
    print(f"Error: {input_file} does not exist.")
    exit(1)

with open(input_file, "r") as file:
    course_detail_data = [line.strip().split("|") for line in file.readlines()]

total_links = len(course_detail_data)
print(f"Found {total_links} course detail links to open.")

#######################################################################################

# Logging into the Drexel Master Schedule
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
wait.until(EC.presence_of_element_located((By.NAME, "_eventId_proceed"))).click()
wait.until(EC.presence_of_element_located((By.NAME, "loginfmt"))).send_keys(username + "\n")
wait.until(EC.presence_of_element_located((By.NAME, "passwd"))).send_keys(password + "\n")

# Wait for manual 2FA approval
print("Waiting for manual sign-in (approve request or 2FA)...")
while "webtms_du" not in driver.current_url:
    time.sleep(1)
print("Sign-in successful! Opening each room_finder.txt class in a new tab.")

#######################################################################################

# Opening every class from room_finder.txt, same tab-opening logic as TimeChecker.py
first = True
for index, parts in enumerate(course_detail_data, start=1):
    if len(parts) != 3:
        print(f"Skipping malformed line {index}: {parts}")
        continue

    course_detail_link, collCode_link, course_list_link = [p.strip() for p in parts]

    try:
        if not first:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
        first = False

        print(f"{index}/{total_links}: Opening course list page...")
        driver.get(course_list_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"{index}/{total_links}: Opening collCode page...")
        driver.get(collCode_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"{index}/{total_links}: Opening course detail page...")
        driver.get(course_detail_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"{index}/{total_links}: Opened {course_detail_link}")

    except Exception as e:
        print(f"{index}/{total_links}: Error opening {course_detail_link}: {e}")

print("All room_finder.txt classes have been opened in tabs.")
