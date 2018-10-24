from scrapy import Request


class SeleniumRequest(Request):

    def __init__(self,
                 driver_func: callable = None,
                 driver_func_args: tuple = (),
                 driver_func_kwargs: dict = {},
                 driver=None,
                 keep_driver=False, *args, **kwargs):
        """
        SeleniumRequest constructor

        You can send some function, that will be running after page loading.
        The function must have one required parameter of the selenium.webdriver.remote.webdriver.WebDriver type.
        Also you can send optional args and kwargs to the function

        Args:
            driver_func(callable): function, that will be running after page loading
            driver_func_args(tuple): Tuple of args
            driver_func_kwargs(dict): Dict of kwargs
            driver(http.Driver): use kept driver (see keep_driver)
            keep_driver(bool): don't unblock driver after using. Driver will be keeped as meta['driver']. Use with caution
            *args:
            **kwargs:
        """
        self.is_selenium = True
        self.driver_func = driver_func
        self.driver_func_args = driver_func_args
        self.driver_func_kwargs = driver_func_kwargs
        self.driver = driver
        self.keep_driver = keep_driver
        if driver is not None:
            kwargs['url'] = driver.web_driver.current_url
            kwargs['dont_filter'] = True
        super().__init__(*args, **kwargs)
