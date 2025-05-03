import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
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

# Function to generate times in the specified range
def generate_time_range(start_time, end_time):
    intervals = [0, 30, 50, 20]
    times = []

    start_time = start_time.replace(" ", "").lower()
    end_time = end_time.replace(" ", "").lower()

    current_time = datetime.strptime(start_time, "%I:%M%p")
    end_time = datetime.strptime(end_time, "%I:%M%p")

    while current_time <= end_time:
        times.append(current_time.strftime("%I:%M %p").lstrip("0").lower())
        for interval in intervals:
            next_time = current_time + timedelta(minutes=interval)
            if next_time > end_time:
                break
            times.append(next_time.strftime("%I:%M %p").lstrip("0").lower())
        current_time += timedelta(hours=1)

    return sorted(set(times))

#######################################################################################

# Ask the user for the time range
start_time = input("INCLUDE THE SPACE AND MAKE SURE LOWERCASE\nEnter the start time (e.g., 6:00 pm): ").strip()
end_time = input("Enter the end time (e.g., 9:00 pm): ").strip()

times_to_check = generate_time_range(start_time, end_time)
print(f"Generated times to check: {times_to_check}")

#######################################################################################

# Opening correct file

script_directory = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_directory, "room_finder.txt")
output_file = os.path.join(script_directory, "time_conflict_classes.txt")


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
print("Sign-in successful! Starting course detail scanning.")

#######################################################################################

filtered_courses = set()

# Time Checker Locgic
for index, (course_detail_link, collCode_link, course_list_link) in enumerate(course_detail_data, start=1):
    try:
        print(f"Processing {index}/{total_links}: Opening course list page...")
        driver.get(course_list_link)  
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(.1)

        print(f"Processing {index}/{total_links}: Opening collCode page...")
        driver.get(collCode_link)  
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(.1)

        print(f"Processing {index}/{total_links}: Opening course detail page...")
        driver.get(course_detail_link)  
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = driver.page_source

        for time_string in times_to_check:
            page_lines = page_source.splitlines()
            time_found = False

            for line in page_lines: # Fixes bug where if the time was in the Last Updated section, it would be added to the list
                if time_string in line:
                    if 'Last Updated' in line:
                        continue
                    else:
                        time_found = True
                        break

            if time_found:
                filtered_courses.add(f"|{course_detail_link}|{collCode_link}|{course_list_link}")
                print(f"{index}/{total_links}: Added (Contains Time: {time_string})")
                break

    except Exception as e:
        print(f"{index}/{total_links}: Error processing {course_detail_link}: {e}")
    
    time.sleep(0.1)

#######################################################################################

# Save courses to file
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w") as file:
    for info in filtered_courses:
        file.write(info + "\n")

print(f"Processing complete! Saved valid courses to {output_file}")

#######################################################################################

# Opening each conflict class
for conflict in filtered_courses:
    try:
        course_detail_link, collCode_link, course_list_link = conflict.split("|")[1:]

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        print(f"Opening course list page for conflict...")
        driver.get(course_list_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"Opening collCode page for conflict...")
        driver.get(collCode_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)

        print(f"Opening course detail page for conflict...")
        driver.get(course_detail_link)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"Conflict opened in new tab: {course_detail_link}")

    except Exception as e:
        print(f"Error opening conflict link: {e}")

print("All conflicts have been opened in new tabs.")