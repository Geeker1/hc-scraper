import os
import scrapy
from bs4 import BeautifulSoup
from gsearch.spiders import DATA_FOLDER

GOOGLE_SEARCH_URL = """https://www.google.com/search?tbm=lcl&sxsrf=A
CYBGNTHC5F2SzC0IbpoIh_zqwo64_l2CA%3A1580504053390&ei=9ZM0XuucEaSp8gLn
3byoAg&q=companies+in+portharcourt&oq=companies+in+porthar&gs_l=psy-ab.
3.0.35i39k1j0i10k1l5j0i22i10i30k1l4.24114.25392.0.28261.7.7.0.0.0.0.45
6.866.4-2.2.0....0...1c.1.64.psy-ab..5.2.864...0.0.iF_eofokIUw#rlfi=hd:
;si:;mv:[[4.8673719,7.1075542],[4.7729566,6.984253]]"""

COMPANY_JSON_FILE = os.path.join(DATA_FOLDER, 'company.jl')


class CompanySpider(scrapy.Spider):
    name = "company"

    custom_settings = {
        'FEED_URI': COMPANY_JSON_FILE,
        'FEED_FORMAT': 'jsonlines'
    }

    start_urls = [GOOGLE_SEARCH_URL]
    download_delay = 15.0

    _entry = 'div.VkpGBb'
    _name = 'div.dbg0pd div'
    _website = 'div.VkpGBb a.yYlJEf.L48Cpd::attr(href)'
    _map = 'div.VkpGBb a.yYlJEf.VByer::attr(data-url)'
    _rating = 'span.rllt__details.lqhpac span.BTtC6e::text'
    _contact = 'span.rllt__details.lqhpac div:nth-child(3) span:nth-child(2)::text'
    _next_page = 'td.b.navend a.pn::attr(href)'

    start = 0

    def __init__(self):
        if os.path.exists(COMPANY_JSON_FILE):
            msg = (
                f'{COMPANY_JSON_FILE}\n'
                'The path to this file already exists, '
                'REMOVE or RENAME this file before proceeding further\n'
            )
            raise FileExistsError(msg)
        return super(scrapy.Spider).__init__()

    def get_name(self, quote, name_selector):
        node = quote.css(name_selector).get()
        try:
            name = BeautifulSoup(node).text
            return name
        except TypeError:
            return ''

    def get_map(self, quote, map_selector):
        text_node = quote.css(map_selector).get()
        if text_node is not None:
            return 'https://google.com' + text_node

    def parse(self, response):

        if self.start == 30:
            return

        for quote in response.css(self._entry):
            yield {
                'name': self.get_name(quote, self._name),
                'website': quote.css(self._website).get(),
                'map': self.get_map(quote, self._map),
                'rating': quote.css(self._rating).get(),
                'contact': quote.css(self._contact).get()
            }

        self.start += 1

        next_page = response.css(self._next_page).get()
        if next_page:
            yield response.follow(next_page, self.parse)
