#encoding: utf-8

from scraper import *
from database import *

def parse_address_line(string):
    string = string.strip()
    lines = string.split(',')

    street = None
    plz_city = None

    if len(lines) == 1:
        # no street
        plz_city = lines[0].strip()
    elif len(lines) == 2:
        street   = lines[0].strip()
        plz_city = lines[1].strip()
    else:
        #raise Exception("Invalid address line: more than two or no lines in '" + string + "'.")
        print "Invalid address line: more than two or no lines in '" + string + "'."
        plz_city = lines[len(lines)-1]

    addr = re.search('(\\d+) (.*)', plz_city)
    if addr:
        return [street, int(addr.group(1)), addr.group(2).strip()]
    else:
        return [street, None, plz_city.strip()]
        print "WARNING: invalid address line: not in format 'PLZ CITY': '" + plz_city + "'."

def parse_size_details_line(string):

    room_count = None
    room_area = None
    floor_level = None

    for s in string.split(','):

        s = s.strip()

        if len(s) == 0:
            continue

        if "Zimmer" in s:
            room_count = float(re.search('(\d+).*', s).group(1))
            if u"\xbd" in s: # 1/2
                room_count += 0.5
        elif u"m\xb2" in s:
            room_area = int(re.search('[^\d]*(\d+).*', s).group(1))
        elif "Etage" in s or "EG" in s or "UG" or "Untergeschoss" in s:
            floor_level = parse_floor_level(s)
        else:
            raise Exception("unknown details data in string '" + s + "'.")

    return [ room_count, room_area, floor_level ]




def parse_creation_date(string):
    r = re.search('[^\d]*(\d+)\.(\d+)\.(\d+).*', string)
    if r:
        return datetime.date(int(r.group(3)), int(r.group(2)), int(r.group(1)))
    else:
        return None


class ScraperComparis(FlatScraper):

    def scrape_page(self, soup):
        flats = []

        for row in soup.find_all('div', class_='result-item'):
            f = Flat()

            f.source_url = 'https://www.comparis.ch' + row.find('a', class_='clickable-area')['href']

            desc = row.find('div', class_='description-column')

            f.short_desc = desc.h5.text

            addr = parse_address_line(desc.find('div', class_='single-line').text)
            f.address_street = addr[0]
            f.address_plz    = addr[1]
            f.address_city   = addr[2]

            details = desc.find('div', class_='details-section')

            f.rent_monthly_brutto = parse_price(details.find('div', class_='price-element').text.strip())

            details = details.find('div', class_='left').find_all('div', class_='single-line')
            f.category = details[0].text.strip()
            f.announce_time = parse_creation_date(details[2].text.strip())

            details = parse_size_details_line(details[1].text.strip())
            # [ room_count, room_area, floor_level ]
            f.room_count = details[0]
            f.room_area  = details[1]
            f.level      = details[2]

            flats.append(f)

        return flats

    def get_start_link(self):
        return 'https://www.comparis.ch/immobilien/marktplatz/zuerich/mieten'

    def get_next_page_link(self, soup):
        a = soup.find('div', class_='paging-container').find('a', class_='paging-arrow-forward')
        if a and a.has_attr('href'):
            return 'https://www.comparis.ch' + a['href']
        else:
            return None
