# Drexel Room Time Finder
A tool that allows you to find if any room in the Drexel term is being used at a certain time by a class

## Motivation
GBM's for the Drexel Electric Racing club often have to move rooms because of a class using up the time slot, so it would be useful to know in advance when to schedule the GBM

## Overview
First of all, the Drexel term master schedule website works in a strange way that you need to go through every link first before you can view the specific class, you cannot just go to the link immediately. So if you're wondering why each text file has multiple links, thats why.

The first python script grabs a link for every lecture, lab, recitation, etc... scheduled during the term given to the script.

The second python script goes through every one of the links from the first script, and checks if they are in the building and room number you provided in the script

The third python script checks every link from script two and checks if they contain the times in the range given to it

I decided to go with three scripts so that you dont have to go through all 3400 classes everytime you want to change the time search in the third script just in case its needed. Also if there were any crashes you would lose less progress.

## Instructions
### PREFACE:
Make sure that you have replaced your drexel email and password in each of the scripts

Example: username = "abc123@drexel.edu"  ||  password = "password456"


1. Follow the comments in EveryCourseGrabber and take the link of the term you're trying to search through, should look something like this: https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/202425?collCode= | paste it into the "" of driver.get() on line 35

2. Run RoomFinder and type in the EXACT building name and room number from the Drexel term master schedule website. (this is the one that takes 45mins so be careful)

3. Run TimeChecker and give the two times for the range you're to see if the room is being used. At the end of the script all of the time conflict links will be opened and you can go through them to check the days. Note there is a quirk where if the final exam takes place in that room during that range it will pick it up, so go through the links afterwards to make sure there aren't false positives.

Alternatively running the script early in the term before there are final exam dates would fix this as well.
