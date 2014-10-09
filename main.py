#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

import re

from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()


from bs4 import BeautifulSoup
from bs4 import element
import urllib2

urlopener = urllib2.build_opener()
#urlopener.addheaders = [('User-agent', 'Mozilla/5.0')]
urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6')]


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


def homegate_parse_link(href):
    return re.search('^(http://.+);jsessionid.*', href).group(1)

def homegate_parse_floor_level(text):
    if not text:
        return None
    if "EG" in text:
        return 0
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
            arr.append(d.encode('utf-8').strip())
            last_was_valid = True
    return arr



def scrape_homegate_table(htmldocument):
    """ gets entries from homegate.ch """

    all_entries = 'http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?mn=ctn_zh&oa=false&ao=&am=&an=&a=default&tab=list&incsubs=default&l=default'

    #page = urlopener.open(all_entries)
    #soup = BeautifulSoup(page)
    soup = BeautifulSoup(htmldocument)

    itemtable = soup.find_all(id='objectList')

    if (len(itemtable) != 1):
        raise "Invalid number of item tables: " + str(len(itemtable))

    itemtable = itemtable[0].find_all('tbody')[0]

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
            f.rent_monthly_brutto = int(re.search('^(\d+)\.--.*', price.replace('\'','')).group(1))

        print f.address_street
        print f.address_plz
        print f.address_city
        print f.room_count
        print f.level
        print f.room_area
        print f.category
        print f.rent_monthly_brutto
        print '------------------------------'

        #print f.level
        #print item.find_all('td')[0].find_all('a')[0]

    #f = Flat()
    #f.category = "test"
    #f.level = 123
    #f.address = "somewhere"
    #f.source_url = "made up"
    #return [f]





# todo: autocreate
# INIT: create tables
# DB_BASECLASS.metadata.create_all(DB_ENGINE)

fs = scrape_homegate_table(open('basiclist.html'))
#DB.add_all(fs)
#DB.commit()

