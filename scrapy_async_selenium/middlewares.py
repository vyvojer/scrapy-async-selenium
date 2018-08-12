from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes
from scrapy import signals

from selenium import webdriver

from .http import SeleniumRequest
from .drivers import DriverPool


class AsyncSeleniumMiddleware:
    def __init__(self, drivers_number: int):
        self.driver_pool = DriverPool(drivers_number)

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        drivers_number = crawler.settings.getint("SELENIUM_POOL_SIZE", 1)
        middleware = cls(drivers_number)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request: SeleniumRequest, spider):
        try:
            request.is_selenium
        except AttributeError:
            return None

        return self.driver_pool.deferred_response(request)

    def spider_closed(self, spider):
        self.driver_pool.close()
