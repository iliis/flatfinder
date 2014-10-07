#!/bin/python
""" This script scrapes various websites for flats and other things to rent """

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()


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



def scrape_homegate():
    """ gets entries from homegate.ch """

    f = Flat()
    f.category = "test"
    f.level = 123
    f.address = "somewhere"
    f.source_url = "made up"
    return [f]





# INIT: create tables
# DB_BASECLASS.metadata.create_all(DB_ENGINE)

fs = scrape_homegate()
DB.add_all(fs)
DB.commit()

