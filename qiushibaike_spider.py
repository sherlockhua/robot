#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from crawl.items import CrawlItem
import re

class QiuShiBaiKeSpider(BaseSpider):

    name = "QiuShiBaiKe"
    start_urls = [http://www.qiushibaike.com/]

    def parse(self, response):

        sel = Selector(response)
        items = []
        contents = sel.xpath('//div[@class="article"]')
        for content in contents:
            item = CrawlItem()
            item['content'] = content.xpath('//a/div/text()')
            print item['content']
            items.append(item) 
        

