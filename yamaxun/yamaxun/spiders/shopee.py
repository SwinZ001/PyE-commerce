import json

import redis
import copy
import re

import requests
import scrapy


from yamaxun.items import YamaxunItem, commentItem
from scrapy_redis.spiders import RedisSpider
import numpy as np

class ShopeeSpider(RedisSpider):
    name = 'shopee'
    # allowed_domains = ['shopee.sg']
    # start_urls = ['http://shopee.sg/']
    # 大分类链接'https://shopee.sg/api/v4/pages/get_category_tree'

    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(ShopeeSpider,self).__init__(*args,**kwargs)

    def make_requests_from_url(self, url):
        # 初始化商品数组，存放商品字典
        item = YamaxunItem()
        item['type'] = 'Product_data'
        item['startUrl'] = url
        return scrapy.Request(url,
                              dont_filter=True,
                              meta={'item': copy.deepcopy(item)},
                              )
    #
    # # 获取总分类列表，构建商品列表链接
    # # 静态页面xpath获取
    # def parse(self, response):
    #     item = response.meta['item']
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #     # 提取数据总数据节点
    #     category_list = data_obj['data']['category_list']
    #     # 通过总数据节点循环获取大分类数据并构建商品总数据链接
    #     for category in category_list:
    #         # 获取大分类id
    #         cat_id = category['catid']
    #         # # 获取大分类name，不管是display_name还是name节点的值都是英文
    #         cat_name = category['name']
    #         # 构建商品总数据链接（根据销量（最热销）by=sales）
    #         Categories_link = 'https://shopee.sg/' + cat_name + '-cat.' + str(cat_id) + '?sortBy=sales&page=0'
    #         item['big_classification_link'] = Categories_link
    #         item['big_classification_text'] = cat_name
    #         # 缩小范围用于测试(女装)（SHOPEEPAY NEAR ME这个分类是附近的商品，里面数据对不上，可以不用爬取）
    #         if "11012819" in Categories_link:
    #             yield scrapy.Request(
    #                 url=item['big_classification_link'],
    #                 callback=self.get_pages,
    #                 meta={'item': copy.deepcopy(item),'cat_id': copy.deepcopy(cat_id),'cat_name': copy.deepcopy(cat_name)},
    #                 dont_filter=True
    #                 )
    #
    # # 翻页链接
    # # 静态页面xpath获取
    # def get_pages(self, response):
    #     item = response.meta['item']
    #     cat_id = response.meta['cat_id']
    #     cat_name = response.meta['cat_name']
    #     # 获取页数组件
    #     pageSize = int(response.xpath('//*[@class="shopee-mini-page-controller__total"]/text()')[0].extract().strip())
    #     # 构建每一页商品总数据链接#（根据销量（最热销）by = sales）
    #     for page in range(pageSize+1):
    #         page_link = 'https://shopee.sg/' + cat_name + '-cat.' + str(cat_id) + '?sortBy=sales&page=' + str(page)
    #         item['page_link'] = page_link
    #         # 缩小范围用于测试（提取第一页）
    #         if "page=0" in page_link:
    #             yield scrapy.Request(
    #                 url=item['page_link'],
    #                 callback=self.get_commodity_link,
    #                 meta={'item': copy.deepcopy(item)},
    #                 dont_filter=True
    #             )
    #
    # # 获取商品详情数据链接
    # # 静态页面xpath获取
    # def get_commodity_link(self, response):
    #     item = response.meta['item']
    #     # # 商品链接组件
    #     # commodity_link_nodes = response.xpath('//*[@class="col-xs-2-4 shopee-search-item-result__item"]')
    #     # print(len(commodity_link_nodes))
    #     commodity_link_nodes = response.xpath('//*[@data-module="cGMtY2F0ZWdvcnlwYWdl"]/text()')[0].extract().strip()
    #     print(commodity_link_nodes)
    #     # # 循环构建商品详情链接
    #     # for commodity_link_node in commodity_link_nodes:
    #     #     commodity_link = commodity_link_node.xpath('./a/@href')[0].extract().strip()
    #     #     # print(commodity_link)
    #     #     patter = re.compile("i.(\d+.\d+)")
    #     #     aa = patter.findall(commodity_link)[0]
    #     #     print(aa)
    #
    #         # # 缩小范围用于测试（提取第一个商品）
    #         # # if "itemid=9752801212&shopid=113177348" in commodity_link:
    #         # yield scrapy.Request(
    #         #     url=item['commodity_link'],
    #         #     callback=self.get_commodity_data,
    #         #     meta={'item': copy.deepcopy(item),'itemid': copy.deepcopy(itemid),'shopid': copy.deepcopy(shopid)},
    #         #     dont_filter=True
    #         # )
    #
    # # def parse(self, response):
    # # 获取商品详情数据
    # def get_commodity_data(self, response):
    #     item = response.meta['item']
    #     # 为后面构建链接使用
    #     itemid = response.meta['itemid']
    #     shopid = response.meta['shopid']
    #
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #
    #     # itemid = data_obj['data']['itemid']
    #     # shopid = data_obj['data']['shopid']
    #
    #     # 商品名
    #     commodity_name = data_obj['data']['name']
    #     item['commodity_name'] = commodity_name
    #
    #     # 历史销量
    #     historical_sold = data_obj['data']['historical_sold']
    #     item['historical_sold'] = historical_sold
    #
    #     # 折扣
    #     discount = data_obj['data']['discount']
    #     item['discount'] = discount
    #
    #     # 星级(取小数点后两位)
    #     rating_star = round(data_obj['data']['item_rating']['rating_star'],2)
    #     item['rating_star'] = rating_star
    #
    #     # sku(包含每个属性，原价，打折后价格，库存（库存0代表当前属性不可选）)
    #     # sku搭配数据节点
    #     sku_models = data_obj['data']['models']
    #     # sku属性名和属性值数据节点
    #     tier_variations = data_obj['data']['tier_variations']
    #     # 存放所有sku的列表
    #     sku_list = []
    #
    #     for sku in sku_models:
    #
    #         # 存sku的字典
    #         sku_dict = {}
    #         # 取出搭配的sku
    #         sku_collocation = sku['name']
    #
    #         # 给搭配sku分割加'#'，给后面sku值也加'#'，增加匹配准确度
    #         # 速卖通以';'虾皮是以','进行分割形成数组
    #         sku_collocation_dict = sku_collocation.split(',')
    #         # 将数据循环重组+‘#’
    #         for i, k in enumerate(sku_collocation_dict):
    #             sku_collocation_dict[i] = k + '#'
    #         # 最后将重组数据后的数组以','进行合并，形成新的字符串14:13978534#,5:4645#(z注意;变成了,不过没影响)
    #         new_sku_collocation = ','.join(sku_collocation_dict)
    #
    #         for tier in tier_variations:
    #             # 取出属性值（数组）
    #             options = tier['options']
    #             for sku_type_value in options:
    #                 # 给sku值加'#'，增加匹配准确度
    #                 new_sku_type_value = sku_type_value + '#'
    #                 # 用单个属性值去匹配搭配的sku，如果搭配的sku有这个属性，就提取出来
    #                 if new_sku_type_value in new_sku_collocation:
    #                     sku_type = tier['name']
    #                     # 给原来值不要给加#的值
    #                     sku_value = sku_type_value
    #                     # sku对应属性和值
    #                     sku_dict[sku_type] = sku_value
    #         # 打折后价格
    #         discount_Price = sku['price']
    #         sku_dict['discount_Price'] = discount_Price
    #         # 原价
    #         original_Price = sku['price_before_discount']
    #         # 有打折就等于原价
    #         if original_Price != 0:
    #             sku_dict['original_Price'] = original_Price
    #         # 原价0代表没有打折,那原价就等于打折后价格
    #         else:
    #             sku_dict['original_Price'] = sku['price']
    #
    #         # 库存
    #         inventory = sku['normal_stock']
    #         sku_dict['inventory'] = inventory
    #
    #         sku_list.append(sku_dict)
    #     item['sku_list'] = sku_list
    #
    #     # 商品图片
    #     image_url_list = []
    #     images = data_obj['data']['images']
    #     # 构建图片链接
    #     for image in images:
    #         image_url = 'https://cf.shopee.sg/file/' + image
    #         image_url_list.append(image_url)
    #     item['commodity_Imge_link'] = image_url_list
    #
    #    # 商品规格
    #     attributes_list = []
    #     attributes = data_obj['data']['attributes']
    #     if attributes != None:
    #         attributes_dict = {}
    #         for attribute in attributes:
    #             attribute_name = attribute['name']
    #             attribute_value = attribute['value']
    #             attributes_dict[attribute_name] = attribute_value
    #         attributes_list.append(attributes_dict)
    #         item['attributes'] = attributes_list
    #     else:
    #         attributes_dict = {}
    #         attributes_dict['null'] = 'null'
    #         attributes_list.append(attributes_dict)
    #         item['attributes'] = attributes_list
    #
    #     # 商品描述
    #     description = data_obj['data']['description']
    #     item['description'] = description
    #
    #     #商品店铺数据请求（获取shopid构建链接）
    #     # 构建链接
    #     store_data_link = 'https://shopee.sg/api/v4/product/get_shop_info?shopid=' + str(shopid)
    #     # 店铺链接
    #     item['store_data_link'] = store_data_link
    #     yield scrapy.Request(
    #         url=item['store_data_link'],
    #         callback=self.get_store_data,
    #         meta={'item': copy.deepcopy(item),'itemid': copy.deepcopy(itemid),'shopid': copy.deepcopy(shopid)},
    #         dont_filter=True
    #     )
    #
    # # 商品店铺数据（里面有包括出货商家的用户名id，但暂时不爬取）
    # def get_store_data(self, response):
    #     item = response.meta['item']
    #
    #     itemid = response.meta['itemid']
    #     shopid = response.meta['shopid']
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #     #店家数据
    #     # 存放店铺数据字典
    #     store_data_list = {}
    #     # 店铺链接前面有
    #     # 店铺名
    #     store_name = data_obj['data']['account']['username']
    #     store_data_list['store_name'] = store_name
    #     # 出货地
    #     shipment_Place = data_obj['data']['place']
    #     store_data_list['shipment_Place'] = shipment_Place
    #     # 粉丝数
    #     follower_count = data_obj['data']['follower_count']
    #     store_data_list['follower_count'] = follower_count
    #     # 开店年份
    #     openTime = data_obj['data']['ctime']
    #     store_data_list['openTime'] = openTime
    #
    #     # #为了与其他平台数据统一，一下先不要
    #
    #     # # 店铺总商品数（）
    #     # item_count = data_obj['data']['item_count']
    #     # store_data_list['item_count'] = item_count
    #     # # 聊天回复率
    #     # response_rate = data_obj['data']['response_rate']
    #     # store_data_list['response_rate'] = response_rate
    #     # # 回应速度（要转时间戳获取，还没研究）
    #     # response_time = data_obj['data']['response_time']
    #     # store_data_list['response_time'] = response_time
    #     # # 好评数
    #     # rating_good = data_obj['data']['rating_good']
    #     # store_data_list['rating_good'] = rating_good
    #
    #     # 保存店铺数据
    #     item['store_data'] = store_data_list
    #     yield item
    #
    #
    #     item2 = commentItem()
    #
    #     item2['type'] = 'Product_Review_Data'
    #     #构建评论数据链接
    #     comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(itemid) + '&limit=6&offset=0&shopid=' + str(shopid) + '&type=0'
    #
    #
    #     yield scrapy.Request(
    #         url=comment_data_link,
    #         callback=self.get_comment_link,
    #         meta={'item2': copy.deepcopy(item2), 'itemid': copy.deepcopy(itemid), 'shopid': copy.deepcopy(shopid)},
    #         dont_filter=True
    #     )
    #
    #
    #
    # # 第一种方法，先构建评论链接再批量请求数据
    # # 获取评论页数链接
    # def get_comment_link(self, response):
    #     item2 = response.meta['item2']
    #
    #     # 获取前面数据的商品id，用于构建每一页评论链接
    #     itemid = response.meta['itemid']
    #     shopid = response.meta['shopid']
    #
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #     # 获取评论总数rating_total
    #     rating_total = data_obj['data']['item_rating_summary']['rating_total']
    #
    #     # 循环构建评论链接
    #     for page in range(rating_total + 1):
    #         item2['page'] = page
    #         # 构建每一页评论数据链接
    #         comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(itemid) + '&limit=1&offset=' + str(page) + '&shopid=' + str(shopid) + '&type=0'
    #         item2['comment_data_link'] = comment_data_link
    #         # if 'offset=0' in comment_data_link:
    #         yield scrapy.Request(
    #                     url=comment_data_link,
    #                     callback=self.get_comment_data,
    #                     meta={'item2': copy.deepcopy(item2),
    #                           'itemid': copy.deepcopy(itemid),
    #                           'shopid': copy.deepcopy(shopid)
    #                           },
    #                     dont_filter=True
    #                 )
    #
    # # 获取评论数据
    # def get_comment_data(self, response):
    #     item2 = response.meta['item2']
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #     # 换\n好后，再把两个，的换成一个
    #     comment = data_obj['data']['ratings'][0]['comment'].replace('\n', ',').replace(',,', ',')
    #     item2['comment_data'] = comment
    #     yield item2










