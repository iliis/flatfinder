import re
import os
import md5
import random # for intrand
import time # for sleep()
import sys # for stdout.flush()


from bs4 import BeautifulSoup
from bs4 import element
import dryscrape

"""
import urllib2
urlopener = urllib2.build_opener()
#urlopener.addheaders = [('User-agent', 'Mozilla/5.0')]
urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6')]
"""

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

def parse_br_list(data):
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

def parse_room_count(string):
    r = re.search('(\d+\.\d).*', string)
    if r:
        return float(r.group(1))
    else:
        return None

def parse_area_count(string):
    r = re.search('(\d+).*', string)
    if r:
        return int(r.group(1))
    else:
        return None

def parse_price(string):
    if not string:
        return None
    string = string.replace('\'', '')
    r = re.search('(\d+)\.--.*', string)
    if r:
        return int(r.group(1))
    else:
        return None
