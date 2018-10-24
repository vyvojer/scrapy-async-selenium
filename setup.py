from setuptools import setup

setup(name='scrapy-session-proxies',
      version='0.0.2',
      description='Scrapy async selenium middleware',
      url='https://github.com/vyvojer/scrapy-async-selenium',
      author='Alexey Londkevich',
      author_email='vyvojer@gmail.com',
      license='MIT',
      packages=['scrapy_async_selenium'],
      install_requires=['scrapy', 'selenium'],
      zip_safe=False)
