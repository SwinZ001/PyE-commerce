# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YamaxunItem(scrapy.Item):
    # define the fields for your item here like:
    # 根据这个区分是普通数据还是评论数据
    # 在pipelines进行区分，在评论新建一个评论的key
    type = scrapy.Field()

    # 开始url
    startUrl = scrapy.Field()
    # 大分类url
    big_classification_link = scrapy.Field()
    # 大分类文本
    big_classification_text = scrapy.Field()
    # 翻页url
    page_link = scrapy.Field()
    # 商品url
    commodity_link = scrapy.Field()
    # 商品名
    commodity_name = scrapy.Field()
    # 历史销量
    historical_sold = scrapy.Field()
    # 折扣
    discount = scrapy.Field()
    # 评分星级
    rating_star = scrapy.Field()
    # sku列表
    sku_list = scrapy.Field()
    # 商品图片链接
    commodity_Imge_link = scrapy.Field()
    # 商品规格(做工材料)
    attributes = scrapy.Field()
    # 商品描述
    description = scrapy.Field()
    # 商品店铺数据链接
    store_data_link = scrapy.Field()
    # 商品店铺详情数据（销量，商品数，评价）
    store_data = scrapy.Field()
    # # 评论数据链接
    # comment_data_link = scrapy.Field()
    # # 评论数据
    # comment_data = scrapy.Field()






class commentItem(scrapy.Item):
    # 根据这个区分是普通数据还是评论数据
    # 在pipelines进行区分，在评论新建一个评论的key
    type = scrapy.Field()
    # 商品名
    commodity_name = scrapy.Field()
    # 链接页数
    page = scrapy.Field()
    # 评论数据链接
    comment_data_link = scrapy.Field()
    # 评论数据
    comment_data = scrapy.Field()