# 项目内部库
from boss_job.utils import select_data
from boss_job.utils import changeMs

# 第三方库
from scrapy.conf import settings
import hashlib
import pymongo
import re
import requests
from lxml import etree

# Python内置库
from retrying import retry
from urllib import parse
import schedule
from multiprocessing import Pool


class IncrementSpider(object):
    def __init__(self):
        self.key = parse.quote('大数据')
        self.start_url = 'https://www.zhipin.com/c{}/?query={}&page={}'
        self.header_url = 'https://www.zhipin.com'
        self.ip_url = ""
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.client.admin.authenticate(settings['MONGO_USER'], settings['MONGO_PSW'])
        self.BossJob = self.client[settings['MONGO_DB']]
        self.BossJobData = self.BossJob[settings['MONGO_COLL']]

    def req(self, url, ip):
        response = requests.get(url, proxies=id)
        return response

    def search_next_page(self, response, ip):
        selector = etree.HTML(response.text)
        if selector.xpath('//a[@class="next"]/@href'):
            next_url = self.header_url + selector.xpath('//a[@class="next"]/@href')[0]
            response = self.req(url=next_url, ip=ip)
            return response

    def get_info_url(self, response):
        selector = etree.HTML(response.text)
        page_url = selector.xpath('//div[@class="info-primary"]/h3/a/@href')
        return page_url

    def get_info(self, response):
        selector = etree.HTML(response.text)
        item = {}
        salary = selector.xpath('string(//span[@class="badge"])').split('-')
        location = selector.xpath('//div[@class="info-primary"]/p/text()')[0].replace('城市：', '')
        date = selector.xpath('string(//span[@class="time"])').replace('发布于', '')
        work_experience = selector.xpath('//div[@class="info-primary"]/p/text()')[1].replace('经验：', '')
        limit_degree = selector.xpath('//div[@class="info-primary"]/p/text()')[2].replace('学历：', '')
        people_count = ''
        career_type = selector.xpath('string(//div[@class="name"]/h1[1])')
        work_info_content = re.sub('\s+', '', selector.xpath('string(//div[@class="job-sec"]/div)')).strip()
        work_info_url = response.url
        business_name = selector.xpath('string(//h3[@class="name"]/a)')
        business_type = ''
        business_website = selector.xpath('string(//div[@class="info-company"]/p[2])').strip()
        business_industry = selector.xpath('string(//div[@class="info-company"]/p[1]/a)').strip()
        business_location = re.sub('\s+', '', selector.xpath('string(//div[@class="location-address"])')).strip()
        business_info = re.sub('\s+', '', selector.xpath('string(//div[@class="job-sec company-info"]/div)')).strip()
        # noinspection PyBroadException
        try:
            business_count = re.search(
                '(\d+)人以上', selector.xpath('string(//div[@class="info-company"]/p[1])')).group(0)
        except:
            business_count = re.search(
                '(\d+)-(\d+)人', selector.xpath('string(//div[@class="info-company"]/p[1])')).group(0)
        if len(salary) == 2:
            min_salary = salary[0]
            max_salary = salary[1]
        else:
            min_salary = salary[0]
            max_salary = salary[0]
        publish_date = changeMs.change_ms(date)
        try:
            if re.findall('职责：(.*?)要求', work_info_content):
                work_duty = re.findall('职责：(.*?)要求', work_info_content)[0][:-2]
                work_need = re.findall('要求：(.*?)', work_info_content)[0]
                if work_duty == '':
                    work_duty_content = work_info_content
                else:
                    work_duty_content = ''
            else:
                work_duty = re.findall('职责：(.*?)', work_info_content)[0]
                work_need = ''
                if work_duty == '':
                    work_duty_content = work_info_content
                else:
                    work_duty_content = ''
        except Exception as err:
            print(err)
            work_duty = ''
            work_need = ''
            work_duty_content = work_info_content
        string = career_type + business_name
        item['_id'] = hashlib.md5(string.encode('utf-8')).hexdigest()
        item['from_website'] = "boss_直聘"
        item['min_salary'] = min_salary
        item['max_salary'] = max_salary
        item['location'] = location
        item['work_experience'] = work_experience
        item['limit_degree'] = limit_degree
        item['people_count'] = people_count
        item['publish_date'] = publish_date
        item['career_type'] = career_type
        item['work_duty'] = work_duty
        item['work_need'] = work_need
        item['work_duty_content'] = work_duty_content
        item['work_info_url'] = work_info_url
        item['work_type'] = '全职'
        item['business_name'] = business_name
        item['business_type'] = business_type
        item['business_count'] = business_count
        item['business_industry'] = business_industry
        item['business_location'] = business_location
        item['business_info'] = business_info
        if len(business_website) == 1:
            item['business_website'] = business_website[0]
        else:
            item['business_website'] = ''
        self.BossJobData.insert(item)

    @retry(wait_exponential_max=5)
    def get_ip(self, ip_url):
        ip = 'http://' + requests.get(url=ip_url).content.decode()
        return ip

    def main(self):
        data = select_data.parse()
        for i in data:
            area = i['city']
            ip = self.get_ip(ip_url=self.ip_url)
            page_response = self.req(url=self.start_url.format(area, self.key, 1), ip=ip)
            page_url = self.get_info_url(response=page_response)
            for purl in page_url:
                info_response = self.req(url=purl, ip=ip)
                self.get_info(response=info_response)
            while True:
                next_page_res = self.search_next_page(response=page_response, ip=ip)
                self.get_info(response=next_page_res)

increment_spider = IncrementSpider()
schedule.every(1).days.do(increment_spider)
