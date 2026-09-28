# Drexel Room Time Finder
A tool that allows you to find if any room in the Drexel term is being used at a certain time by a class

## Motivation
GBM's for the Drexel Electric Racing club often have to move rooms because of a class using up the time slot, so it would be useful to know in advance when to schedule the GBM

## Overview
First of all, the Drexel term master schedule website works in a strange way that you need to go through every link first before you can view the specific class, you cannot just go to the link immediately. So if you're wondering why each text file has multiple links, thats why.

The first python script (`EveryCourseGrabber.py`) grabs a link for every lecture, lab, recitation, etc... scheduled during the term given to the script.

The second python script (`RoomFinder.py`) goes through every one of the links from the first script, and checks if they are in the building and room number you provided.

The third python script (`TimeChecker.py`) checks every link from script two and checks if they contain the times in the range given to it.

I decided to go with three scripts so that you dont have to go through all 3400 classes everytime you want to change the time search in the third script just in case its needed. Also if there were any crashes you will lose less progress.

## Setup

### 1. Install dependencies
```
pip install selenium
```
(You also need Chrome + the matching chromedriver on your PATH.)

### 2. Credentials
Insert yout Drexel email/password into the plain text file named `credentials.txt` in this same folder, with:
```
your_email@drexel.edu
your_password
https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/202535?collCode=
```
(email on line 1, password on line 2, term master schedule link on line 3 — nothing else in the file)

Line 3 should look something like `https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/202425?collCode=` — swap in whichever term you're searching through.

All three scripts read from that file automatically.

## Instructions
1. Go to `https://termmasterschedule.drexel.edu/webtms_du/`, select the term you are searching through, and copy the link. Paste it into line 3 of your `credentials.txt`, it should look something like this: `https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/202425?collCode=`. Then run `EveryCourseGrabber.py`.

2. Run `RoomFinder.py` and type in the EXACT building name and room number when prompted. (this is the one that takes 45mins)

3. Run `TimeChecker.py` and give the two times for the range you want to check if the room is being used. At the end of the script all of the time conflict links will be opened and you can go through them to check the days. Note there is a quirk where if the final exam takes place in that room during that range it will pick it up, so go through the links afterwards to make sure there aren't false positives.

Alternatively running the script early in the term before there are final exam dates would fix this as well.