Async Selenium middleware for Scrapy
=====================================

Middleware allows to async use multiple Selenium instance with Scrapy

## Install

    git clone git@github.com:vyvojer/scrapy-async-selenium.git
    cd scrapy-async-selenium
    python setup.py install --user
    
## Using

### settings.py

    DOWNLOADER_MIDDLEWARES = {
        'scrapy_async_selenium.middlewares.AsyncSeleniumMiddleware': 3, 
    }
    
    # Maximum number of selenium instances
    SELENIUM_POOL_SIZE = 5

    
### SeleniumRequest

    def start_requests(self):
        url = "http://quotes.toscrape.com/js/page/{}/"
        for page in range(1, 11):
            yield SeleniumRequest(url=url.format(page), callback=self.parse)
            
#### Interacting with page

You can send some function, that will be running after page loading. 
The function must have one required parameter of the **selenium.webdriver.remote.webdriver.WebDriver** type.

Send the function as **driver_func** parameter of **SeleniumRequest**. 
Send args and kwargs for the function as **driver_func_args** and **driver_func_kwargs** of **SeleniumRequest**.

    # Fill search field of 'python.org', press 'Enter', wait for results
    def search(self, webdriver: WebDriver, search: str):
        input = webdriver.find_element_by_xpath("//input[@id='id-search-field']")
        input.clear()
        input.send_keys(search)
        input.send_keys(Keys.RETURN)
        WebDriverWait(webdriver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Results')]")))
            
    # Open 'python.org' with self.search function
    def start_requests(self):
        url = 'https://www.python.org'
                yield SeleniumRequest(callback=self.parse_search,
                              driver_func=self.search,
                              driver_func_args=('python',))

        