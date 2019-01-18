"""
This program will scrap each of the word from the wiktionary page. The starting page will be "https://en.wiktionary.org/wiki/Wiktionary:All_Thesaurus_pages".

Firstly we aim at constructing the scraper with 1 table and sqlite3 database.


"""

import sqlite3
import time
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import os.path

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('wikiDB.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS wiki_data (
    cnc   INTEGER,
    pid   INTEGER,
    sid    INTEGER,
    url   TEXT UNIQUE PRIMARY KEY,
    html  TEXT   
);
''')


def url_crawl(url,pid):
    #try:
    html = urllib.request.urlopen(url, context=ctx).read()	# html parser
    soup = BeautifulSoup(html, 'html.parser')
    cur.execute('''UPDATE wiki_data SET cnc = ? WHERE url = ?''',(1,url,))
    cur.execute('''UPDATE wiki_data SET html = ? WHERE url = ?''',(str(soup),url,))
    
    print(url,pid)
    #except:
    #fucked up
    #print("Ops something is wrong!")
    test_li = re.findall(r'<li>(.+)</li>',str(soup))
    #print(test_li) # it have all the list element
    url_str = 'https://en.wiktionary.org'
    cur.execute(''' SELECT max(sid) FROM wiki_data''')
    
    sid_max = cur.fetchone()[0] #converts the cursor object to number
    print("max sid = ",sid_max)
    if sid_max == None:
        sid_max = 0
    sid = sid_max + 1
    for item_li in test_li:
        find_first = item_li.find('href="')
        cut_first = find_first+6
        string_cut = item_li[cut_first:]
        find_sec = string_cut.find('"')
        get_url_part = string_cut[:find_sec]
        #print(get_url_part)
        next_url = url_str + get_url_part
        #print(next_url)
        cur.execute('''INSERT OR IGNORE INTO wiki_data (cnc, pid, sid, url, html)
					VALUES ( ?, ?, ?, ?, ? )''', ( 0,pid,sid, next_url, "", ) )
        sid += 1
    cur.execute('''SELECT min(sid) FROM wiki_data WHERE cnc = ?''',(0,))
    
    sid_ = cur.fetchone()[0] #converts the cursor object to number
    print("min sid= ",sid_)
    get_next_url = cur.execute('''SELECT url FROM wiki_data WHERE sid = ?''',(sid_,)).fetchone()[0]
    print("next url :  ",next_url)
    conn.commit()
    print("*************************************************** sid  ================",sid)
    #time.sleep(3)
    url_crawl(str(get_next_url),sid_-1)
    

if __name__ == "__main__":
    if os.path.isfile("wikiDB.sqlite") == True:
        # If the db exists
        cur.execute('''SELECT min(sid) FROM wiki_data WHERE cnc = ?''',(0,))
        
        sid_ = cur.fetchone()[0] #converts the cursor object to number
        print("min sid= ",sid_)
        get_next_url = cur.execute('''SELECT url FROM wiki_data WHERE sid = ?''',(sid_,)).fetchone()[0]
        url_crawl(str(get_next_url),sid_-1)
    else:
        #For the first time :)
        url = "https://en.wiktionary.org/wiki/Wiktionary:All_Thesaurus_pages"			# The first url that is entered, required for ignition
        pid = 0    #parent id : 0
        sid = 1    #self id : 0   
        cur.execute('''INSERT OR IGNORE INTO wiki_data (cnc, pid, sid, url, html)
                            VALUES ( ?, ?, ?, ?, ? )''', ( 0,pid,sid, url,"", ) )
        # insert the cnc, pid, sid and url 
        url_crawl(url,1)




