# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import string
import json
import psycopg2
import os
import traceback
import cookielib
import urllib2
import oss2
import random
from hashlib import md5  

class RobotPipeline(object):

    def __ini__(self, pg_uri, pg_database):
        self.pg_uri = pg_uri
        self.pg_database = pg_database

    def open_spider(self, spider):
        try:
            self.auth = oss2.Auth('xxx', 'xxx')
            #self.service = oss2.Service(self.auth, 'http://oss-cn-shanghai-internal.aliyuncs.com')
            self.bucket = oss2.Bucket(self.auth, 'http://oss-cn-shanghai-internal.aliyuncs.com',
                    'xxx')

            self.client = psycopg2.connect(database="robot", 
                user="robot_koala", 
                password="robot_koala", 
                host="localhost", 
                port="5432")
        except:
            traceback.print_exc()

    def close_spider(self, spider):
        self.client.close()

    def  get_filename(self, origin_filename):
        ext = os.path.splitext(origin_filename)
        m = md5()
        m.update(ext[0] + unichr(random.randint(0,255)))
        return m.hexdigest() + ext[1]

    def process_item(self, item, spider):

        cur = self.client.cursor()
        try:
            for node in item['content']:
                if (node['type'] == 'pic'):
                    cj = cookielib.LWPCookieJar()
                    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                    urllib2.install_opener(opener)

                    conn = urllib2.Request(node['data'])
                    operate=opener.open(conn)
                    data = operate.read()
                    filename = os.path.basename(node['data'])
                    filename_new = self.get_filename(filename)
                    result = self.bucket.put_object(filename_new, data)

                    operate.close()
                    if result.status != 200:
                        return item
                    node['data'] = "http://408772ac8ffe66e91ca44b0f90f52963.oss-cn-shanghai.aliyuncs.com/" \
                            + filename_new
                    continue

            content = json.dumps(item['content'])
            thread_type = 'Text'
            if item['has_image'] == True:
                thread_type = 'Pic'
            cur.execute(
                    'insert into rb_content(title, content, source_author, source_uri, \
                    source_url, source, unique_id, category, thread_type)values(%s, %s, %s,\
                    %s, %s, %s, %s, %s, %s) ON CONFLICT (unique_id) do nothing', \
                    (item['title'], content, item['author'], item['uri'], item['url'],\
                    'tieba', item['post_id'], item['category'], thread_type))
            self.client.commit()
        except:
            self.client.rollback()
            traceback.print_exc()
        cur.close()

        return item





