from scrapy import Request


class SeleniumRequest(Request):

    def __init__(self,
                 before_response: callable = None,
                 driver_id: int = None,
                 keep_response=False, *args, **kwargs):
        self.is_selenium = True
        self.before_response = before_response
        self.driver_id = driver_id
        self.keep_response = keep_response
        super().__init__(*args, **kwargs)
