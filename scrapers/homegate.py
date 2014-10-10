from scraper import *
from database import *
import time

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

# TODO: remove session ID from link, maybe start a whole new session

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

        max_tries = 4
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
                    s = 10*(5-max_tries)
                    print "waiting", s, "seconds ..."
                    time.sleep(s)
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
