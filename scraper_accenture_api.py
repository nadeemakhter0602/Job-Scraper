from scraper import API_Scraper
import requests
import json
import time


class Scraper(API_Scraper):

    def __init__(self, cursor):
        API_Scraper.__init__(self)
        self.num_jobs = 1
        self.cur = cursor
        # create a table for jobs if does not exist
        create_table_statement = '''CREATE TABLE IF NOT EXISTS jobs(current_datetime, 
                                                                    job_link, 
                                                                    job_title, 
                                                                    job_description, 
                                                                    job_location_country, 
                                                                    job_location_city, 
                                                                    job_date_posted,
                                                                    extraction_time)'''
        self.cur.execute(create_table_statement)
        self.url = 'https://www.accenture.com/api/accenture/jobsearch/result'
        self.jobs_extracted = 0

    def set_headers(self):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundarydZBZYK0PATliNKCr",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "Referer": self.url,
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        return headers

    def set_body(self, num_jobs):
        data = "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data;" \
                + " name=\"f\"\r\n\r\n1\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data;"\
                + " name=\"s\"\r\n\r\n" \
                + str(num_jobs) \
                + "\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data;"\
                + " name=\"k\"\r\n\r\n\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; "\
                + "name=\"lang\"\r\n\r\nen\r\n------WebKitFormBoundarydZBZYK0PATliNKCr\r\n" \
                + "Content-Disposition: form-data; name=\"cs\"\r\n\r\nin-en\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; " \
                + "name=\"df\"\r\n\r\n[{\"metadatafieldname\":\"skill\",\"items\":[]}," \
                + "{\"metadatafieldname\":\"location\",\"items\":[]},{\"metadatafieldname\":\"postedDate\",\"items\":[]}," \
                + "{\"metadatafieldname\":\"travelPercentage\",\"items\":[]},{\"metadatafieldname\":\"jobTypeDescription\",\"items\":[]}," \
                + "{\"metadatafieldname\":\"businessArea\",\"items\":[]},{\"metadatafieldname\":\"specialization\",\"items\":[]}," \
                + "{\"metadatafieldname\":\"workforceEntity\",\"items\":[]},{\"metadatafieldname\":\"yearsOfExperience\",\"items\":[]}]" \
                + "\r\n------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"c\"\r\n\r\nIndia\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"sf\"\r\n\r\n2\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"syn\"\r\n\r\nfalse\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"isPk\"\r\n\r\nfalse\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"wordDistance\"\r\n\r\n0\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"userId\"\r\n\r\n\r\n" \
                + "------WebKitFormBoundarydZBZYK0PATliNKCr\r\nContent-Disposition: form-data; name=\"componentId\"\r\n\r\n" \
                + "careerjobsearchresults-6e7bb92edd\r\n------WebKitFormBoundarydZBZYK0PATliNKCr--\r\n"
        return data

    def make_api_request(self):
        headers = self.set_headers()
        data = self.set_body(self.num_jobs)
        response = requests.post(self.url, headers=headers, data=data)
        data = json.loads(response.content.decode())
        print("Total number of jobs postings :", data['total'])
        self.num_jobs = data['total']
        data = self.set_body(self.num_jobs)
        start_time = time.time()
        response = requests.post(self.url, headers=headers, data=data)
        data = json.loads(response.content.decode())
        extraction_time = time.time() - start_time
        for job in data['documents']:
            current_datetime = time.time()
            job_link = job['jobDetailUrl']
            job_title = job['title']
            job_date_posted = job['postedDate']
            job_description = job['jobDescription']
            job_country = job['country']
            job_city = job['location'].pop()
            job = (current_datetime, 
                    job_link, 
                    job_title,
                    job_description, 
                    job_location_country, 
                    job_location_city,
                    job_date_posted,
                    extraction_time)
            search_query = '''SELECT job_link FROM jobs WHERE job_link="{0}" AND job_date_posted IS NULL'''.format(job_link)
            res = self.cur.execute(search_query)
            if res.fetchone() is None:
                self.jobs_extracted += 1
                print()
                print('Job No.', self.jobs_extracted)
                print('Time taken for extraction (seconds) :', extraction_time)
                print('Job Title :', job_title)
                print('City :', job_city)
                print('Country :', job_country)
                print('Job Posting Link :', job_link)
                print()
                # add job to sqlite db
                self.cur.execute('INSERT INTO jobs VALUES(?, ?, ?, ?, ?, ?, ?, ?)', job)
