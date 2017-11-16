# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request
from scrapy import signals
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.spider import CrawlSpider, Rule
from scrapy.xlib.pydispatch import dispatcher
from lxml import etree
#import os

from anycrawl.items import CssmobanItems
'''
import logging
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
'''

class MultSetSpider(CrawlSpider):
    name = "cssmobanSpider"
    allowed_domains = ["cssmoban.com"]
    start_urls = [
        "http://www.cssmoban.com/cssthemes/index.shtml"
        ]

    def __init__(self):
        dispatcher.connect(self.spider_opened,signals.spider_opened)
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def parse(self, response):
        base_url = get_base_url(response)
        yield Request(base_url, callback=self.parse_page_lvl1, dont_filter=False)
        
    def parse_page_lvl1(self,response):
        items = []
        base_url = get_base_url(response)

        links = response.xpath('//li/a[1]').extract()
        for index, link in enumerate(links):
            selector = etree.HTML(link)
            
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]
            
            img_urls = selector.xpath('//a/img/@src')
            if len(img_urls) == 0:
                continue
            img_url = img_urls[0]
            
            titles = selector.xpath('//a/img/@alt')
            if len(titles) == 0:
                title = '未知主题'
            else:
                title = titles[0]
            
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            item = CssmobanItems()
            item['url'] = abs_url
            item['ref_url'] = abs_url
            item['img_url'] = img_url
            item['title'] = title
            items.append(item)
        
        #for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
        #    abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
        #    yield Request(abs_url, callback=self.parse_page_lvl1, dont_filter=False)
        
        for item in items:
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_page_lvl2, dont_filter=False)

        if len(response.xpath("//a[text()='下一页']")) > 0:
            next_label = response.xpath("//a[text()='下一页']").extract()[0]
            selector = etree.HTML(next_label)
            url_next = selector.xpath('//a/@href')[0]
            abs_url = str(urljoin_rfc(base_url, url_next), encoding = "utf-8")
            yield Request(abs_url, callback=self.parse_page_lvl1, dont_filter=False)

    def parse_page_lvl2(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
        
        for file_url in response.xpath('//a[text()="免费下载"]').extract():
            selector = etree.HTML(file_url)
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            file_url = urls[0]
            item = CssmobanItems()
            item['ref_url'] = g_item['ref_url']
            item['title'] = g_item['title']
            file_url = file_url.strip()
            item['img_url'] = g_item['img_url']
            item['file_url'] = file_url
            #print(file_url)
            yield item
            
    def spider_opened(self,spider):
        print("★★★★★task start!★★★★★")

    def spider_closed(self,spider):
        print("★★★★★task over!★★★★★")
