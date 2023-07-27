# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import copy
import json

from itemadapter import ItemAdapter
from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from scrapy_redis import defaults, connection
# from scrapy_redis.pipelines import RedisPipeline, default_serialize


default_serialize = ScrapyJSONEncoder().encode
# 重写redis管道（默认的是scrapy_redis.pipelines.RedisPipeline）
class YamaxunPipeline():
    """Pushes serialized item into a redis list/queue

        Settings
        --------
        REDIS_ITEMS_KEY : str
            Redis key where to store items.
        REDIS_ITEMS_SERIALIZER : str
            Object path to serializer function.

        """

    def __init__(self, server,
                 key=defaults.PIPELINE_KEY,
                 serialize_func=default_serialize,
                 # 自己新增代码
                 comments_key=defaults.COMMENTS_KEY,
                 ):
        """Initialize pipeline.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        key : str
            Redis key where to store items.
        serialize_func : callable
            Items serializer function.

        """
        self.server = server
        self.key = key
        self.serialize = serialize_func
        # 自己新增代码
        self.comments_key = comments_key

    @classmethod
    def from_settings(cls, settings):
        params = {
            'server': connection.from_settings(settings),
        }
        if settings.get('REDIS_ITEMS_KEY'):
            params['key'] = settings['REDIS_ITEMS_KEY']
        if settings.get('REDIS_ITEMS_SERIALIZER'):
            params['serialize_func'] = load_object(
                settings['REDIS_ITEMS_SERIALIZER']
            )

        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        # 原来key
        key = self.item_key(item, spider)
        data = self.serialize(item)

        # 评论key
        comments_key = self.item_key(item, spider)
        # 深层拷贝，作用：去重
        copy_data = copy.deepcopy(data)
        # 放到redis里的数据都是字符串，这里转json格式，获取[‘type’]属性
        data_json = json.loads(copy_data)
        data_type = data_json['type']
        # 判断数据类型，拦截数据进行数据分类
        # 普通商品数据
        if data_type == 'Product_data':
            # 去重
            # 将数据以集合（set）的方式，不用列表（list）的方式添加到redis，
            # set的添加方法sadd，list的添加方法rpush
            # 两者区别就是set不会允许相同的数据存入，也就是自动去重，list不行
            self.server.sadd(key,copy_data)

            # # 去重
            # # 查询redis数据去重的列表(如果没有这个列表会返回空[])
            # key_dict = self.server.lrange(key,0,-1)
            # # redis查询出的数据是bytes格式，要转成utf-8格式(形成一个字典)，不然无法比对()
            # # 其实可以直接将bytes转成字符串，这里为了不忘记还可以转成utf-8获得字典
            # for Product_data_i, Product_data_k in enumerate(key_dict):
            #     key_dict[Product_data_i] = Product_data_k.decode('utf-8')
            # # 将字典转字符串（可以同类型对比数据）
            # key_dict_str = str(key_dict)
            # # 如果商品名字符串没有在字典字符串里则添加到数据库（准确应该添加id，这里先用商品名）
            # if data_json['commodity_name'] not in key_dict_str:
            #     self.server.rpush(key, copy_data)
        # 评论数据
        else:
            # 去重
            aa = self.server.sadd(comments_key, copy_data)
            print(aa)

        # 原来的代码
        # self.server.rpush(key, data)
        return item

    # 为键命名
    def item_key(self, item, spider):
        """Returns redis key based on given spider.

        Override this function to use a different key depending on the item
        and/or spider.

        """
        # 修改代码
        item_type = item['type']
        # 判断数据类型，拦截数据进行数据分类
        if item_type == 'Product_data':
            # 普通商品数据
            return self.key % {'spider': spider.name}
        else:
            # 评论数据
            return self.comments_key % {'spider': spider.name}


        #原来代码
        # return self.key % {'spider': spider.name}










# class YamaxunPipeline:
#     def open_spider(self, spider):
#         if spider.name == "amazon":
#             self.file = open(spider.name + ".json", 'w', encoding='utf-8')
#
#     def process_item(self, item, spider):
#         if spider.name == "amazon":
#             item = dict(item)
#             data = json.dumps(item, ensure_ascii=False) + ',\n'
#             self.file.write(data)
#         return item
#
#     def close_spider(self, spider):
#         if spider.name == "amazon":
#             self.file.close()