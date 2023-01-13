from scraper import Selenium_Scraper
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import sqlite3
import time
import datetime
import requests
import sys
import re


class Scraper(Selenium_Scraper):

    def __init__(self, cursor):
        # call init of super class
        Selenium_Scraper.__init__(self)
        self.retry_period = 0
        self.thread_num = 2
        self.cur = cursor
        # create a table for jobs if does not exist
        create_table_statement = '''CREATE TABLE IF NOT EXISTS jobs(current_datetime, 
                                                                              job_link, 
                                                                              job_title, 
                                                                              job_description, 
                                                                              job_location_country, 
                                                                              job_location_city, 
                                                                              extraction_time)'''
        self.cur.execute(create_table_statement)
        self.url = 'https://www.accenture.com/in-en/careers/jobsearch'
        # jobs extracted
        self.jobs_extracted = 0


    def scrape_page(self, page_num, driver):
        url = self.url + "?jk=&sb=1&vw=0&is_rj=0&pg=" + str(page_num)
        driver.get(url)
        # check if no jobs message place holder is populated
        if driver.find_element(By.CLASS_NAME, 'cmp-jobs-results__no-jobs-message').text.strip() == '':
            start_time = time.time()
            job_list_class = "wrapper.teaser.dcc.dcc-job-card.has-tooltip.color-block-accent-purple-2.color-block-purple"
            # get html of job list
            content = driver.find_element(By.CLASS_NAME, job_list_class)
            content = content.get_attribute('innerHTML')
            # parse content
            jobs = self.parse_jobs(content, url, start_time)
            # check if jobs exist already in db
            for job in jobs:
                job_ext_time = job[-1]
                job_link = job[1]
                search_query = '''SELECT job_link FROM jobs WHERE job_link="{0}"'''.format(job_link)
                res = self.cur.execute(search_query)
                if res.fetchone() is None:
                    print()
                    print('Page :', page_num)
                    print('Time taken for extraction (seconds) :', job_ext_time)
                    print('Job Posting Link :',job_link)
                    print()
                    self.jobs_extracted += 1
                    # add job to sqlite db
                    self.cur.execute('INSERT INTO jobs VALUES(?, ?, ?, ?, ?, ?, ?)', job)
                    # check if jobs extracted reaches 1000
                    if self.jobs_extracted == 1000:
                        raise Exception('Jobs Limit Reached')
        else:
            raise Exception('No Jobs Found')


    def parse_jobs(self, content, url, start_time):
        # parse html of job list and get all job cards
        soup = BeautifulSoup(content, 'html.parser')
        content = soup.find_all('div', {'class': 'cmp-teaser card'})
        # measure time taken for extraction
        extraction_time = time.time() - start_time
        jobs = []
        # check if job data was found
        if len(content) > 0:
            for job in content:
                # extract data from job card
                job_title = job.find('h3').get_text()
                job_link = job.find('a')['href']
                job_description = job.find('span', {'class': 'description'}).get_text()
                job_location_country = job.find('div', {'class' : "cmp-teaser__pretitle cmp-teaser-region"}).get_text()
                job_location_city = job.find('div', {'class' : 'cmp-teaser__pretitle cmp-teaser-city'}).get_text()
                current_datetime = datetime.datetime.now()
                job_date_posted = job.find('p', {'class' : 'cmp-teaser__job-listing cmp-teaser__job-listing-posted-date'}).get_text()
                # check if job was posted more than 3 days ago
                job_date_posted = re.search(r'(\d+) (day|days) ago', job_date_posted)
                if bool(job_date_posted):
                    if int(job_date_posted.group(1)) > 3:
                        raise Exception('Jobs Limit Reached')
                job = (current_datetime, 
                        job_link, 
                        job_title,
                        job_description, 
                        job_location_country, 
                        job_location_city,
                        extraction_time)
                jobs.append(job)
            return jobs
        else:
            raise Exception('Job Extraction Failed For URL : ' + url)


    def scrape(self):
        driver = self.initialize_webdriver()
        logger = self.logger
        page_num = 1
        while True:
            try:
                self.scrape_page(page_num, driver)
                page_num += 1
            except Exception as err:
                print()
                print(str(err))
                print()
                logger.exception(str(err))
                if str(err) == 'No Jobs Found' or str(err) == 'Jobs Limit Reached':
                    break
                # incase of exception, populate logs and try again
                logger.info(str.format('Retrying in', self.retry_period, 'seconds....'))
                time.sleep(self.retry_period)
        # exit selenium webdriver
        driver.quit()
        # return jobs extracted
        return self.jobs_extracted
