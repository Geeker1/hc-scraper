import argparse
import os
import json
import logging
import sys
from typing import List

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import ErrorInResponseException,\
    NoSuchElementException, TimeoutException

from bs4 import BeautifulSoup

HOTEL_SEARCH_URL = '''https://www.google.com/travel/hotels/Port%20Harcourt?
g2lb=2502405%2C2502548%2C4208993%2C4254308%2C4258168%2C4260007%2C4270442%2
C4274032%2C4291318%2C4305595%2C4308216%2C4314846%2C4315873%2C4317915%2C43
26765%2C4328159%2C4329288%2C4330113%2C4338438%2C4340162%2C4270859%2C428497
0%2C4291517%2C4292955%2C4316256&hl=en&gl=ng&un=1&q=hotels%20in%20portharcour
t&rp=EJzyzNrum6mvwgEQ3eiwzfzSxI_EARCdoeqY8uDj_GwQlbzy0e7x3YYdOAFAAEgC&ictx=1
&ved=2ahUKEwi6oK7Qu6LnAhWL2BQKHU0ZBOQQtccEegQICxBv&hrf=CgYI8KsBEAAiA05HTioWC
gcI5A8QARgfEgcI5A8QAhgBGAEoALABAFgBaAGaAQ8SDVBvcnQgSGFyY291cnSiARoKCS9tLzAya
nRzeRINUG9ydCBIYXJjb3VydKoBCgoCCCESAggvGAGSAQIgAQ'''

NEXT_BUTTON = "div.U26fgb.O0WRkf.oG5Srb.C0oVfc.JDnCLc.yHhO4c.yNl8hd.zbLWdb"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr
)
logger = logging.getLogger("selenium")
logging.getLogger("chardet.charsetprober").disabled = True


def main(url) -> None:
    links = []
    options = Options()
    options._arguments = ['-headless']

    with webdriver.Firefox(options=options) as driver:
        try:
            driver.get(url)
        except ErrorInResponseException as e:
            raise e('There was an error in the network')

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "f1dFQe"))
        )
        add_page_links(links, driver)

        fetch_more_links(driver, links)

        write_to_file(links)


def write_to_file(links) -> bool:
    file = os.path.join(BASE_DIR, 'data.json')
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception:
            file = os.path.join(BASE_DIR, 'alternate.json')

    with open('data.json', 'w') as fp:
        data = json.dumps(links, indent=4)
        fp.write(data)

    return True


def add_page_links(links: List[str], driver) -> None:
    linkset = driver.find_elements_by_css_selector("a.qi3t6e.XWbMGb")
    for link in linkset:
        url = link.get_attribute('href')
        links.append(url)


def fetch_more_links(driver, links) -> None:
    def next_page(driver):
        try:
            button = driver.find_element_by_css_selector(NEXT_BUTTON)
        except NoSuchElementException:
            button = None
        return button

    count = 1
    while next_page(driver):
        element = driver.find_element_by_css_selector(NEXT_BUTTON)
        WebDriverWait(driver, 10)
        element.click()

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, NEXT_BUTTON))
            )
            add_page_links(links, driver)
            count += 1
        except (
            NoSuchElementException,
            TimeoutException
        ):
            logger.exception(
                "An Exception occurred while fetching new hotels"
            )

        logger.info(f'FINISHED SCRAPING PAGE `{count}`')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        help="Link of website to parse",
        type=str)
    args = parser.parse_args()
    main(args.url)
