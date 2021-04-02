# GuitarFinder
GuitarFinder is a script developed by [Evan Cole](https://github.com/ecole96) on April 1, 2021. Its purpose is to assist its users in finding used guitars they're looking for, scanning various marketplaces across the web for new sale listings and notifying users via desktop notifications.

## How It Works
As a Python script, GuitarFinder is called from the command line, on the user's local machine. It requires a single command line argument: a string consisting of the terms and/or items the user wants to receive notifications for, delimited by commas. If a listing title matches any of the terms provided (and has not previously been found), a notification will be pushed to the user's desktop. Clicking the notification will open up the user's browser and take them straight to the item listing.

Example script call:
```
python GuitarFinder.py "Martin D-28,Gibson Les Paul,Fender Telecaster"
```

For continual, automated updates, use GuitarFinder in a cronjob.

## Supported Websites
Currently, the following marketplaces are scanned:
* [The Gear Page - Guitar Emporium](https://www.thegearpage.net/board/index.php?forums/guitar-emporium.22/)
* [Acoustic Guitar Forum - Guitar Classifieds](https://www.acousticguitarforum.com/forums/forumdisplay.php?f=17)
* [Unofficial Martin Guitar Forum - Buy and Sell](https://umgf.com/buy-and-sell-f23/)

## Requirements
* Python 3
* Mac OS 10+ 

Use is currently limited to Mac OS due to the specialized notifications library used. 

## Installation
Download and extract this repo, install the dependencies with requirements.txt, and call GuitarFinder.py as necessary. As long as GuitarFinder.py remains in the project folder, it can be called from anywhere.