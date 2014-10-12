from scraper import *
from database import *
import time

def homegate_parse_link(href):
    return re.search('^(http://.+)(;jsessionid.*)?', href).group(1)

class ScraperHomegate(FlatScraper):

    def get_start_link(self):
        return 'http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?mn=ctn_zh&oa=false&ao=&am=&an=&a=default&tab=list&incsubs=default&l=default'

    def get_next_page_link(self, soup):
        """ parses link to next page of search result table. returns None if not
        found (probably because this was the last page) """

# TODO: remove session ID from link, maybe start a whole new session

        t = soup.find('table', id='pictureNavigation')
        if t:
            t = t.find('a', class_='forward iconLink')
            if t:
                return t['href']
        return None


    def scrape_page(self, soup):
        """ gets entries from homegate.ch """

        itemtable = soup.find('table', id='objectList').find('tbody')

        all_flats = []

        for item in itemtable.find_all('tr'):
            tds = item.find_all('td')

            f = Flat()
            f.source_url = homegate_parse_link(tds[0].a['href'])
            f.short_desc = tds[2].a.string.strip()

            addr = parse_br_list(tds[3].a.contents)

            f.address_street = addr[0]
            f.address_plz    = int(addr[1])
            f.address_city   = addr[2]

            details = parse_br_list(tds[4].a.contents)

            if (details[0]):
                f.room_count     = parse_room_count(details[0])
            if (details[2]):
                f.room_area      = parse_area_count(details[2])
            f.level              = parse_floor_level(details[1])

            details = parse_br_list(tds[5].a.contents)

            if (details[0]):
                f.category = details[0]

            price = tds[5].find_all('a')[1].text.encode('utf-8').strip()
            if (price):
                f.rent_monthly_brutto = parse_price(price)

            all_flats.append(f)

        return all_flats
