import copy
import json
import re
import scrapy
from yamaxun.items import YamaxunItem
from scrapy_redis.spiders import RedisSpider


class KshouSpider(RedisSpider):
    name = 'Kshou'
    # allowed_domains = ['kuaishou.com']
    # start_urls = ['http://kuaishou.com/']
    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(KshouSpider,self).__init__(*args,**kwargs)

    # def start_requests(self):
    #     headers = {
    #         'Accept': 'application/vnd.com.amazon.api+json; type="cart.add-items/v1"',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'Accept-Language': 'zh-CN',
    #         'Connection': 'keep-alive',
    #         'Content-Length': '100',
    #         'Content-Type': 'application/vnd.com.amazon.api+json; type="cart.add-items.request/v1"',
    #         # 需要headers和headers2同Cookie才可成功
    #         'Cookie': 'session-id=136-6298940-5529567; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=132-4276056-1407021; skin=noskin; session-token="Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="',
    #         'Host': 'data.amazon.com',
    #         'Origin': 'https://www.amazon.com',
    #         'Referer': 'https://www.amazon.com/',
    #         'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': 'Windows',
    #         'Sec-Fetch-Dest': 'empty',
    #         'Sec-Fetch-Mode': 'cors',
    #         'Sec-Fetch-Site': 'same-site',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    #         'x-api-csrf-token': '1@g8AwvXtYMh39qf0WE+SzVEQyclVOSBU+AawanZlDfsubAAAAAQAAAABjgUGUcmF3AAAAABVX8CwXqz42z+J7i/ABqA==@NLD_Y47GLU'
    #     }

    # def make_requests_from_url(self, url):
    #     # 初始化商品数组，存放商品字典
    #     item = YamaxunItem()
    #     item['startUrl'] = url
    #
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    #         'Cookie': 'kpf=PC_WEB; kpn=KUAISHOU_VISION; clientid=3; did=web_821df3db85bd3a901667d87961f2094b; ktrace-context=1|MS43NjQ1ODM2OTgyODY2OTgyLjE2NjE1NTQyLjE2NjQ0NzM0MDc3ODQuMTkzMDg=|MS43NjQ1ODM2OTgyODY2OTgyLjIxMzM5OTkyLjE2NjQ0NzM0MDc3ODQuMTkzMDk=|0|graphql-server|webservice|false|NA; client_key=65890b29; userId=1632901381; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABaTTKJQdzDqYWmidGw4KVBhCaIeTr8Q1Q66ljzQlCMx3bV415_kvzAxXIEUXlMMge2cW4yOf6HeG-JU9p4vIT-CUJdfrmzgZEk_AYCsgihxpxIYMzp0cRMP9TjLmpJpJ77N31We3wqs-XR9T5jvRMQaKff7_rF3Se3tG0RQL1FmzhPLajetOgvZ37zwSrsqYKQgOTtYoVonaSfUF0MwG9pBoS5dGNQ2tN9j6L3QVO7fJXKiWdIiBAaPInmRNr1Q0K0mLa7AV9ZzO7bs6dlqGsc6-6OU9orygFMAE; kuaishou.server.web_ph=3788d68c0d7e8976cadee146860475eef527',
    #         'content-type': 'application/json'
    #     }
    #     params = {"operationName": "visionSearchPhoto",
    #               "query": "fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionSearchPhoto($keyword: String, $pcursor: String, $searchSessionId: String, $page: String, $webPageArea: String) {\n  visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    searchSessionId\n    pcursor\n    aladdinBanner {\n      imgUrl\n      link\n      __typename\n    }\n    __typename\n  }\n}\n",
    #               "variables": {"keyword": '假面骑士', "pcursor": '0', "page": "search",
    #                             "searchSessionId": "MTRfMTYzMjkwMTM4MV8xNjY0NDc4OTg5NTU5X-WBh-mdoumqkeWjq180OTE5"},
    #               }
    #
    #     return scrapy.Request(url,
    #                           method='POST',
    #                           headers=headers,
    #                           body=json.dumps(params),
    #                           dont_filter=True,
    #                           meta={'item': copy.deepcopy(item)},
    #                           )
    #
    # def parse(self, response):
    #     data_obj = response.json()
    #     print(data_obj)
    #     pass


    # # 一般来说，Get请求用Parameters，Post请求用Body Data。
    # # 精确的对于Post的说法是：
    # # 普通的post请求和上传接口，选择Parameters。
    # # json和xml点数据格式请求接口，选择Body
    # # 最后不行就用data
    # # 这是测试速卖通的post的Form请求(有 Form Data的要用scrapy.FormRequest方法，提交数据为字典的用上面的方法)
    # def make_requests_from_url(self, url):
    #     # 初始化商品数组，存放商品字典
    #     item = YamaxunItem()
    #     item['startUrl'] = url
    #
    #     params = {'ownerMemberId': '238742518',
    #               'memberType': 'seller',
    #               'productId': '4000206483343',
    #               'companyId': '',
    #               'evaStarFilterValue': 'all Stars',
    #               'evaSortValue': 'sortlarest@feedback',
    #               'page': '2',
    #               'currentPage': '',
    #               'startValidDate': '',
    #               'i18n': 'true',
    #               'withPictures': 'false',
    #               'withAdditionalFeedback': 'false',
    #               'onlyFromMyCountry': 'false',
    #               'version': '',
    #               'isOpened': 'true',
    #               'translate': 'Y',
    #               'jumpToTop': 'false',
    #               'v': '2'
    #               }
    #
    #     return scrapy.FormRequest(url=url, formdata=params, meta={'item': copy.deepcopy(item)}, dont_filter=True)
    #
    #
    # def parse(self, response):
    #     item = response.meta['item']
    #     comment_list_node = response.xpath('//*[@class="feedback-list-wrap"]//dt[@class="buyer-feedback"]')
    #
    #     comment_node = response.xpath('//*[@class="feedback-list-wrap"]/div[2]//dt/span[1]/text()').extract_first()
    #     print(len(comment_list_node), comment_node)
    #     for comment_node in range(len(comment_list_node)):
    #         comment_page = comment_node+1
    #         print(str(comment_page))
    #         comment_node = response.xpath('//*[@class="feedback-list-wrap"]/div[' + str(comment_page) + ']//dt/span[1]/text()').extract_first()
    #         print(comment_node)
    #         item['comment_data'] = comment_node
    #         item['type'] = 'Product_Review_Data'
    #         yield item



    # 亚马逊库存(有些headers加了某些参数会导致访问数据出错，所以要删除一些非必要参数，保留必要参数)
    def make_requests_from_url(self, url):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        # cookies = {
        #     'session-id': 'session-id=136-6298940-5529567',
        #     'session-id-time': '2082787201l',
        #     'i18n-prefs': 'USD',
        #     'lc-main': 'zh_CN',
        #     'sp-cdn': '"L5Z9:CN"',
        #     'ubid-main': '132-4276056-1407021',
        #     'skin': 'noskin',
        #     'session-token': 'Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="',
        # }
        return scrapy.Request(url=url,
                              headers=headers,
                              # cookies=cookies,
                              dont_filter=True,
                              )


    def parse(self, response):
        print(response.request.headers)
        # 获取库存
        aod_atc_csrf_token = response.xpath('//*[@id="aod-atc-csrf-token"]/@value')[0].extract().strip()
        # 点开查看所有购物选择，产品有多个商家多个价格库存，这里取第一个做测试。取别的可根据调整[0]获取
        data_aod_atc_action = response.xpath('//*[@id="aod-offer-list"]//span[@data-aod-atc-action]/@data-aod-atc-action')[0].extract().strip()
        data_aod_atc_action_json = json.loads(data_aod_atc_action)
        asin = data_aod_atc_action_json['asin']
        oid = data_aod_atc_action_json['oid']
        print(aod_atc_csrf_token, asin, oid)
        # cookies = {
        #     'session-id': 'session-id=136-6298940-5529567',
        #     'session-id-time': '2082787201l',
        #     'i18n-prefs': 'USD',
        #     'lc-main': 'zh_CN',
        #     'sp-cdn': '"L5Z9:CN"',
        #     'ubid-main': '132-4276056-1407021',
        #     'skin': 'noskin',
        #     'session-token': 'Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="',
        # }
        headers = {
            'Accept': 'application/vnd.com.amazon.api+json; type="cart.add-items/v1"',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN',
            'Content-Type': 'application/vnd.com.amazon.api+json; type="cart.add-items.request/v1"',
            'Cookie': 'session-id=136-6298940-5529567; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=132-4276056-1407021; skin=noskin; session-token="Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="',
            'Origin': 'https://www.amazon.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'x-api-csrf-token': aod_atc_csrf_token
            # 非必要参数
            # 'Connection': 'keep-alive',
            # Content-Length在scrapy中加了会访问不到数据返回500
            # 'Content-Length':'100',
            # 'Host': 'data.amazon.com',
            # 'Referer': 'https://www.amazon.com/',
            # 'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': 'Windows',
            # 'Sec-Fetch-Dest': 'empty',
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-site',
        }
        Add_Cart_params = {
            "items": [
                {"asin": asin,
                 "offerListingId": oid,
                 "quantity": 999,
                 "additionalParameters": {}
                 }
            ]
        }
        # 发起添加购物车请求进行商品添加购物车
        Add_Cart_url = 'https://data.amazon.com/api/marketplaces/ATVPDKIKX0DER/cart/carts/retail/items'
        yield scrapy.Request(Add_Cart_url,
                             method='POST',
                             body=json.dumps(Add_Cart_params),
                             headers=headers,
                             # cookies=cookies,
                             callback=self.add_Cart,
                             dont_filter=True
                             )

    def add_Cart(self, response):
        print(response.request.headers)
        print(response.text)