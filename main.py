#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

from scrapers.homegate import ScraperHomegate
from scrapers.anzeiger import ScraperAnzeiger
from scrapers.comparis import ScraperComparis
from database import *
import os

if not os.path.exists('flats_data.db'):
    # INIT: create tables
    print "creating empty database ..."
    DB_BASECLASS.metadata.create_all(DB_ENGINE)

if not os.path.exists('html_cache'):
    os.mkdir('html_cache')


all_scrapers = [ScraperAnzeiger(), ScraperComparis(), ScraperHomegate()]





def scrape_everything():
    total = 0

    for scraper in all_scrapers:
        fs = scraper.scrape_all()
        total += len(fs)

        DB.add_all(fs)
        DB.commit()

    print "done. found", len(fs), "entries"




scrape_everything()



#fs = scrape_homegate()

#from bs4 import BeautifulSoup
#fs = scrape_anzeiger_table(BeautifulSoup(open('examples/anzeiger.html')))
#fs = scrape_comparis_table(BeautifulSoup(open('examples/comparis.html')))

#compscraper = ScraperComparis()
#fs = compscraper.scrape_all()

#scraper = ScraperComparis()
#fs = scraper.scrape_all()

#import dryscrape
#sess = dryscrape.Session()
#sess.set_attribute('auto_load_images', False)
#url = scraper.get_start_link()

#sess.visit(url)
#print sess.body()


#DB.add_all(fs)
#DB.commit()

