#encoding: utf-8

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=False, encoding='utf-8', convert_unicode=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()

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

    short_desc = Column(String)
    long_desc  = Column(String)

    rent_monthly_brutto = Column(Integer)
    rent_monthly_netto  = Column(Integer)

    rent_begin_date = Column(Date)
    rent_end_date = Column(Date)

    announce_time = Column(DateTime) # when was this entry put online

    # meta-data
    first_seen = Column(DateTime) # when did we download this entry for the first time?
    last_seen  = Column(DateTime) # when's the last time we downloaded this?
    source_url = Column(Integer)


    def show(self):
        print '------------------------------'
        print "Strasse:  ", self.address_street
        print "PLZ ORT:  ", self.address_plz, self.address_city
        print "Zimmer:   ", self.room_count
        print "Fläche:   ", self.room_area
        print "Etage:    ", self.level
        print "Kategorie:", self.category
        print "Miete:    ", self.rent_monthly_brutto
        print '------------------------------'
