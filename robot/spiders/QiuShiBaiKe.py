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
            item = RobotItem()
            result = content.xpath('.//a/div/span/text()').extract()
            item['content'] = result[0]
            item['voteCount'] = content.xpath('.//div[@class="stats"]/span[@class="stats-vote"]/i/text()').extract()[0]
            item['link'] = content.xpath('.//a[@class="contentHerf"]/@href').extract()[0]
            item['commentCount'] = content.xpath('.//div[@class="stats"]/span[@class="stats-comments"]/a/i/text()').extract()[0]
            items.append(item)

        return items
