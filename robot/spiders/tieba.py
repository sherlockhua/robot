#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from robot.items import TiebaItem
from urlparse import urlparse
from scrapy import log
import re
import string

class TiebaSpider(BaseSpider):

    name = "Tieba"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = ["http://tieba.baidu.com/f?kw=%E7%AC%91%E8%AF%9D&ie=utf-8",                #笑话吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E6%81%90%E6%80%96",                      #恐怖吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E6%8E%A8%E7%90%86",                      #推理吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E6%90%9E%E7%AC%91",                      #搞笑吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E6%90%9E%E7%AC%91%E5%9B%BE%E7%89%87",    #搞笑图片吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E5%86%85%E6%B6%B5%E5%9B%BE",             #内涵图吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E5%86%85%E6%B6%B5%E6%AE%B5%E5%AD%90",    #内涵段子吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E5%86%85%E6%B6%B5%E7%AC%91%E8%AF%9D",    #内涵笑话吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E5%86%85%E6%B6%B5",                      #内涵吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E6%BC%82%E4%BA%AE%E5%A5%B3%E4%BA%BA"     #漂亮女人吧
            "http://tieba.baidu.com/f?ie=utf-8&kw=%E8%82%B2%E5%84%BF"                       #育儿吧
            ] 
    host = "http://tieba.baidu.com"
    __min_reply_num = 512
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
        if (reply_num < self.__min_reply_num):
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

    def parse_post_category(self, sel):
        category_list = sel.xpath('//a[@class="card_title_fname"]/text()').extract()
        if (len(category_list) <= 0):
            return ""
        category = category_list[0]
        tmp = category.strip('吧')
        return tmp

    def parse_post_list(self, response):

        sel = Selector(response)
        url = response.url
        uri = self.parse_post_uri(url)
        title = self.parse_post_title(sel)
        category = self.parse_post_category(sel)

        post_list = sel.xpath('//div[@class="l_post l_post_bright j_l_post clearfix  "]')
        for post in post_list:
            author, content, post_id, has_image, ok = self.parse_post(post)
            if ok == False:
                continue
            item = TiebaItem()
            item['content'] = content
            item['url'] = url
            item['author'] = author
            item['title'] = title
            item['uri'] = uri
            item['post_id'] = self.name + '.' + post_id
            item['category'] = category
            item['has_image'] = has_image
            yield item

        page_list = sel.xpath('//li[@class="l_pager pager_theme_5 pb_list_pager"]/a/@href').extract()
        for page_link in page_list:
            if (len(page_link) == 0):
                continue
            yield Request(self.host+page_link, callback = self.parse_post_list)

    def parse_post(self, post):
        has_image = False
        author_wrap = post.xpath('.//div/div[@class="louzhubiaoshi_wrap"]')
        if (len(author_wrap) == 0):
            return "", "", "", has_image, False
        author_list = author_wrap.xpath('.//div/@author').extract()
        if (len(author_list) == 0):
            return "", "", "", has_image, False

        author = author_list[0]
        content, post_id, has_image, ok = self.parse_post_content(post)
        if ok == False:
            return "", "", "", has_image, False

        return author, content, post_id, has_image, True

    def parse_post_content(self, post):

        has_image = False
        content_list = post.xpath('.//div/div/cc/div/div[@class="post_bubble_middle"]')
        if (len(content_list) == 0):
            content_list = post.xpath('.//div/div/cc/div[@class="d_post_content j_d_post_content "]')
        if (len(content_list) == 0):
            return "", "", has_image, False

        node_list = content_list.xpath('./node()')
        if (len(node_list) <= 0):
            return  "", "", has_image, False

        content = []
        last_node_type=0
        for node in node_list:
            node_name = node.xpath('name()').extract()
            if (len(node_name) == 0):
                text = node.extract().strip()
                if (len(text) ==0):
                    continue
                content_node = {'type':'text', 'data':text}
                content.append(content_node)
                last_node_type = 1
                continue
            if (node_name[0].lower() == "a"):
                text_list = node.xpath('./text()').extract()
                if len(text_list) == 0:
                    continue
                text = text_list[0].strip()
                if (len(text) == 0):
                    continue
                if last_node_type == 1 and len(content) > 0:
                    last_text = content[len(content)-1]
                    last_text['data'] = last_text['data'] + text
                    content[len(content)-1] = text
                else:
                    content_node = {'type':'text', 'data':text}
                    content.append(content_node)

                last_node_type = 2

            if (node_name[0].lower() == "img"):
                image_class = node.xpath('contains(@class, "BDE_Image")').extract()
                if (len(image_class) == 0 or image_class[0] == '0'):
                    continue
                src = node.xpath('./@src').extract()
                if len(src) == 0:
                    continue
                has_image = True
                content_node = {'type':'pic', 'data':src[0]}
                content.append(content_node)
                last_node_type = 3

        post_id_list=post.xpath('.//div/div/cc/div[@class="d_post_content j_d_post_content "]/@id').extract()
        if (len(post_id_list) <= 0):
            return "", "", has_image, False

        if (has_image == False and len(content) <= self.__min_post_word_count):
            return "", "", has_image, False

        return content, post_id_list[0], has_image, True



