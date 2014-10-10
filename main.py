#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

import re
import os
import md5
import random # for intrand
import time # for sleep()
import sys # for stdout.flush()

from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=False, encoding='utf-8', convert_unicode=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()


from bs4 import BeautifulSoup
from bs4 import element
import dryscrape

"""
import urllib2
urlopener = urllib2.build_opener()
#urlopener.addheaders = [('User-agent', 'Mozilla/5.0')]
urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6')]
"""


class Flat(DB_BASECLASS):
    """ This class represents specific properties to rent """

    __tablename__ = 'flats'

    db_id = Column(Integer, primary_key=True)

    room_count = Column(Float)
    room_area  = Column(Integer)  # in m^2
    category = Column(String)     # 'room', 'WG', 'flat', 'house'
    level = Column(Integer)       # 0: EG, 1: 1.OG, ...

    #address = Column(String)
    address_street = Column(String)
    address_plz    = Column(Integer)
    address_city   = Column(String)
    lat = Column(Integer)
    lon = Column(Integer)

    source_url = Column(Integer)

    short_desc = Column(String)
    long_desc  = Column(String)

    rent_monthly_brutto = Column(Integer)
    rent_monthly_netto  = Column(Integer)

    def foofoo(self):
        """ asdfasdf """
        self.address = "asdfasdf"

def url_to_filename(url):
    """ creates a human readable hash from url which is also a valid filename """
    domain = re.search('^(http://)?([A-Za-z\.-_/]+)/.*', url).group(2)
    domain = domain.replace('.', '_').replace('/', '_')
    return domain + "__" + str(md5.new(url).hexdigest()) + ".html"

def download_site(url, filename, dryscrape_session):
    dryscrape_session.visit(url)
    with open(filename, "wb") as localfile:
        localfile.write(dryscrape_session.body())

    #data = urlopener.open(url).read()
    #with open(filename, "wb") as localfile:
        #localfile.write(data)

def getfile_cached(url, dryscrape_session):
    """ returns local copy of 'url' and downloads it if its not chached yet. """
    path = 'html_cache/'+url_to_filename(url)
    if not os.path.exists(path):
        s = random.randint(1, 8)
        print url, "not found in cache."
        print "waiting", s, "seconds ...",
        sys.stdout.flush()
        time.sleep(s)
        print "OK"
        print "downloading to", path, "...",
        download_site(url, path, dryscrape_session)
        print "OK"
    else:
        print "found cached copy of", url, "at", path
    return open(path)

def destroy_cached_file(url):
    if not url:
        print "cannot delete url, it's invalid:", url
        return
    path = 'html_cache/'+url_to_filename(url)
    if os.path.exists(path):
        print "deleting", path
        os.remove(path)
    else:
        print "cannot delete cache of", url, "==", path, ": it's not cached"

def homegate_parse_link(href):
    return re.search('^(http://.+)(;jsessionid.*)?', href).group(1)

def homegate_parse_floor_level(text):
    if not text:
        return None
    if "EG" in text:
        return 0
    if "UG" in text:
        return -1
    else:
        return re.search('^(\d+)\..*', text).group(1)

def homegate_parse_br_array(data):
    arr = []
    last_was_valid = False
    for d in data:
        if type(d) is element.Tag: # <br/>
            if (last_was_valid):
                # this <br/> is just a break between normal elements
                last_was_valid = False
            else:
                # this <br/> has no preceding string, i.e. the string was empty
                arr.append(None)
                last_was_valid = True
        else:
            arr.append(unicode(d).strip())
            last_was_valid = True
    return arr

def homegate_get_next_page_link(soup):
    """ parses link to next page of search result table. returns None if not
    found (probably because this was the last page) """

    t = soup.find('table', id='pictureNavigation')
    if t:
        t = t.find('a', class_='forward iconLink')
        if t:
            return t['href']
    return None


def scrape_homegate_table(soup):
    """ gets entries from homegate.ch """

    itemtable = soup.find('table', id='objectList').find('tbody')

    all_flats = []

    for item in itemtable.find_all('tr'):
        tds = item.find_all('td')

        f = Flat()
        f.source_url = homegate_parse_link(tds[0].a['href'])
        f.short_desc = tds[2].a.string.strip()

        addr = homegate_parse_br_array(tds[3].a.contents)

        f.address_street = addr[0]
        f.address_plz    = int(addr[1])
        f.address_city   = addr[2]

        details = homegate_parse_br_array(tds[4].a.contents)

        if (details[0]):
            f.room_count     = float(re.search('^(\d+\.\d).*', details[0]).group(1))
        if (details[2]):
            f.room_area      = int(re.search('^(\d+).*', details[2]).group(1))
        f.level              = homegate_parse_floor_level(details[1])

        details = homegate_parse_br_array(tds[5].a.contents)

        if (details[0]):
            f.category = details[0]

        price = tds[5].find_all('a')[1].text.encode('utf-8').strip()
        if (price):
            p = re.search('^(\d+)\.--.*', price.replace('\'',''))
            if p:
                f.rent_monthly_brutto = int(p.group(1))

        print f.address_street
        print f.address_plz
        print f.address_city
        print f.room_count
        print f.level
        print f.room_area
        print f.category
        print f.rent_monthly_brutto
        print '------------------------------'

        all_flats.append(f)

    return all_flats


def scrape_homegate():
    sess = dryscrape.Session(base_url = 'http://www.homegate.ch/')
    sess.set_attribute('auto_load_images', False)
    url = 'http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?mn=ctn_zh&oa=false&ao=&am=&an=&a=default&tab=list&incsubs=default&l=default'

    all_flats = []

    while True:

        soup = None

        max_tries = 3
        while max_tries > 0:
            try:
                max_tries = max_tries - 1
                print "parsing", url
                htmldocument = getfile_cached(url, sess)
                soup = BeautifulSoup(htmldocument)

                fs = scrape_homegate_table(soup)
            except:
                if max_tries > 0:
                    print "failed to parse", url, "trying again."
                    destroy_cached_file(url)
                else:
                    print "failed to parse", url, "too many times. giving up."
                    return

        all_flats.extend(fs)

        if soup:
            url = homegate_get_next_page_link(soup)
            if url:
                continue

        break

    return all_flats




if not os.path.exists('flats_data.db'):
    # INIT: create tables
    print "creating empty database ..."
    DB_BASECLASS.metadata.create_all(DB_ENGINE)

if not os.path.exists('html_cache'):
    os.mkdir('html_cache')


all_entries = 'http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?mn=ctn_zh&oa=false&ao=&am=&an=&a=default&tab=list&incsubs=default&l=default'


fs = scrape_homegate()

print "done. found", len(fs), "entries"

DB.add_all(fs)
DB.commit()

