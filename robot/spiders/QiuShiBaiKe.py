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
    start_urls = ["http://www.qiushibaike.com/history/", 
            "http://www.qiushibaike.com/", 
            "http://www.qiushibaike.com/hot/", 
            "http://www.qiushibaike.com/imgrank/", 
            "http://www.qiushibaike.com/text/"]

    host = "http://www.qiushibaike.com"

    def parse(self, response):

        sel = Selector(response)
        contents = sel.xpath('//div[@class="article block untagged mb15"]')
        for content in contents:
            item = RobotItem()
            result = content.xpath('.//a/div/span/text()').extract()
            if result:
                item['content'] = result[0]

            pic = content.xpath('.//div[@class="thumb"]/a/img/@src').extract()
            if pic:
                item["pic"] = pic[0]

            star = content.xpath('.//div[@class="stats"]/span[@class="stats-vote"]/i/text()').extract()
            if star:
                item['star_count'] = star[0]

            link = content.xpath('.//a[@class="contentHerf"]/@href').extract()
            if link:
                item['href'] = link[0]

            count = content.xpath('.//div[@class="stats"]/span[@class="stats-comments"]/a/i/text()').extract()
            if count:
                item['comment_count'] = count[0]

            yield item

        sellink = Selector(response)
        pages = sellink.xpath('//ul[@class="pagination"]/li')
        for page in pages:
            link = page.xpath('.//a/@href').extract()
            if link:
                yield Request(self.host + link[0], callback=self.parse)

        next_day = sellink.xpath('//div[@class="history-nv mb15 clearfix"]/a/@href').extract()
        if next_day:
            yield Request(self.host + next_day[0], callback=self.parse)
