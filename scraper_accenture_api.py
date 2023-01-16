from scraper import API_Scraper
import requests
import json
import time


class Scraper(API_Scraper):
    def __init__(self):
        API_Scraper.__init__(self)
        self.num_jobs = 1

    def set_headers(self):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundarydZBZYK0PATliNKCr",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "Referer": "https://www.accenture.com/in-en/careers/jobsearch",
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
        response = requests.post('https://www.accenture.com/api/accenture/jobsearch/result', headers=headers, data=data)
        data = json.loads(response.content.decode())
        print("Total number of jobs postings :", data['total'])
        self.num_jobs = data['total']
        data = self.set_body(self.num_jobs)
        start_time = time().time()
        response = requests.post('https://www.accenture.com/api/accenture/jobsearch/result', headers=headers, data=data)
        data = json.loads(response.content.decode())
        extraction_time = time().time() - start_time
        i = 1
        for job in data['documents']:
            current_datetime = time.time()
            job_link = job['jobDetailUrl']
            job_title = job['title']
            job_date_posted = job['postedDate']
            job_description = job['jobDescription']
            job_country = job['country']
            job_city = job['location'].pop()
            print()
            print('Job No.', i)
            print('Time taken for extraction (seconds) :', extraction_time)
            print('Job Title :', job_title)
            print('City :', job_city)
            print('Country :', job_country)
            print('Job Posting Link :', job_link)
            print()
            i += 1

if __name__ == '__main__':
    scraper = Scraper()
    scraper.make_api_request()
