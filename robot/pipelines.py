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
            self.client = psycopg2.connect(database="robot", 
                user="robot_koala", 
                password="robot_koala", 
                host="localhost", 
                port="5432")
        except:
            traceback.print_exc()

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        cur = self.client.cursor()
        try:
            cur.execute(
                    'insert into rb_content(title, content, source_author, source_uri, \
                    source_url, source, unique_id, category)values(%s, %s, %s, %s, %s, %s, %s, %s) ON \
                    CONFLICT (unique_id) do nothing', (item['title'], item['content'], \
                    item['author'], item['uri'], item['url'], 'tieba', item['post_id'], item['category']))
            self.client.commit()
        except:
            self.client.rollback()
            traceback.print_exc()
        cur.close()

        return item





