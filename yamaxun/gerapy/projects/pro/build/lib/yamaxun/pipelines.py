# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from scrapy_redis import defaults, connection
# from scrapy_redis.pipelines import RedisPipeline, default_serialize


default_serialize = ScrapyJSONEncoder().encode

class YamaxunPipeline(object):
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
                 serialize_func=default_serialize):
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
        key = self.item_key(item, spider)
        data = self.serialize(item)
        self.server.rpush(key, data)
        print("哈哈哈哈哈啊哈哈哈")
        return item

    def item_key(self, item, spider):
        """Returns redis key based on given spider.

        Override this function to use a different key depending on the item
        and/or spider.

        """
        return self.key % {'spider': spider.name}






















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