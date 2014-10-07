#!/bin/python

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import *

db = create_engine('sqlite:///flats_data.db')

SQLBase = declarative_base()






class Flat(SQLBase):
    __tablename__ = 'flats'

    id = Column(Integer, primary_key = True)

    room_count = Column(Integer)
    category = Column(String)   # 'room', 'WG', 'flat', 'house'
    level = Column(Integer)       # 0: EG, 1: 1.OG, ...

    address = Column(String)
    lat = Column(Integer)
    lon = Column(Integer)

    source_url = Column(Integer)







