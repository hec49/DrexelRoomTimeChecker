import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

# Ask the user for the building and room number
building = input("Enter the building name you are looking for: \nCHECK MASTER TERM SCHEDULE FOR EXACT SPELLING IF YOU ARE UNSURE\n").strip()
room_number = input("Enter the room number you are looking for: ").strip()

#######################################################################################

# Opening correct file

script_directory = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_directory, "every_class_in_term.txt")
output_file = os.path.join(script_directory, "room_finder.txt")


if not os.path.exists(input_file):
    print(f"Error: {input_file} does not exist.")
    exit(1)


with open(input_file, "r") as file:
    course_detail_data = [line.strip().split("|") for line in file.readlines()]

total_links = len(course_detail_data)
print(f"Found {total_links} course detail links to process.")

#######################################################################################

# Logging into the Drexel Master Schedule
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=chrome_options)


driver.get("https://termmasterschedule.drexel.edu/webtms_du/")

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


print("Waiting for manual sign-in (approve request or 2FA)...")
while True:
    if "webtms_du" in driver.current_url:
        break
    time.sleep(0.5)

print("Sign-in successful! Starting to process course detail links.")

#######################################################################################

collected_course_details_info = set()

# Room Finder Logic
for index, (course_detail_link, collCode_link, course_list_link) in enumerate(course_detail_data, start=1):
    try:
        print(f"Processing {index}/{total_links}: Navigating to course list page...")
        driver.get(course_list_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"Processing {index}/{total_links}: Navigating to collCode page...")
        driver.get(collCode_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"Processing {index}/{total_links}: Navigating to course detail page...")
        driver.get(course_detail_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = driver.page_source

        if building in page_source and room_number in page_source:
            print(f"{index}/{total_links}: Collected course info")

    except Exception as e:
        print(f"{index}/{total_links}: Error processing {course_detail_link}: {e}")

    time.sleep(0.1)

#######################################################################################

# Save courses to file
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w") as file:
    for info in collected_course_details_info:
        file.write(info + "\n")

print(f"Processing complete! Saved course details information to {output_file}")
driver.quit()