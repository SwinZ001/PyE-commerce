import copy
import re
import scrapy
from yamaxun.items import YamaxunItem
from scrapy_redis.spiders import RedisSpider
import numpy as np


class AibababSpider(RedisSpider):
    name = 'aibabab'
    # allowed_domains = ['p4psearch.1688.com']
    # start_urls = ['http://p4psearch.1688.com/']
    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(AibababSpider,self).__init__(*args,**kwargs)


    def make_requests_from_url(self, url):
        # 初始化商品数组，存放商品字典
        item = YamaxunItem()
        item['startUrl'] = url
        return scrapy.Request(url,
                              dont_filter=True,
                              meta={'item': copy.deepcopy(item)},
                              # cookies=cookies
                              )

    def parse(self, response):
        print(response.text)
        sum_pages = response.xpath(
            '//*[@id="alibar"]/div[1]/div[2]/ul/li[1]/div[1]/span/a/text()').extract_first()
        print(sum_pages)
        pass
