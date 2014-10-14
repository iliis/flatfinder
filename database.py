#encoding: utf-8

import difflib

from sqlalchemy import * #Column, Integer, String, Float, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DB_ENGINE = create_engine('sqlite:///flats_data.db', echo=False, encoding='utf-8', convert_unicode=True)
DB_BASECLASS = declarative_base(bind=DB_ENGINE)
DB_SESSIONCLASS = sessionmaker(bind=DB_ENGINE)

DB = DB_SESSIONCLASS()


def bayesian_update(prior, evidence_observed, evidence_given_hypothesis, evidence_given_not_hypothesis):
    """
    We estimate the likelihood of some hypothesis H as P(H) = prior.
    For the 'Flat'-class we want to know how similiar two entries are,
    i.e. P(F1 == F2) given some attributes like price or address.

    Now, we observe some evidence E: Two attributes are identical (e.g. two
    flats cost the same). However, this measurement might be partial only
    as we want be somewhat robust against noisy attributes (for example,
    one site might report the brutto price while another reports the
    netto value). evidence_observed is 1 if the attributes are exactly
    equal and 0 if they are certain to be different. I.e. the probability/
    confidence that we actually observed E.

    Given the hypothesis (the two flats are the same) or its inverse, we say
    how likely the observed evidence is. These two values are quite independent:

    Two ads for the same flat probably report the same price, so
    evidence_given_hypothesis is close to 1. But two different flats might
    conceiveably cost the same as well, so evidence_given_not_hypothesis is not
    so close to 0.

    """

    assert 0 <= prior <= 1
    assert 0 <= evidence_observed <= 1
    assert 0 <= evidence_given_hypothesis <= 1
    assert 0 <= evidence_given_not_hypothesis <= 1


    marginal = ( evidence_given_hypothesis * prior \
        + evidence_given_not_hypothesis * (1-prior) )

    factor = evidence_observed * evidence_given_hypothesis \
           + (1-evidence_observed) *evidence_given_not_hypothesis

    #print "evidence_observed:", evidence_observed
    #print "factor:", factor
    #print "marginal:", marginal

    posterior = prior * factor / marginal

    assert 0 <= posterior <= 1

    return posterior


def spike_hat(x, y, deviation):
    """
    returns 1 if x == y
            0 for x > y + deviation
            0 for x < y - deviation
            0-0.8 in between


             |
            / \
    _______/   \_______
    """

    # special cases: None
    if not x and not y:
        return 0.2 # both are missing this attribute, but this doesn't say all that much
    elif not x or not y:
        return 0

    if x == y:
        return 1
    elif abs(x-y) >= deviation:
        return 0
    else:
        return abs(x-y)/float(deviation) * 0.8

class SimilarityAssoc(DB_BASECLASS):
    __tablename__ = 'flat_similarity'
    left_id  = Column(Integer, ForeignKey('flats.id'), primary_key = True)
    right_id = Column(Integer, ForeignKey('flats.id'), primary_key = True)
    similarity = Column(Float)

    left  = relationship("Flat", primaryjoin = "flats.c.id == flat_similarity.c.left_id")
    right = relationship("Flat", primaryjoin = "flats.c.id == flat_similarity.c.right_id")

    def __init__(self, flat1, flat2, similarity):
        self.left  = flat1
        self.right = flat2
        self.similarity = similarity

class Flat(DB_BASECLASS):
    """ This class represents specific properties to rent """

    __tablename__ = 'flats'

    id = Column(Integer, primary_key=True)

    # similarity measure to other entries
    similar_entries = relationship("SimilarityAssoc",
            secondary = "flat_similarity",
            primaryjoin   = "flats.c.id == flat_similarity.c.left_id", #id == flat_similarity_table.c.left_id,
            secondaryjoin = "flats.c.id == flat_similarity.c.right_id", #id == flat_similarity_table.c.right_id,
            backref = "similar_entries_reversed")

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
    source_url = Column(String)


    def __repr__(self):
        return "------------------------------\n" + \
               "Strasse:  " + unicode(self.address_street).encode('utf-8') + '\n' + \
               "PLZ ORT:  " + unicode(self.address_plz).encode('utf-8') + \
                        " " + unicode(self.address_city).encode('utf-8') + '\n' + \
               "Zimmer:   " + unicode(self.room_count).encode('utf-8') + '\n' + \
               "Fläche:   " + unicode(self.room_area).encode('utf-8') + '\n' + \
               "Etage:    " + unicode(self.level).encode('utf-8') + '\n' + \
               "Kategorie:" + unicode(self.category).encode('utf-8') + '\n' + \
               "Miete:    " + unicode(self.rent_monthly_brutto).encode('utf-8') + '\n' + \
               "------------------------------\n"

    def similarity(self, other):
        """
        This is basically a fancy '==' operator to detect duplicated entries
        from different sources. It returns a value between zero and one,
        indicating the similarity between self and other, i.e. the probability
        for self == other.
        """

        s = 0.01 # low prior probability for self == other

        s = bayesian_update(s, spike_hat(self.rent_monthly_brutto,
                                         other.rent_monthly_brutto,
                                         200),
                            0.95, # if self == other, its quite likely they have the same price
                            0.02)  # but if not, others might still have the same price (about 1 in 50 here)

        s = bayesian_update(s, spike_hat(self.room_area,   other.room_area,   1), 0.99, 0.04)
        s = bayesian_update(s, spike_hat(self.address_plz, other.address_plz, 1), 0.99, 0.2)

        # use levenshtein distance for strings
        # TODO: can we encode correlation between PLZ and city?


        if self.address_city and other.address_city:
            s = bayesian_update(s,
                    difflib.SequenceMatcher(None, self.address_city, other.address_city).ratio(),
                    0.99, 0.05)

        if self.address_street and other.address_street:
            s = bayesian_update(s,
                    difflib.SequenceMatcher(None, self.address_street, other.address_street).ratio(),
                    0.99, 0.01)

        if False:
            if self.short_desc and other.short_desc:
                s = bayesian_update(s,
                        difflib.SequenceMatcher(None, self.short_desc, other.short_desc).ratio(),
                        0.95, 0.002)

            if self.long_desc and other.long_desc:
                s = bayesian_update(s,
                        difflib.SequenceMatcher(None, self.long_desc, other.long_desc).ratio(),
                        0.95, 0.002)

            if self.category and other.category:
                s = bayesian_update(s,
                        difflib.SequenceMatcher(None, self.category, other.category).ratio(),
                        0.99, 0.4) # category isn't a very good measure, mosts are "Wohnung" anyway

            s = bayesian_update(s, spike_hat(self.level, other.level, 1), 0.99, 0.1)

            if self.source_url and other.source_url:
                s = bayesian_update(s,
                        difflib.SequenceMatcher(None, self.source_url, other.source_url).ratio(),
                        0.01, # if we have the same entry twice, they are probably from different sites
                        0.00001) # but if they arent the same, they certainly don't have the same link!

        return s

    def similarity_assoc(self, other):
        return SimilarityAssoc(self, other, self.similarity(other))

def calculate_similarity_for_all(threshold):
    for flat1 in DB.query(Flat):
        for flat2 in DB.query(Flat):
            s = flat1.similarity(flat2)

            if s >= threshold:
                print flat1.id, ":", flat1.address_street, "is similiar to one at",
                print flat2.id, ":", flat2.address_street, "(p =", s, ")"
