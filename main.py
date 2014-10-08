#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

import re

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()


from bs4 import BeautifulSoup
import urllib2

urlopener = urllib2.build_opener()
#urlopener.addheaders = [('User-agent', 'Mozilla/5.0')]
urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6')]


class Flat(DB_BASECLASS):
    """ This class represents specific properties to rent """

    __tablename__ = 'flats'

    db_id = Column(Integer, primary_key=True)

    room_count = Column(Integer)
    category = Column(String)     # 'room', 'WG', 'flat', 'house'
    level = Column(Integer)       # 0: EG, 1: 1.OG, ...

    address = Column(String)
    lat = Column(Integer)
    lon = Column(Integer)

    source_url = Column(Integer)

    def foofoo(self):
        """ asdfasdf """
        self.address = "asdfasdf"


def homegate_parse_link(href):
    return re.search('^(http://.+);jsessionid.*', href).group(1)

def scrape_homegate():
    """ gets entries from homegate.ch """

    all_entries = 'http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?mn=ctn_zh&oa=false&ao=&am=&an=&a=default&tab=list&incsubs=default&l=default'

    #page = urlopener.open(all_entries)
    #soup = BeautifulSoup(page)
    soup = BeautifulSoup(open('basiclist.html'))

    itemtable = soup.find_all(id='objectList')

    if (len(itemtable) != 1):
        raise "Invalid number of item tables: " + str(len(itemtable))

    itemtable = itemtable[0].find_all('tbody')[0]


    for item in itemtable.find_all('tr'):
        print homegate_parse_link(item.td.a['href'])
        #print item.find_all('td')[0].find_all('a')[0]

    #f = Flat()
    #f.category = "test"
    #f.level = 123
    #f.address = "somewhere"
    #f.source_url = "made up"
    #return [f]





# INIT: create tables
# DB_BASECLASS.metadata.create_all(DB_ENGINE)

fs = scrape_homegate()
#DB.add_all(fs)
#DB.commit()

