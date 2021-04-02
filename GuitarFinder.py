# Developed by Evan Cole (https://github.com/ecole96) on April 1, 2021
# This script scans several guitar sale forums (Acoustic Guitar Forum, The Gear Page, Unofficial Martin Guitar Forum) for new listings based on user-input search criteria
# The user inputs a string of comma-delimited terms / items to look for, and if there is a never-before-seen match, a desktop notification is pushed that opens the listing when clicked
# This was built to help me find a nice used Martin acoustic, so the focus is narrow, but it could potentially be extended to other musical equipment and websites
# As of now, it only works with Mac OS - this is because the notifications library (pync) is built exclusively for it
# Ideally used with a cronjob for continual checking

from bs4 import BeautifulSoup
import tldextract
import requests
import sqlite3
import pync
import sys
import os
my_absolute_dirpath = os.path.abspath(os.path.dirname(__file__))

# download web page, return as BeautifulSoup object for parsing
def download(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    request = requests.get(url,headers={'User-Agent':user_agent},timeout=15)
    page = request.content
    soup = BeautifulSoup(page, 'lxml')
    return soup

# returns domain name of URL for use in notification message
def getDomain(url):
    return tldextract.extract(url.lower()).domain

# returns for-sale listings at Acoustic Guitar Forum
def agf():
    url = "https://www.acousticguitarforum.com/forums/forumdisplay.php?f=17&daysprune=1&order=desc&sort=lastpost"
    listings = []
    try:
        soup = download(url)
        listings = [(a.text.strip(),"https://www.acousticguitarforum.com/forums/"+a['href']) 
                    for a in 
                        [thread.select_one("a[id*='thread_title']") 
                            for thread in 
                            soup.select("td[id*='td_threadtitle'] > div:nth-of-type(1)") 
                            if thread.text.strip().lower().startswith('for sale')
                        ]
                   ]
    except Exception as e:
        print(e)
    return listings

# returns for-sale listings at the Unofficial Martin Guitar Forum
def umgf():
    url = "https://umgf.com/buy-and-sell-f23/"
    listings = []
    try:
        soup = download(url)
        skipTerms = ['wtb', 'want', 'wtt', 'sold', 'delete', 'close','pending']
        listings = [(a.text.strip(),a['href'].split("?")[0]) 
                    for a in soup.select("div.normal dl.topic_read_hot div.responsive-hide a.topictitle") 
                    if not any([term in a.text.lower().strip() for term in skipTerms])]
    except Exception as e:
        print(e)
    return listings

# returns for-sale listings at The Gear Page
def tgp():
    # site allows one to filter by For Sale / For Sale Or Trade, but not both at once so doing each filter
    urls = ["https://www.thegearpage.net/board/index.php?forums/guitar-emporium.22/&prefix_id=1&last_days=7&order=post_date&direction=desc",
            "https://www.thegearpage.net/board/index.php?forums/guitar-emporium.22/&prefix_id=3&last_days=7&order=post_date&direction=desc"]
    listings = []
    for url in urls:
        try:
            soup = download(url)
            page_listings = [(a.text.strip(),"https://www.thegearpage.net"+a['href']) for a in soup.select("div.structItem-title a:nth-of-type(2)")]
            listings += page_listings
        except Exception as e:
            print(e)
    return listings

# gathers listings from each site and puts them into a single array
def collect():
    listings = agf() + umgf() + tgp()
    return listings

# sends desktop notification for new, relevant listing (only works for Mac OS)
def sendNotification(item,listing_title,listing_url):
    msg = "At %s: %s" % (getDomain(listing_url),listing_title)
    title = 'New Guitar Listing: %s' % item
    APP_ICON = os.path.join(os.path.dirname(__file__), 'icons8-guitar-48.png')
    pync.notify(msg,title=title,open=listing_url,appIcon=APP_ICON)

# check if any new listings match the desired terms / items - if so, send notifications
def checkListings(listings,toSearch,db_cursor):
    for listing in listings:
        listing_title = listing[0]
        listing_url = listing[1]
        for term in toSearch:
            if term.lower() in listing_title.lower():
                db_cursor.execute("""SELECT COUNT(*) FROM listings WHERE url=?""",(listing_url,))
                listingAlreadySeen = bool(db_cursor.fetchone()[0])
                if not listingAlreadySeen: # don't send a notification if one's already been sent for that listing
                    print(term+":",listing_title,"("+listing_url+")")
                    sendNotification(term,listing_title,listing_url)
                    db_cursor.execute("""INSERT INTO listings(url) VALUES (?)""",(listing_url,))
    
def main():
    if len(sys.argv) < 2: # items are read in via command line argument
        print("Items not set: provide a command line argument in the form of a comma-delimited list of items (as a quotation-enclosed string) for the script to search for.")
    else:
        toSearch = [term.strip() for term in sys.argv[1].split(",")]
        listings = collect()
        DB_FILENAME = os.path.join(os.path.dirname(__file__), 'listings.db')
        with sqlite3.connect(DB_FILENAME) as db:
            c = db.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS listings(url TEXT NOT NULL, datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
            checkListings(listings,toSearch,c)

main()