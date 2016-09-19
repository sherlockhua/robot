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

    name = "QiuShiBaiKe"
    allowed_domains = ["www.qiushibaike.com"]
    start_urls = ["http://www.qiushibaike.com/hot/"]

    def parse(self, response):

        sel = Selector(response)
        items = []
        contents = sel.xpath('//div[@class="article block untagged mb15"]')
        for content in contents:
            print 'ok'
            item = RobotItem()
            item['content'] = content.xpath('//a/div/text()')
            print item['content']
            items.append(item)

