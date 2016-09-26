#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from robot.items import RobotItem
import re

class QiuShiBaiKeSpider(BaseSpider):

    name = "Tieba"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = ["http://tieba.baidu.com/f?kw=%E7%AC%91%E8%AF%9D&ie=utf-8"] 
    host = "http://tieba.baidu.com"

    def parse(self, response):

        sel = Selector(response)
        thread_list = sel.xpath('//ul[@id="thread_list"]/li')
        print thread_list
        for thread in thread_list:
            print thread
