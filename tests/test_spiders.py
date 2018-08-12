import unittest

from scrapy import Spider
from scrapy_async_selenium.http import SeleniumRequest
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.signals import item_scraped


class TestSpider(Spider):
    name = "test"

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {'scrapy_async_selenium.middlewares.AsyncSeleniumMiddleware': 3, },
        'SELENIUM_POOL_SIZE': 8,
    }

    def start_requests(self):
        url = "http://quotes.toscrape.com/js/page/{}/"
        for page in range(1, 11):
            yield SeleniumRequest(url=url.format(page), callback=self.parse)

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]/span[@class="text"]/text()').extract():
            yield {'quote': quote}


class SpiderTest(unittest.TestCase):
    def setUp(self):
        self.items = []

    def add_quote(self, item):
        self.items.append(item)

    def test_spider(self):
        process = CrawlerProcess()
        crawler = Crawler(TestSpider)
        process.crawl(crawler)
        crawler.signals.connect(self.add_quote, item_scraped)
        process.start()
        self.assertEqual(len(self.items), 100)
