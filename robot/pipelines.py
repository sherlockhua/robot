# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import string
import json
import psycopg2
import traceback

class RobotPipeline(object):

    def __ini__(self, pg_uri, pg_database):
        self.pg_uri = pg_uri
        self.pg_database = pg_database

    def open_spider(self, spider):
        try:
            self.client = psycopg2.connect(database="robot_content", 
                user="robot_koala", 
                password="robot_koala", 
                host="localhost", 
                port="5432")
        except:
            traceback.print_exc()

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if (string.atoi(item['comment_count']) < 60):
            return item

        cur = self.client.cursor()
        try:
            cur.execute(
                    'insert into rb_content(content, href, source, star_count, \
                    comment_count)values(%s, %s, %s, %s, %s)', (item['content'], \
                    item['href'], "qiushibaike", item['star_count'], item['comment_count']))
            self.client.commit()
        except:
            self.client.rollback()
            traceback.print_exc()
        cur.close()

        return item





