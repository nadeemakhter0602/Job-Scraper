from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging


class Selenium_Scraper:
    def __init__(self):
        # configure log file
        logging.basicConfig(filename="selenium_scraper.log",
                            format='%(asctime)s %(message)s',
                            filemode='a')
        # create log object
        self.logger = logging.getLogger()
        # setting threshold
        self.logger.setLevel(logging.INFO)

    def initialize_webdriver(self):
        # run chromium webdriver in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', 
                                               ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)
        return driver
