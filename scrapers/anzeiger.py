from scraper import *
from database import *

def scrape_anzeiger_table(soup):
    flats = []

    itemtable = soup.find('div', id='resultList')

    for row in itemtable.find_all('div', class_='row'):
        f = Flat()

        cell = row.find('div', class_='cell2')
        f.source_url = 'http://www.anzeiger.ch/mieten/' + re.search('^/mieten/(\d+)/.*', cell.a['href']).group(1)

        f.short_desc = cell.a.text
        f.long_desc = unicode(cell.br.next_sibling).strip()

        cell = parse_br_list(row.find('div', class_='cell3'))

        f.address_street = cell[0]

        addr = re.search('(\d+) (.*)', cell[1])
        if addr:
            f.address_plz = int(addr.group(1))
            f.address_city = addr.group(2).strip()


        cell = parse_br_list(row.find('div', class_='cell4'))

        f.room_count = parse_room_count(cell[0])
        f.room_area  = parse_area_count(cell[1])

        cell = parse_br_list(row.find('div', class_='cell5'))

        f.category = cell[0].strip()
        f.rent_monthly_brutto = parse_price(cell[2])


        flats.append(f)


    return flats
