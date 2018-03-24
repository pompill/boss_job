# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class BossJobPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.client.admin.authenticate(settings['MONGO_USER'], settings['MONGO_PSW'])
        self.BossJob = self.client[settings['MONGO_DB']]
        self.BossJobData = self.BossJob[settings['MONGO_COLL']]
        pass

    def process_item(self, item, spider):
        self.BossJobData.insert_one(item)
        return item

    def close_spider(self, spider):
        pass
