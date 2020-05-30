import scrapy
import os
import json
import logging
import sys
from gsearch.spiders import DATA_FOLDER

HOTEL_JSON_FILE = os.path.join(DATA_FOLDER, 'hotels.jl')
DATA_FILE = os.path.join(DATA_FOLDER, 'data.json')

if os.path.exists(HOTEL_JSON_FILE):
    msg = (
        f'\033[91m {HOTEL_JSON_FILE}\n'
        'The path to this file already exists, '
        'REMOVE or RENAME this file before proceeding further\n\033[0m'
    )
    raise FileExistsError(msg)

with open(DATA_FILE, 'r') as fp:
    data = json.loads(fp.read())

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr
)
logger = logging.getLogger("hotel-spider")
logging.getLogger("chardet.charsetprober").disabled = True


class HotelSpider(scrapy.Spider):
    name = "hotels"

    custom_settings = {
        'FEED_URI': HOTEL_JSON_FILE,
        'FEED_FORMAT': 'jsonlines'
    }

    _address = 'div.K4nuhf span:nth-child(1)::text'
    _phone = 'div.K4nuhf span:nth-child(3)::text'
    _website = 'a.FKF6mc.TpQm9d::attr(href)'
    _rating = 'div.iDqPh.BgYkof::text'
    _name = 'h1.fZscne::text'

    start_urls = data
    count = 1

    def __init__(self):
        if os.path.exists(HOTEL_JSON_FILE):
            msg = (
                f'{HOTEL_JSON_FILE}\n'
                'The path to this file already exists, '
                'REMOVE or RENAME this file before proceeding further\n'
            )
            raise FileExistsError(msg)
        return super(scrapy.Spider).__init__()

    def parse(self, response):
        yield {
            'name': response.css(self._name).get(),
            'address': response.css(self._address).get(),
            'website': response.css(self._website).get(),
            'rating': response.css(self._rating).get(),
            'phone': response.css(self._phone).get()
        }
        self.count += 1
        logging.info(f"Done with Link {self.count}")
