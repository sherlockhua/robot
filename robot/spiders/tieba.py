#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from robot.items import TiebaItem
from urlparse import urlparse
import re
import string

class TiebaSpider(BaseSpider):

    name = "Tieba"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = ["http://tieba.baidu.com/f?kw=%E7%AC%91%E8%AF%9D&ie=utf-8"] 
    host = "http://tieba.baidu.com"
    __max_reply_num = 100
    __min_post_word_count = 16*3

    def parse(self, response):

        sel = Selector(response)
        thread_list = sel.xpath('//li[@class=" j_thread_list clearfix"]')

        for thread in thread_list:
            link, need_crawl = self.parse_thread(thread)
            if (need_crawl == False or len(link) == 0):
                continue

            yield Request(link, callback = self.parse_post_list)

        page_list = sel.xpath('//div[@id="frs_list_pager"]/a/@href').extract()
        for page_link in page_list:
            if (len(page_link) == 0):
                continue
            yield Request(page_link, callback = self.parse)



    def parse_thread(self, thread):

        reply_list = thread.xpath('.//div/div/span[@class="threadlist_rep_num center_text"]/text()').extract()
        if len(reply_list) == 0:
            return "", False

        reply_num = string.atoi(reply_list[0])
        if (reply_num < self.__max_reply_num):
            return "", False

        link_list = thread.xpath('.//div/div/div/div/a[@class="j_th_tit "]/@href').extract()
        if (len(link_list) == 0):
            return "", False

        link = link_list[0]
        return self.host+link, True

    def parse_post_title(self, sel):
        title_list = sel.xpath('//h3[@class="core_title_txt pull-left text-overflow  "]/@title').extract()
        if (len(title_list) <= 0):
            return ""
        title = title_list[0]
        return title

    def parse_post_uri(self, url):
        result = urlparse(url)
        return result.scheme + "://" + result.netloc + result.path

    def parse_post_list(self, response):

        sel = Selector(response)
        url = response.url
        uri = self.parse_post_uri(url)
        title = self.parse_post_title(sel)

        post_list = sel.xpath('//div[@class="l_post l_post_bright j_l_post clearfix  "]')
        for post in post_list:
            author, content, post_id, ok = self.parse_post(post)
            if ok == False:
                continue
            item = TiebaItem()
            item['content'] = content
            item['url'] = url
            item['author'] = author
            item['title'] = title
            item['uri'] = uri
            item['post_id'] = self.Name + '.' + post_id
            yield item

        page_list = sel.xpath('//li[@class="l_pager pager_theme_5 pb_list_pager"]/a/@href').extract()
        for page_link in page_list:
            if (len(page_link) == 0):
                continue
            yield Request(self.host+page_link, callback = self.parse_post_list)

    def parse_post(self, post):
        author_wrap = post.xpath('.//div/div[@class="louzhubiaoshi_wrap"]')
        if (len(author_wrap) == 0):
            return "", "", "", False
        author_list = author_wrap.xpath('.//div/@author').extract()
        if (len(author_list) == 0):
            return "", "", "", False

        author = author_list[0]
        content, post_id, ok = self.parse_post_content(post)
        if ok == False:
            return "", "", "", False

        print "--------------post_id:%s-----------" % post_id
        return author, content, post_id, True

    def parse_post_content(self, post):

        content_list = post.xpath('.//div/div/cc/div/div[@class="post_bubble_middle"]')
        if (len(content_list) == 0):
            content_list = post.xpath('.//div/div/cc/div[@class="d_post_content j_d_post_content "]')
        if (len(content_list) == 0):
            return "", "", False

        text_list = content_list.xpath('string(.)').extract()
        if (len(text_list) <= 0 or len(text_list[0]) < self.__min_post_word_count):
            return  "", "", False

        post_id_list = content_list.xpath('.//@id').extract()
        if (len(post_id_list) <= 0):
            print "ERROR------------------------WARN"
            return "", "", False

        return text_list[0], post_id_list[0], True



