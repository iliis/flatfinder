#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

from scrapers.homegate import scrape_homegate
from database import *
import os

if not os.path.exists('flats_data.db'):
    # INIT: create tables
    print "creating empty database ..."
    DB_BASECLASS.metadata.create_all(DB_ENGINE)

if not os.path.exists('html_cache'):
    os.mkdir('html_cache')


fs = scrape_homegate()

print "done. found", len(fs), "entries"

DB.add_all(fs)
DB.commit()