# 旧方式获取（403错误）
# //////////////////////////////////////////以下为json数据获取商品列表数据/////////////////////////////////////////////////////////////////

    # # 方式1，通过json数据获取，但是现在会403错误，需要换ip
    def parse(self, response):
        item = response.meta['item']
        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()
        # 提取数据总数据节点
        category_list = data_obj['data']['category_list']
        print(len(category_list))
        # 通过总数据节点循环获取大分类数据并构建商品总数据链接
        for category in category_list:
            # 获取大分类id
            catid = category['catid']
            # # 获取大分类name，不管是display_name还是name节点的值都是英文
            name = category['name']
            # 构建商品总数据链接（根据销量（最热销）by=sales）
            Categories_link = 'https://shopee.sg/api/v4/search/search_items?by=sales&limit=60&match_id=' + str(catid) + '&newest=0'
            item['big_classification_link'] = Categories_link
            item['big_classification_text'] = name
            # 缩小范围用于测试(女装)（SHOPEEPAY NEAR ME这个分类是附近的商品，里面数据对不上，可以不用爬取）
            if "11012819" in Categories_link:
                yield scrapy.Request(
                    url=item['big_classification_link'],
                    callback=self.get_pages,
                    meta={'item': copy.deepcopy(item),'catid': copy.deepcopy(catid),'name': copy.deepcopy(name)},
                    dont_filter=True
                    )

    # 方式1，通过json数据获取，但是现在会403错误，需要换ip
    # 获取页数链接
    def get_pages(self, response):
        item = response.meta['item']
        catid = response.meta['catid']
        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()

        # 获取商品总数total_count
        total_count = data_obj['total_count']
        #第一页的商品数
        items_len = len(data_obj['items'])
        # 页面总页数 = total_count（商品总数量） / （60）第一页的商品数
        pageSize = int(total_count / items_len)
        print(pageSize)
        # 构建每一页商品总数据链接（后台数据有3000（51页），但页面只限制显示2940（50页），这里按照页面显示爬取，要爬取全部就pageSize+1)
        #（根据销量（最热销）by = sales）
        for i in range(pageSize+1):
            page = i * items_len
            print(page)
            page_link = 'https://shopee.sg/api/v4/search/search_items?by=sales&limit=60&match_id=' + str(catid) + '&newest=' + str(page)
            item['page_link'] = page_link
            print(page_link)
            # 缩小范围用于测试（提取第一页）
            if "newest=0" in page_link:
                yield scrapy.Request(
                    url=item['page_link'],
                    callback=self.get_commodity_link,
                    meta={'item': copy.deepcopy(item)},
                    dont_filter=True
                )

    # 方式1，通过json数据获取，但是现在会403错误，需要换ip
    # 获取商品数据链接
    def get_commodity_link(self, response):
        item = response.meta['item']
        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()
        # 全部商品数据节点
        item_Data = data_obj['items']
        # 循环构建商品详情链接
        for items in item_Data:
            itemid = items['item_basic']['itemid']
            shopid = items['item_basic']['shopid']

            commodity_link = 'https://shopee.sg/api/v4/item/get?itemid=' + str(itemid) + '&shopid=' + str(shopid)
            item['commodity_link'] = commodity_link

            # 缩小范围用于测试（提取第一个商品）
            # if "itemid=9752801212&shopid=113177348" in commodity_link:
            yield scrapy.Request(
                url=item['commodity_link'],
                callback=self.get_commodity_data,
                meta={'item': copy.deepcopy(item),'itemid': copy.deepcopy(itemid),'shopid': copy.deepcopy(shopid)},
                dont_filter=True
            )
    # def parse(self, response):
    # 获取商品详情数据
    def get_commodity_data(self, response):
        item = response.meta['item']
        # 为后面构建链接使用
        itemid = response.meta['itemid']
        shopid = response.meta['shopid']

        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()

        # itemid = data_obj['data']['itemid']
        # shopid = data_obj['data']['shopid']

        # 商品名
        commodity_name = data_obj['data']['name']
        item['commodity_name'] = commodity_name

        # 历史销量
        historical_sold = data_obj['data']['historical_sold']
        item['historical_sold'] = historical_sold

        # 折扣
        discount = data_obj['data']['discount']
        item['discount'] = discount

        # 星级(取小数点后两位)
        rating_star = round(data_obj['data']['item_rating']['rating_star'],2)
        item['rating_star'] = rating_star

        # sku(包含每个属性，原价，打折后价格，库存（库存0代表当前属性不可选）)
        # sku搭配数据节点
        sku_models = data_obj['data']['models']
        # sku属性名和属性值数据节点
        tier_variations = data_obj['data']['tier_variations']
        # 存放所有sku的列表
        sku_list = []

        for sku in sku_models:

            # 存sku的字典
            sku_dict = {}
            # 取出搭配的sku
            sku_collocation = sku['name']

            # 给搭配sku分割加'#'，给后面sku值也加'#'，增加匹配准确度
            # 速卖通以';'虾皮是以','进行分割形成数组
            sku_collocation_dict = sku_collocation.split(',')
            # 将数据循环重组+‘#’
            for i, k in enumerate(sku_collocation_dict):
                sku_collocation_dict[i] = k + '#'
            # 最后将重组数据后的数组以','进行合并，形成新的字符串14:13978534#,5:4645#(z注意;变成了,不过没影响)
            new_sku_collocation = ','.join(sku_collocation_dict)

            for tier in tier_variations:
                # 取出属性值（数组）
                options = tier['options']
                for sku_type_value in options:
                    # 给sku值加'#'，增加匹配准确度
                    new_sku_type_value = sku_type_value + '#'
                    # 用单个属性值去匹配搭配的sku，如果搭配的sku有这个属性，就提取出来
                    if new_sku_type_value in new_sku_collocation:
                        sku_type = tier['name']
                        # 给原来值不要给加#的值
                        sku_value = sku_type_value
                        # sku对应属性和值
                        sku_dict[sku_type] = sku_value
            # 打折后价格
            discount_Price = sku['price']
            sku_dict['discount_Price'] = discount_Price
            # 原价
            original_Price = sku['price_before_discount']
            # 有打折就等于原价
            if original_Price != 0:
                sku_dict['original_Price'] = original_Price
            # 原价0代表没有打折,那原价就等于打折后价格
            else:
                sku_dict['original_Price'] = sku['price']

            # 库存
            inventory = sku['normal_stock']
            sku_dict['inventory'] = inventory

            sku_list.append(sku_dict)
        item['sku_list'] = sku_list

        # 商品图片
        image_url_list = []
        images = data_obj['data']['images']
        # 构建图片链接
        for image in images:
            image_url = 'https://cf.shopee.sg/file/' + image
            image_url_list.append(image_url)
        item['commodity_Imge_link'] = image_url_list

       # 商品规格
        attributes_list = []
        attributes = data_obj['data']['attributes']
        if attributes != None:
            attributes_dict = {}
            for attribute in attributes:
                attribute_name = attribute['name']
                attribute_value = attribute['value']
                attributes_dict[attribute_name] = attribute_value
            attributes_list.append(attributes_dict)
            item['attributes'] = attributes_list
        else:
            attributes_dict = {}
            attributes_dict['null'] = 'null'
            attributes_list.append(attributes_dict)
            item['attributes'] = attributes_list

        # 商品描述
        description = data_obj['data']['description']
        item['description'] = description

        #商品店铺数据请求（获取shopid构建链接）
        # 构建链接
        store_data_link = 'https://shopee.sg/api/v4/product/get_shop_info?shopid=' + str(shopid)
        # 店铺链接
        item['store_data_link'] = store_data_link
        yield scrapy.Request(
            url=item['store_data_link'],
            callback=self.get_store_data,
            meta={'item': copy.deepcopy(item),'itemid': copy.deepcopy(itemid),'shopid': copy.deepcopy(shopid)},
            dont_filter=True
        )

    # 商品店铺数据（里面有包括出货商家的用户名id，但暂时不爬取）
    def get_store_data(self, response):
        item = response.meta['item']

        itemid = response.meta['itemid']
        shopid = response.meta['shopid']
        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()
        #店家数据
        # 存放店铺数据字典
        store_data_list = {}
        # 店铺链接前面有
        # 店铺名
        store_name = data_obj['data']['account']['username']
        store_data_list['store_name'] = store_name
        # 出货地
        shipment_Place = data_obj['data']['place']
        store_data_list['shipment_Place'] = shipment_Place
        # 粉丝数
        follower_count = data_obj['data']['follower_count']
        store_data_list['follower_count'] = follower_count
        # 开店年份
        openTime = data_obj['data']['ctime']
        store_data_list['openTime'] = openTime

        # #为了与其他平台数据统一，一下先不要

        # # 店铺总商品数（）
        # item_count = data_obj['data']['item_count']
        # store_data_list['item_count'] = item_count
        # # 聊天回复率
        # response_rate = data_obj['data']['response_rate']
        # store_data_list['response_rate'] = response_rate
        # # 回应速度（要转时间戳获取，还没研究）
        # response_time = data_obj['data']['response_time']
        # store_data_list['response_time'] = response_time
        # # 好评数
        # rating_good = data_obj['data']['rating_good']
        # store_data_list['rating_good'] = rating_good

        # 保存店铺数据
        item['store_data'] = store_data_list
        yield item


        # item2 = commentItem()
        #
        # item2['type'] = 'Product_Review_Data'
        # #构建评论数据链接
        # comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(itemid) + '&limit=6&offset=0&shopid=' + str(shopid) + '&type=0'
        #
        #
        # yield scrapy.Request(
        #     url=comment_data_link,
        #     callback=self.get_comment_link,
        #     meta={'item2': copy.deepcopy(item2), 'itemid': copy.deepcopy(itemid), 'shopid': copy.deepcopy(shopid)},
        #     dont_filter=True
        # )



    # 第一种方法，先构建评论链接再批量请求数据
    # 获取评论页数链接
    def get_comment_link(self, response):
        item2 = response.meta['item2']

        # 获取前面数据的商品id，用于构建每一页评论链接
        itemid = response.meta['itemid']
        shopid = response.meta['shopid']

        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()
        # 获取评论总数rating_total
        rating_total = data_obj['data']['item_rating_summary']['rating_total']

        # 循环构建评论链接
        for page in range(rating_total + 1):
            item2['page'] = page
            # 构建每一页评论数据链接
            comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(itemid) + '&limit=1&offset=' + str(page) + '&shopid=' + str(shopid) + '&type=0'
            item2['comment_data_link'] = comment_data_link
            # if 'offset=0' in comment_data_link:
            yield scrapy.Request(
                        url=comment_data_link,
                        callback=self.get_comment_data,
                        meta={'item2': copy.deepcopy(item2),
                              'itemid': copy.deepcopy(itemid),
                              'shopid': copy.deepcopy(shopid)
                              },
                        dont_filter=True
                    )

    # 获取评论数据
    def get_comment_data(self, response):
        item2 = response.meta['item2']
        # 这是返回的是json数据，所以直接用response.json()
        data_obj = response.json()
        # 换\n好后，再把两个，的换成一个
        comment = data_obj['data']['ratings'][0]['comment'].replace('\n', ',').replace(',,', ',')
        item2['comment_data'] = comment
        yield item2







    # # 获取评论第二种方法
    #
    #
    # # 商品店铺数据（里面有包括出货商家的用户名id，但暂时不爬取）
    # def get_store_data(self, response):
    #     item = response.meta['item']
    #
    #     itemid = response.meta['itemid']
    #     shopid = response.meta['shopid']
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #     # 店家数据
    #     # 存放店铺数据字典
    #     store_data_list = {}
    #     # 店铺链接前面有
    #     # 店铺名
    #     store_name = data_obj['data']['account']['username']
    #     store_data_list['store_name'] = store_name
    #     # 出货地
    #     shipment_Place = data_obj['data']['place']
    #     store_data_list['shipment_Place'] = shipment_Place
    #     # 粉丝数
    #     follower_count = data_obj['data']['follower_count']
    #     store_data_list['follower_count'] = follower_count
    #     # 开店年份
    #     openTime = data_obj['data']['ctime']
    #     store_data_list['openTime'] = openTime
    #
    #     # #为了与其他平台数据统一，一下先不要
    #
    #     # # 店铺总商品数（）
    #     # item_count = data_obj['data']['item_count']
    #     # store_data_list['item_count'] = item_count
    #     # # 聊天回复率
    #     # response_rate = data_obj['data']['response_rate']
    #     # store_data_list['response_rate'] = response_rate
    #     # # 回应速度（要转时间戳获取，还没研究）
    #     # response_time = data_obj['data']['response_time']
    #     # store_data_list['response_time'] = response_time
    #     # # 好评数
    #     # rating_good = data_obj['data']['rating_good']
    #     # store_data_list['rating_good'] = rating_good
    #
    #     # 保存店铺数据
    #     item['store_data'] = store_data_list
    #     yield item
    #
    #
    #
    #     item2 = commentItem()
    #
    #     item2['type'] = 'Product_Review_Data'
    #     # 构建评论数据链接
    #     comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(
    #         itemid) + '&limit=6&offset=0&shopid=' + str(shopid) + '&type=0'
    #     item2['comment_data_link'] = comment_data_link
    #
    #     # 为后面爬取评论数据构建参数
    #     # 初始化循环次数
    #     page_i = 0
    #     # 初始化存放每一个商品的全部评论的列表
    #     comment_list = []
    #
    #     yield scrapy.Request(
    #         url=item2['comment_data_link'],
    #         callback=self.get_comment_data,
    #         meta={'item2': copy.deepcopy(item2), 'itemid': copy.deepcopy(itemid), 'shopid': copy.deepcopy(shopid),
    #               'page_i': copy.deepcopy(page_i), 'comment_list': copy.deepcopy(comment_list)},
    #         dont_filter=True
    #     )
    #
    #
    #
    #
    # # 获取评论第二种方法
    # # 第二种方法，将这个函数作为一个循环体，一页一页的爬取评论
    # # 获取评论页数链接(将这个函数作为一个循环体，一页一页的爬取评论，)
    # def get_comment_data(self, response):
    #     item2 = response.meta['item2']
    #
    #     # 获取前一个方法创建的初始化数据（一个商品只有一次，后面都是接受自身方法结尾传递的参数数据）
    #     # 循环次数
    #     page_i = response.meta['page_i']
    #     # 存放每一个商品的评论的列表
    #     comment_list = response.meta['comment_list']
    #     # 获取前面数据的商品id，用于构建每一页评论链接
    #     itemid = response.meta['itemid']
    #     shopid = response.meta['shopid']
    #
    #     # 这是返回的是json数据，所以直接用response.json()
    #     data_obj = response.json()
    #
    #     # 这些数据只要第一页的
    #     if page_i == 0:
    #         # 获取评论总数rating_total
    #         rating_total = data_obj['data']['item_rating_summary']['rating_total']
    #         # 第一页的评论数
    #         ratings_len = len(data_obj['data']['ratings'])
    #         # 页面总页数 = rating_total（评论数总数量） / （60）第一页的评论数
    #         pageSize = int(rating_total / ratings_len)
    #         print(str(rating_total),str(ratings_len),str(pageSize))
    #     else:
    #         ratings_len = response.meta['ratings_len']
    #         pageSize = response.meta['pageSize']
    #
    #
    #
    #     # 获取每一页评论数列表
    #     ratings = data_obj['data']['ratings']
    #     # 循环获取每一条评论
    #     for rating in ratings:
    #         comment = rating['comment']
    #         # 把评论添加评论列表
    #         comment_list.append(comment)
    #
    #
    #     # 获取完一页获取下一页
    #     page_i += 1
    #     # 次数等于一个商品评论页数，则提交数据
    #     if page_i == pageSize:
    #         print(str(page_i),str(len(comment_list)))
    #         item2['comment_data'] = comment_list
    #         # 商品店铺全部商品数据：（从商品详情列表数据获取shopid构建网址链接，这里不演示）
    #         yield item2
    #     # 次数不等于评论页数则构造下一页页数
    #     else:
    #         page = page_i * ratings_len
    #         print(str(page_i))
    #
    #         # 构建每一页评论数据链接
    #         comment_data_link = 'https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(itemid) + '&limit=6&offset=' + str(page) + '&shopid=' + str(shopid) + '&type=0'
    #         item2['comment_data_link'] = comment_data_link
    #
    #         yield scrapy.Request(
    #             url=item2['comment_data_link'],
    #             callback=self.get_comment_data,
    #             meta={'item2': copy.deepcopy(item2),
    #                   'page_i': copy.deepcopy(page_i),
    #                   'ratings_len':copy.deepcopy(ratings_len),
    #                   'pageSize': copy.deepcopy(pageSize),
    #                   'itemid': copy.deepcopy(itemid),
    #                   'shopid': copy.deepcopy(shopid),
    #                   'comment_list': copy.deepcopy(comment_list)},
    #             dont_filter=True
    #         )





