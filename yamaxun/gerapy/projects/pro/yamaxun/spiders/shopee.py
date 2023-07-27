
import copy
import re
import scrapy
from yamaxun.items import YamaxunItem
from scrapy_redis.spiders import RedisSpider
import numpy as np

class ShopeeSpider(RedisSpider):
    name = 'shopee'
    # allowed_domains = ['shopee.sg']
    # start_urls = ['http://shopee.sg/']
    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(ShopeeSpider,self).__init__(*args,**kwargs)

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
        sum_pages = response.xpath('//*[@id="main"]/div/div[2]/div/div[2]/div[2]/div/div[1]/div[2]/div/span[2]/text()').extract_first()
        print(sum_pages)
        pass
