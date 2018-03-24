# -*- coding:utf-8 -*-

# Python内置库
from urllib import parse

# 第三方库
import scrapy
from scrapy.spiders import Spider
from lxml import etree
import re
import hashlib

# 项目内部库
from boss_job.items import BossJobItem
from boss_job.utils import changeMs
from boss_job.utils import select_data
from boss_job.settings import *


class BossJobSpider(Spider):
    name = 'boss_job'
    key = parse.quote('大数据')
    start_url = ['https://www.zhipin.com/c{}/?query={}&page={}']
    header_url = 'https://www.zhipin.com'
    page = '{}'
    header = {'user-agent': random.choice(USER_AGENTS)}

    def start_requests(self):
        data = select_data.parse()
        for i in data:
            area = i['city']
            yield scrapy.Request(url=self.start_url[0].format(area, self.key, 1), callback=self.parse)

    def parse(self, response):
        info_url = self.get_info_url(response=response)
        print(info_url)
        for i in info_url:
            i_url = self.header_url + i
            print(i_url)
            yield scrapy.Request(response.urljoin(i_url), callback=self.get_info, meta={'url': i_url})
        selector = etree.HTML(response.body)
        if selector.xpath('//a[@class="next"]/@href'):
            next_url = self.header_url + selector.xpath('//a[@class="next"]/@href')[0]
            print(next_url)
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

    @staticmethod
    def get_info_url(response):
        selector = etree.HTML(response.body)
        page_url = selector.xpath('//div[@class="info-primary"]/h3/a/@href')
        return page_url

    @staticmethod
    def get_info(response):
        html = response.body
        selector = etree.HTML(html)
        item = BossJobItem()
        salary = selector.xpath('string(//span[@class="badge"])').split('-')
        location = selector.xpath('//div[@class="info-primary"]/p/text()')[0].replace('城市：', '')
        date = selector.xpath('string(//span[@class="time"])').replace('发布于', '')
        work_experience = selector.xpath('//div[@class="info-primary"]/p/text()')[1].replace('经验：', '')
        limit_degree = selector.xpath('//div[@class="info-primary"]/p/text()')[2].replace('学历：', '')
        people_count = ''
        career_type = selector.xpath('string(//div[@class="name"]/h1[1])')
        work_info_content = re.sub('\s+', '', selector.xpath('string(//div[@class="job-sec"]/div)')).strip()
        work_info_url = response.meta['url']
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
        yield item
