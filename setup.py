from setuptools import setup

setup(name='scrapy-session-proxies',
      version='0.0.1',
      description='Scrapy async selenium middleware',
      url='https://github.com/vyvojer/scrapy-async-selenium',
      author='Alexey Londkevich',
      author_email='vyvojer@gmail.com',
      license='MIT',
      packages=['scrapy_session_proxies'],
      install_requires=['scrapy', 'selenium'],
      zip_safe=False)
