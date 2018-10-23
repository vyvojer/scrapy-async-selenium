import unittest

from scrapy import Spider
from scrapy.http import Response
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.signals import item_scraped

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrapy_async_selenium.http import SeleniumRequest


class ToScrapeSpider(Spider):
    name = "to_scrape"

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
        'LOG_LEVEL': 'DEBUG',
        'DOWNLOADER_MIDDLEWARES': {'scrapy_async_selenium.middlewares.AsyncSeleniumMiddleware': 3, },
        'SELENIUM_POOL_SIZE': 5,
    }

    def start_requests(self):
        url = "http://quotes.toscrape.com/js/page/{}/"
        for page in range(1, 11):
            yield SeleniumRequest(url=url.format(page), callback=self.parse)

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]/span[@class="text"]/text()').extract():
            yield {'quote': quote}


class PythonSpider(Spider):
    name = "python"

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {'scrapy_async_selenium.middlewares.AsyncSeleniumMiddleware': 3, },
        'SELENIUM_POOL_SIZE': 2,
    }

    def start_requests(self):
        url = 'https://www.python.org'
        yield SeleniumRequest(url=url, callback=self.parse, keep_driver=True)

    def search(self, webdriver: WebDriver, search: str):
        input = webdriver.find_element_by_xpath("//input[@id='id-search-field']")
        input.clear()
        input.send_keys(search)
        input.send_keys(Keys.RETURN)
        WebDriverWait(webdriver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Results')]")))

    def parse(self, response: Response):
        driver = response.meta['driver']
        yield {'title': response.xpath("//title/text()").extract_first()}
        yield SeleniumRequest(callback=self.parse_search,
                              driver_func=self.search,
                              driver_func_args=('python',),
                              driver=driver)

    def parse_search(self, response: Response):
        pass
        results = response.xpath('//ul[@class="list-recent-events menu"]/li/h3/text()').extract()
        for result in results:
            yield {'result': result}


class MiddlewareTest(unittest.TestCase):
    to_scrape_items = []
    python_title = []
    python_results = []

    @classmethod
    def setUpClass(cls):
        process = CrawlerProcess()
        crawler_to_scrape = Crawler(ToScrapeSpider)
        crawler_python = Crawler(PythonSpider)
        process.crawl(crawler_to_scrape)
        process.crawl(crawler_python)
        crawler_to_scrape.signals.connect(MiddlewareTest.add_quote, item_scraped)
        crawler_python.signals.connect(MiddlewareTest.add_python_item, item_scraped)
        process.start()

    @staticmethod
    def add_quote(item):
        MiddlewareTest.to_scrape_items.append(item)

    @staticmethod
    def add_python_item(item):
        if 'title' in item:
            MiddlewareTest.python_title.append(item)
        if 'result' in item:
            MiddlewareTest.python_results.append(item)

    def test_to_scrape(self):
        self.assertEqual(len(MiddlewareTest.to_scrape_items), 100)

    def test_python_title(self):
        self.assertEqual(self.python_title[0]['title'], "Welcome to Python.org")

    def test_python_results(self):
        self.assertGreater(len(self.python_results), 2)
        self.assertIn('Release – ', [r['result'] for r in self.python_results])
