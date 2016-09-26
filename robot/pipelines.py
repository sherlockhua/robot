# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import string
import json
import psycopg2

class RobotPipeline(object):

    def __ini__(self, pg_uri, pg_database):
        self.pg_uri = pg_uri
        self.pg_database = pg_database

    #def open_spider(self, spider):
    #    self.client = psycopg2.connect(database="robot_content", 
    #            user="robot_koala", 
    #            password="robot_koala", 
    #            host="localhost", 
    #            port="5432")

    #def close_spider(self, spider):
    #    self.client.close()

    def process_item(self, item, spider):
        if (string.atoi(item['commentCount']) > 60):
            print item
        return item





