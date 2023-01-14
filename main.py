from scraper_accenture_selenium import Scraper
import time
import datetime
import sqlite3

# interval to poll site
polling_period = 1

# connect to sqlite db
conn = sqlite3.connect('jobs.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS runs(start_run, end_run, jobs_extracted, status)')

# poll site every polling_period seconds
while True:
    try:
        start_run = datetime.datetime.now()
        print()
        print('Starting run, hit Ctrl + C to quit')
        print()
        scraper = Scraper(cur)
        jobs_extracted = scraper.scrape()
        status = ''
        if jobs_extracted > 0:
            print()
            print('Start Time :', start_run)
            print("Total jobs extracted :", jobs_extracted)
            status = 'success'
        else:
            print()
            print('Start Time :', start_run)
            print("Extraction Failed")
            status = 'failure'
        end_run = datetime.datetime.now()
        print('End Time :', end_run)
        print()
        cur.execute('INSERT INTO runs VALUES(?, ?, ?, ?)', (start_run, end_run, jobs_extracted, status))
        conn.commit()
        time.sleep(polling_period)
    except KeyboardInterrupt as err:
        print()
        print('Quitting....')
        print()
        # close connection to db
        conn.close()
        break
