# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RobotItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    comment_count = scrapy.Field()
    star_count = scrapy.Field()
    content = scrapy.Field()
    href = scrapy.Field()
    pic = scrapy.Field()
    
class TiebaItem(scrapy.Item):
    content = scrapy.Field()
    uri = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    post_id = scrapy.Field()
    category = scrapy.Field()
