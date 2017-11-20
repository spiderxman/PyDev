# -*- coding: utf-8 -*-
import scrapy
import os

from scrapy import Request
from scrapy import signals
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.spider import CrawlSpider, Rule
from scrapy.xlib.pydispatch import dispatcher
from lxml import etree

from anycrawl.items import AitaotuItems


class JapanZipCodeSpider(CrawlSpider):
    name = "japanZipCodeSpider"
    allowed_domains = ["post.japanpost.jp"]
    start_urls = [
            "http://www.post.japanpost.jp/zipcode/"
        ]

    def __init__(self):
        dispatcher.connect(self.spider_opened,signals.spider_opened)
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def parse(self, response):
        base_url = get_base_url(response)
        yield Request(base_url, callback=self.parse_address_pref, dont_filter=False)
        
    def parse_address_pref(self,response):
        items = []
        base_url = get_base_url(response)

        links = response.xpath('//div[@class="areaTxt"]/ul/li/a').extract()
        for index, link in enumerate(links):
            selector = etree.HTML(link)
            
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]
            
            addr_prefs = selector.xpath('//a/text()')
            if len(addr_prefs) == 0:
                addr_pref = '未知都道府県'
            else:
                addr_pref = addr_prefs[0]
            
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            item = JapanZipCodeItems()
            item['url'] = abs_url
            item['pref'] = addr_pref
            #items.append(item)
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_address_city, dont_filter=False)
        
        #for item in items:
        #    yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_address_city, dont_filter=False)

    def parse_address_city(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
        
        for link in response.xpath('//tr[@valign="top"]').extract():
            selector = etree.HTML(link)
            urls = selector.xpath('//td[1]//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]

            addr_citys = selector.xpath('//td[1]//a/text()')
            if len(addr_city) == 0:
                addr_city = '未知市町村'
            else:
                addr_city = addr_citys[0]

            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")

            item = JapanZipCodeItems()
            item['url'] = abs_url
            item['pref'] = g_item['pref']
            item['city'] = addr_city
            #print(img_url)
            #yield item
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_address_street, dont_filter=False)

        #for item in items:
        #    yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_address_street, dont_filter=False)

    def parse_address_street(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
        str_xpath = '//td[@class="data" and text()=' + g_item["city"] + ']//a'
        for link in response.xpath(str_xpath).extract():
            selector = etree.HTML(link)
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]

            addr_streets = selector.xpath('//a/text()')
            if len(addr_street) == 0:
                addr_street = '未知番地'
            else:
                addr_street = addr_streets[0]

            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            
            item = JapanZipCodeItems()
            item['url'] = abs_url
            item['pref'] = g_item['pref']
            item['city'] = g_item['city']
            item['street'] = addr_street
            #print(img_url)
            #yield item
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_address_zipcode, dont_filter=False)

    def parse_address_zipcode(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
        
        zipCode = response.xpath('//span[@class="zip-code"]/text()').extract()

        item = JapanZipCodeItems()
        item['pref'] = g_item['pref']
        item['city'] = g_item['city']
        item['street'] = g_item['street']
        item['zipCode'] = zipCode
        #print(img_url)
        yield item
            
    def spider_opened(self,spider):
        print("★★★★★task start!★★★★★")

    def spider_closed(self,spider):
        print("★★★★★task over!★★★★★")
            
