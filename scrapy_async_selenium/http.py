from scrapy import Request


class SeleniumRequest(Request):

    def __init__(self,
                 driver_func: callable = None,
                 driver_func_args: tuple = (),
                 driver_func_kwargs: dict = {},
                 driver=None,
                 keep_driver=False, *args, **kwargs):
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
