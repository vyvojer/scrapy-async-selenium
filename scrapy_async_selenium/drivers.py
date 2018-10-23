import logging

from selenium import webdriver

from scrapy.utils.python import to_bytes
from scrapy.http import HtmlResponse

from twisted.internet.threads import deferToThreadPool
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .http import SeleniumRequest


logger = logging.getLogger(__name__)


class Driver:
    def __init__(self, pool: 'DriverPool' = None):
        self.web_driver = webdriver.Firefox()
        self._blocked = False
        self.pool = pool

    @property
    def blocked(self):
        return self._blocked

    def block(self):
        self._blocked = True

    def unblock(self):
        self._blocked = False
        self.pool.update(self)


class DriverPool:
    def __init__(self, size=1):
        self.size = size
        self.drivers = []
        self._waiting = []

    def append_driver(self):
        driver = Driver(pool=self)
        self.drivers.append(driver)
        return driver

    def close(self):
        for driver in self.drivers:
            driver.web_driver.close()

    def update(self, driver):
        """ Listener callback for DriverItem"""
        if self._waiting:
            free_driver = self._waiting.pop()
            free_driver.callback(driver)
            logger.info('Free deferred from waiting, len = %s', len(self._waiting))

    def get_driver(self, keeped_driver=None):
        if keeped_driver is not None:
            free_driver = Deferred()
            free_driver.callback(keeped_driver)
            return free_driver
        free_driver = Deferred()
        free_drivers = [driver for driver in self.drivers if not driver.blocked]
        if free_drivers:
            free_driver.callback(free_drivers[0])
            logger.info("Free driver found")
        elif len(self.drivers) < self.size:
            driver = self.append_driver()
            logger.info("Free driver not found. New driver appended")
            free_driver.callback(driver)
        else:
            logger.info("Free driver not found. Waiting for ....")
            self._waiting.append(free_driver)
            logger.info('Append deferred tor waiting, len = %s', len(self._waiting))
        return free_driver

    @staticmethod
    def _get_url(driver: Driver, request: SeleniumRequest) -> HtmlResponse:
        web_driver = driver.web_driver
        if request.driver is None:
            web_driver.get(request.url)
        if request.driver_func is not None:
            request.driver_func(web_driver,
                                *request.driver_func_args,
                                **request.driver_func_kwargs)
        body = to_bytes(web_driver.page_source)  # body must be of type bytes
        response = HtmlResponse(web_driver.current_url, body=body, encoding='utf-8', request=request)
        response.meta['driver'] = driver
        return response

    @staticmethod
    def _response(driver: Driver, request: SeleniumRequest) -> Deferred:
        driver.block()
        deferred = deferToThreadPool(reactor, reactor.getThreadPool(), DriverPool._get_url, driver, request)
        return deferred

    @staticmethod
    def _unblock(response: HtmlResponse):
        driver = response.meta['driver']
        if not response.request.keep_driver:
            driver.unblock()
            response.meta['driver'] = None
        return response

    def get_response(self, request: SeleniumRequest) -> Deferred:
        driver = self.get_driver(request.driver)
        response = driver.addCallback(self._response, request).addCallback(self._unblock)
        return response




