import logging

from selenium import webdriver

from scrapy.utils.python import to_bytes
from scrapy.http import HtmlResponse

from twisted.internet.threads import deferToThreadPool
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .http import SeleniumRequest


logger = logging.getLogger(__name__)


class DriverItem:
    def __init__(self):
#        profile = webdriver.FirefoxProfile()
#        profile.set_preference("permissions.default.image", 3)
#        self.driver = webdriver.Firefox(firefox_profile=profile)
        self.driver = webdriver.Firefox()
        self.busy = False


class DriverPool:
    def __init__(self, size=1):
        self.size = size
        self.drivers = []

    def append_driver(self):
        driver_item = DriverItem()
        self.drivers.append(driver_item)
        return driver_item

    def close(self):
        for item in self.drivers:
            item.driver.close()

    @staticmethod
    def sleep(secs):
        deferred = Deferred()
        reactor.callLater(secs, deferred.callback, None)
        return deferred

    def _get_free_driver(self) -> DriverItem:
        free_drivers = [item for item in self.drivers if not item.busy]
        if free_drivers:
            return free_drivers[0]
        elif len(self.drivers) < self.size:
            driver_item = self.append_driver()
            return driver_item
        else:
            logger.info("No free driver in the pool. Waiting...")
            self.sleep(0.001)
            return self._get_free_driver()

    @staticmethod
    def _get_url(driver_item: DriverItem, request: SeleniumRequest) -> HtmlResponse:
        driver = driver_item.driver
        if request.driver_id is None:
            driver.get(request.url)
        if request.before_response is not None:
            request.before_response(driver)
        body = to_bytes(driver.page_source)  # body must be of type bytes
        driver_item.busy = False
        return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)

    def deferred_response(self, request: SeleniumRequest):
        if request.driver_id is None:
            driver_item = self._get_free_driver()
        else:
            try:
                driver_item = self.drivers[request.driver_id]
            except IndexError:
                raise ValueError("Driver num {} doesn't exist".format(request.driver_id))
        driver_item.busy = True
        deferred = deferToThreadPool(reactor, reactor.getThreadPool(), self._get_url, driver_item, request)
        return deferred





