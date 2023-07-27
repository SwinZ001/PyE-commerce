import copy
import json

import re
from pprint import pprint
from time import sleep

import scrapy


from yamaxun.items import YamaxunItem, commentItem
from scrapy_redis.spiders import RedisSpider

# scrapy-redis原码路径在项目路径下/External Libraries/Python 3.9(pythonProject)/site-packages/scrapy-redis
class AliexpressSpider(RedisSpider):
    name = 'aliexpress'
    # allowed_domains = ['aliexpress.com']
    # start_urls = ['https://www.aliexpress.com/all-wholesale-products.html?spm=a2g0o.productlist.0.0.456b3afbURcglh']
    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(AliexpressSpider,self).__init__(*args,**kwargs)

    def make_requests_from_url(self, url):
        # 初始化商品数组，存放商品字典
        item = YamaxunItem()
        item['type'] = 'Product_data'
        item['startUrl'] = url
        return scrapy.Request(url,
                              dont_filter=True,
                              meta={'item': copy.deepcopy(item)}
                              )

    def parse(self, response):
        item = response.meta['item']

        All_Categories = response.xpath('//*[@class="cg-main"]/div')
        for Categories in All_Categories:
            Categories_link = response.urljoin(Categories.xpath('./h3/a/@href')[0].extract())
            Categories_name = Categories.xpath('./h3/a/text()')[0].extract()
            item['big_classification_link'] = Categories_link
            item['big_classification_text'] = Categories_name
            # 缩小范围用于测试(女装)
            if "100003109" in Categories_link:
                yield scrapy.Request(
                    url=item['big_classification_link'],
                    callback=self.get_pages,
                    meta={'item': copy.deepcopy(item)},
                    dont_filter=True
                    )

    # 获取页数链接
    def get_pages(self, response):
        item = response.meta['item']
        # 解析页面文件
        patter = re.compile("window.runParams = (.*);")
        commodity_htmldata = patter.findall(response.text)[1]
        commodity_json_data = json.loads(commodity_htmldata)

        # 获取总页数
        pageSize = commodity_json_data['pageInfo']['pageSize']
        print(pageSize)
        # # SortType菜单筛选参数，排序，销量什么的
        # # 根据销量SortType=total_tranpro_desc（页数从1开始，0和1是同一页）
        # for page in range(1, int(pageSize) + 1):
        #     page_link = item['big_classification_link'] + '?SortType=total_tranpro_desc&page=' + str(page)
        #     item['page_link'] = page_link
        #     yield scrapy.Request(
        #         url=item['page_link'],
        #         callback=self.get_commodity_link,
        #         meta={'item': copy.deepcopy(item)},
        #         dont_filter=True
        #     )
        # 缩小范围只取一页用于测试
        # 根据销量
        for page in range(1,3):
            print(item['big_classification_link'])
            page_link = item['big_classification_link'] + '?SortType=total_tranpro_desc&page=' + str(page)
            item['page_link'] = page_link
            yield scrapy.Request(
                url=item['page_link'],
                callback=self.get_commodity_link,
                meta={'item': copy.deepcopy(item)},
                dont_filter=True
            )


    # 获取商品数据链接
    def get_commodity_link(self, response):
        item = response.meta['item']
        # 解析页面文件
        patter = re.compile("window.runParams = (.*);")
        commodity_htmldata = patter.findall(response.text)[1]
        commodity_json_data = json.loads(commodity_htmldata)

        # 获取商品数量
        commodity_content = commodity_json_data['mods']['itemList']['content']
        # 获取productId构建商品详情url
        for commodity_num in commodity_content:
            productId = commodity_num['productId']
            commodity_link = 'https://www.aliexpress.com/item/' + str(productId) + '.html'
            item['commodity_link'] = commodity_link
            yield scrapy.Request(
                url=item['commodity_link'],
                callback=self.get_commodity_data,
                meta={'item': copy.deepcopy(item)},
                # dont_filter=False
                dont_filter=True
            )

            # # ///////////////////scrapy yield后还可执行，异步获取评论数据///////////////////////////////////////
            # item2 = commentItem()
            #
            # item2['type'] = 'Product_Review_Data'
            # # 获取商品名(根据商品名查找对应评论)
            # commodity_name = commodity_num['title']['displayTitle']
            # item2['commodity_name'] = commodity_name
            #
            # # 构建评论数据链接获取评论数据(当地评论请求是get请求，只能看到当地评论数据，全部评论数据是一个post，要构建参数之后使用scrapy.FormRequest方法)
            # ownerMemberId = commodity_num['store']['aliMemberId']
            # productId = commodity_num['trace']['utLogMap']['x_object_id']
            # # 方便传递下页用
            # id_data = []
            # id_data.append(ownerMemberId)
            # id_data.append(productId)
            #
            # # 构建评论数据链接
            # comment_data_link = 'https://feedback.aliexpress.com/display/productEvaluation.htm'
            #
            # params = {'ownerMemberId': str(ownerMemberId),
            #           'memberType': 'seller',
            #           'productId': productId,
            #           # 需要可在商品详情获取，不过这里不需要
            #           'companyId': '',
            #           'evaStarFilterValue': 'all Stars',
            #           'evaSortValue': 'sortlarest@feedback',
            #           'page': '1',
            #           'currentPage': '0',
            #           'startValidDate': '',
            #           'i18n': 'true',
            #           'withPictures': 'false',
            #           'withAdditionalFeedback': 'false',
            #           'onlyFromMyCountry': 'false',
            #           'version': '',
            #           'isOpened': 'true',
            #           'translate': 'Y',
            #           # 是否跳转到顶部，false代表跳转，true代表不跳转,为了获取顶部评星数据,这里是为了评论数据所以不跳转，不过第一页默认false，只需取第一页即可
            #           'jumpToTop': 'false',
            #           'v': '2'
            #           }
            #
            # yield scrapy.FormRequest(url=comment_data_link,
            #                          callback=self.get_comment_link,
            #                          formdata=params,
            #                          meta={'item2': copy.deepcopy(item2), 'id_data': copy.deepcopy(id_data)},
            #                          dont_filter=True)




    # def parse(self, response):
    # 获取商品详情数据
    def get_commodity_data(self, response):
        item = response.meta['item']

        data_obj = response.text

# \\\\\\\\\\# 详情界面布局有些商品是不同的(所以要捕获异常)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        try:
            # 第一种方法（data这些字段没有加“”，无法解析json，所以先直接匹配data节点的数据，其他有需要在用这种方法）
            # # 第一次清洗
            # # "window.runParams = (.*);"匹配不到，因为数据有很多换行符，先匹配出有空格的数据(两种)
            # 一种
            # patter2 = re.compile('dataToReturn = ([\s\S]*)};return dataToReturn;')
            # 二种
            # patter2 = re.compile("window.runParams = (.\s.*\s.*\s.*\s.*\s.*)")
            # commodity_htmldata = patter2.findall(response.text)[0]
            #
            # # 第二次清洗
            # # 再次匹配现有数据的换行符，去掉，得到最终数据
            # patter3 = re.compile("(\s)")
            # commodity_htmldata1 = patter3.sub("", commodity_htmldata)
            # print(commodity_htmldata1)
            #
            # # # 第三次清洗(不用这步，因为转换json文件后会自动消除转义字符‘\’符号，放这只是为了记住)
            # # # 解析页面文件,替换掉原文件所有‘\’符号，替换匹配用‘\\\\’来匹配‘\’符号）
            # # patter = re.compile("\\\\")
            # # commodity_htmldata2 = patter.sub("", commodity_htmldata1)
            # # print(commodity_htmldata2)

            # 第二种方法（直接匹配data）
            # 第一次清洗
            patter = re.compile("data: (.*),")
            commodity_htmldata = patter.findall(data_obj)[0]
            # 匹配数据转为json
            commodity_json_data = json.loads(commodity_htmldata)
            # 解析数据

            # 获取商品名
            commodity_name = commodity_json_data['titleModule']['subject']
            item['commodity_name'] = commodity_name

            # 获取销量(int)
            tradeCount = commodity_json_data['titleModule']['tradeCount']
            item['historical_sold'] = tradeCount

            # 获取折扣# 界面没有销量星级都会返回0和0.0，但是没有折扣不会返回0，会报错
            try:
                discount = commodity_json_data['priceModule']['discountRatioTips']
                item['discount'] = discount
            except:
                item['discount'] = '-0%'

            # 获取星级(转数字)星级是评论星级，没有评论星级为0.0
            evarageStar = float(commodity_json_data['titleModule']['feedbackRating']['evarageStar'])
            item['rating_star'] = evarageStar

            # 商品图片
            image_url_list = commodity_json_data['imageModule']['imagePathList']
            item['commodity_Imge_link'] = image_url_list

            # 商品规格
            attributes_list = []
            attributes_dict = {}
            attributes = commodity_json_data['specsModule']['props']
            for attribute in attributes:
                attribute_name = attribute['attrName']
                attribute_value = attribute['attrValue']
                attributes_dict[attribute_name] = attribute_value
            attributes_list.append(attributes_dict)
            item['attributes'] = attributes_list

            # 商品描述（没有规律，直接给链接）
            description = commodity_json_data['descriptionModule']['descriptionUrl']
            item['description'] = description

            # 店铺链接(获取的链接不标准无法访问，通过replace()函数替换字符构造标准链接)
            old_store_data_link = commodity_json_data['storeModule']['storeURL']
            store_data_link = old_store_data_link.replace('//www.', 'https://mingheclothes.')
            item['store_data_link'] = store_data_link

            # 店铺数据
            store_data_list = {}
            # 店铺名
            store_name = commodity_json_data['storeModule']['storeName']
            store_data_list['store_name'] = store_name
            # 出货地
            shipment_Place = commodity_json_data['storeModule']['countryCompleteName']
            store_data_list['shipment_Place'] = shipment_Place
            # 粉丝数
            follower_count = commodity_json_data['storeModule']['followingNumber']
            store_data_list['follower_count'] = follower_count
            # 开店年份
            openTime = commodity_json_data['storeModule']['openTime']
            store_data_list['openTime'] = openTime
            # # 为了与其他平台数据统一，一下先不要
            # # 商店正利率（正为好，负为不好）
            # positiveRate = commodity_json_data['storeModule']['positiveRate']
            # store_data_list['positiveRate'] = positiveRate

            # 保存店铺数据
            item['store_data'] = store_data_list

            # 获取sku数据
            # 存放所有sku的列表
            sku_list = []
            # 通过捕异常来判断有无sku列表
            # 有sku时
            try:
                # 属性大小（有多少个属性）
                productSKUPropertyList = commodity_json_data['skuModule']['productSKUPropertyList']
                # 属性sku搭配对应价格数量（有多少个属性价格）
                skuPriceList = commodity_json_data['skuModule']['skuPriceList']

                # 根据属性对应价格数量循环
                for skuPrice in skuPriceList:
                    # 存sku的字典
                    sku_And_price_dict = {}

                    # sku结合码字符串14:13978534;5:4645
                    # 给每个结合码最后都加上#，用于匹配准确
                    skuAttr = skuPrice['skuAttr']
                    # 以;进行分割形成数组
                    skuAttr_dict = skuAttr.split(';')
                    # 将数据循环重组+‘#’
                    for i, k in enumerate(skuAttr_dict):
                        skuAttr_dict[i] = k + '#'
                    # 最后将重组数据后的数组以','进行合并，形成新的字符串14:13978534#,5:4645#(z注意;变成了,不过没影响)
                    new_skuAttr = ','.join(skuAttr_dict)

                    # 根据属性大小（有多少个属性）循环
                    for productSKUProperty in productSKUPropertyList:
                        # 获取属性id和属性
                        skuPropertyId = str(productSKUProperty['skuPropertyId'])
                        skuPropertyName = productSKUProperty['skuPropertyName']
                        # 获取属性值大小
                        skuPropertyValues = productSKUProperty['skuPropertyValues']
                        # 根据属性值大小循环（一个属性对应多个属性值）
                        for skuPropertyValue in skuPropertyValues:
                            # 获取属性值id和属性值
                            # 给单个sku码结尾加上#，避免因为字节大小问题匹配重复（如：14:13978534和14:13，这样会匹配到两个14:13）
                            propertyValueId = str(skuPropertyValue['propertyValueId']) + '#'
                            propertyValueName = skuPropertyValue['propertyValueDisplayName']
                            # 结合属性id和属性值id去匹配价格对应搭配的sku，再把属性id和属性值id替换成对应的属性和属性值，形成整体的sku字典
                            if skuPropertyId + ':' + propertyValueId in new_skuAttr:
                                # 单个sku，每循环一次就匹配取出一个sku,直到价格的所有sku匹配完毕
                                sku_And_price_dict[skuPropertyName] = propertyValueName

                    # 获取sku搭配价格(有两种，一种是打折前skuAmount，一种是打折后skuActivityAmount，有些没打折的会出错，所以要捕获错误)
                    # 打折后价钱
                    # 有些没打折
                    try:
                        discount_Price = skuPrice['skuVal']['skuActivityAmount']['value']
                    # 没打折等于原价
                    except:
                        discount_Price = skuPrice['skuVal']['skuAmount']['value']
                    sku_And_price_dict['discount_Price'] = discount_Price
                    # 原价
                    original_Price = skuPrice['skuVal']['skuAmount']['value']
                    sku_And_price_dict['original_Price'] = original_Price

                    # sku库存
                    inventory = skuPrice['skuVal']['inventory']
                    sku_And_price_dict['inventory'] = inventory

                    # 循环结束再输出完整的sku字典，再把完整的sku添加到sku列表
                    sku_list.append(sku_And_price_dict)
                item['sku_list'] = sku_list

            # 无sku时
            except:
                sku_And_price_dict = {}

                # sku
                sku_And_price_dict['skuPropertyName'] = '无sku，只有一个'

                # 属性对应价格数量（有多少个属性价格）
                skuPriceList = commodity_json_data['skuModule']['skuPriceList']
                # 获取sku搭配价格(有两种，一种是打折前skuAmount，一种是打折后skuActivityAmount，有些没打折的会出错，所以要捕获错误)
                # 打折后价钱
                # 有些没打折
                try:
                    discount_Price = skuPriceList[0]['skuVal']['skuActivityAmount']['value']
                # 没打折等于原价
                except:
                    discount_Price = skuPriceList[0]['skuVal']['skuAmount']['value']
                sku_And_price_dict['discount_Price'] = discount_Price
                # 原价
                original_Price = skuPriceList[0]['skuVal']['skuAmount']['value']
                sku_And_price_dict['original_Price'] = original_Price

                # sku库存（int）
                inventory = skuPriceList[0]['skuVal']['inventory']
                sku_And_price_dict['inventory'] = inventory

                # 把完整的sku添加到sku列表
                sku_list.append(sku_And_price_dict)
                item['sku_list'] = sku_list


            yield item

# \\\\\\\\\\# 速卖通不同布局商品详情页\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        except:

            # 匹配数据
            patter = re.compile("data: (.*)}")
            commodity_htmldata = patter.findall(data_obj)[0]
            # 匹配数据转为json
            new_commodity_json_data = json.loads(commodity_htmldata)
            # 解析数据

            # 获取商品名
            commodity_name = new_commodity_json_data['data']['titleBanner_2440']['fields']['subject']
            item['commodity_name'] = commodity_name

            # 获取销量
            tradeCount = int(new_commodity_json_data['data']['shareHeader_2242']['fields']['formatTradeCount'])
            item['historical_sold'] = tradeCount

            # 获取折扣# 界面没有销量星级都会返回0和0.0，但是没有折扣不会返回0，会报错
            try:
                discount = new_commodity_json_data['data']['price_2256']['fields']['discountRatioTips']
                item['discount'] = discount
            except:
                item['discount'] = '-0%'

            # 获取星级(转数字)（正常界面星级是评论和界面都有显示，另一种界面产品星级只有在评论界面才显示，所以要获取评论才能获取星级，没评论星级为0）
            # 获取星级(转数字)星级是评论星级，没有评论星级为0.0
            evarageStar = '新界面不显示星级'
            item['rating_star'] = evarageStar

            # 获取商品图片
            image_url_list = new_commodity_json_data['data']['imageView_2247']['fields']['imageList']
            item['commodity_Imge_link'] = image_url_list

            # 获取商品规格
            attributes_list = []
            attributes_dict = {}
            attributes = new_commodity_json_data['data']['specsInfo_2263']['fields']['specs']
            for attribute in attributes:
                attribute_name = attribute['attrName']
                attribute_value = attribute['attrValue']
                attributes_dict[attribute_name] = attribute_value
            attributes_list.append(attributes_dict)
            item['attributes'] = attributes_list

            # 获取商品描述
            description = new_commodity_json_data['data']['description_2253']['fields']['detailDesc']
            item['description'] = description

            # 店铺链接
            old_store_data_link = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['storeURL']
            store_data_link = old_store_data_link.replace('//www.', 'https://mingheclothes.')
            item['store_data_link'] = store_data_link

            # 店铺数据
            store_data_list = {}
            # 店铺名
            store_name = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['storeName']
            store_data_list['store_name'] = store_name
            # 出货地
            shipment_Place = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['countryCompleteName']
            store_data_list['shipment_Place'] = shipment_Place
            # 粉丝数
            follower_count = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['followingNumber']
            store_data_list['follower_count'] = follower_count
            # 开店年份
            openTime = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['openTime']
            store_data_list['openTime'] = openTime
            # # 为了与其他平台数据统一，一下先不要
            # # 商店正利率（正为好，负为不好）
            # positiveRate = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['positiveRate']
            # store_data_list['positiveRate'] = positiveRate

            # 保存店铺数据
            item['store_data'] = store_data_list


            # 获取sku数据
            # 存放所有sku的列表
            sku_list = []
            # 通过捕异常来判断有无sku列表
            # 有sku时
            try:
                # 属性对应价格数量（有多少个属性价格）
                skuPriceList = new_commodity_json_data['data']['sku_2257']['fields']['skuList']
                # 属性大小（有多少个属性）
                productSKUPropertyList = new_commodity_json_data['data']['sku_2257']['fields']['propertyList']

                # 根据属性对应价格数量循环
                for skuPrice in skuPriceList:
                    # 存sku的字典
                    sku_And_price_dict = {}

                    # sku结合码字符串14:13978534;5:4645
                    # 给每个结合码最后都加上#，用于匹配准确
                    skuAttr = skuPrice['skuAttr']
                    # 以;进行分割形成数组
                    skuAttr_dict = skuAttr.split(';')
                    # 将数据循环重组+‘#’
                    for i, k in enumerate(skuAttr_dict):
                        skuAttr_dict[i] = k + '#'
                    # 最后将重组数据后的数组以','进行合并，形成新的字符串14:13978534#,5:4645#(z注意;变成了,不过没影响)
                    new_skuAttr = ','.join(skuAttr_dict)

                    # 根据属性大小（有多少个属性）循环
                    for productSKUProperty in productSKUPropertyList:
                        # 获取属性id和属性
                        skuPropertyId = str(productSKUProperty['skuPropertyId'])
                        skuPropertyName = productSKUProperty['skuPropertyName']

                        # 获取属性值大小
                        skuPropertyValues = productSKUProperty['skuPropertyValues']
                        # 根据属性值大小循环（一个属性对应多个属性值）
                        for skuPropertyValue in skuPropertyValues:
                            # 获取属性值id和属性值
                            # propertyValueId = str(skuPropertyValue['propertyValueId']) + '#'
                            # propertyValueId有时不准，所以用propertyValueIdLong
                            # 给单个sku码结尾加上#，避免因为字节大小问题匹配重复（如：14:13978534和14:13，这样会匹配到两个14:13）
                            propertyValueIdLong = str(skuPropertyValue['propertyValueIdLong']) + '#'
                            # # 实际值（对不上界面，所以用界面显示值）
                            # propertyValueName = skuPropertyValue['propertyValueName']
                            # 界面显示值（以这个为准）
                            propertyValueDisplayName = skuPropertyValue['propertyValueDisplayName']
                            # 结合属性id和属性值id去匹配价格对应搭配的sku，再把属性id和属性值id替换成对应的属性和属性值，形成整体的sku字典
                            if skuPropertyId + ':' + propertyValueIdLong in new_skuAttr:
                                # 单个sku，每循环一次就匹配取出一个sku,直到价格的所有sku匹配完毕
                                sku_And_price_dict[skuPropertyName] = propertyValueDisplayName

                    # 获取sku搭配价格(有两种，一种是打折前skuAmount，一种是打折后skuActivityAmount，有些没打折的会出错，所以要捕获错误)
                    # 打折后价钱
                    # 有些没打折
                    try:
                        discount_Price = skuPrice['skuVal']['skuActivityAmount']['value']
                    # 没打折等于原价
                    except:
                        discount_Price = skuPrice['skuVal']['skuAmount']['value']
                    sku_And_price_dict['discount_Price'] = discount_Price
                    # 原价
                    original_Price = skuPrice['skuVal']['skuAmount']['value']
                    sku_And_price_dict['original_Price'] = original_Price

                    # sku库存
                    inventory = skuPrice['skuVal']['inventory']
                    sku_And_price_dict['inventory'] = inventory

                    # 循环结束再输出完整的sku字典，再把完整的sku添加到sku列表
                    sku_list.append(sku_And_price_dict)
                item['sku_list'] = sku_list

            # 无sku时
            except:
                sku_And_price_dict = {}

                # sku
                sku_And_price_dict['skuPropertyName'] = '无sku，只有一个'

                # 属性对应价格数量（有多少个属性价格）
                skuPriceList = new_commodity_json_data['data']['sku_2257']['fields']['skuList']
                # 获取sku搭配价格(有两种，一种是打折前skuAmount，一种是打折后skuActivityAmount，有些没打折的会出错，所以要捕获错误)
                # 打折后价钱
                # 有些没打折
                try:
                    discount_Price = skuPriceList[0]['skuVal']['skuActivityAmount']['value']
                # 没打折等于原价
                except:
                    discount_Price = skuPriceList[0]['skuVal']['skuAmount']['value']
                sku_And_price_dict['discount_Price'] = discount_Price
                # 原价
                original_Price = skuPriceList[0]['skuVal']['skuAmount']['value']
                sku_And_price_dict['original_Price'] = original_Price

                # sku库存
                inventory = skuPriceList[0]['skuVal']['inventory']
                sku_And_price_dict['inventory'] = inventory

                # 把完整的sku添加到sku列表
                sku_list.append(sku_And_price_dict)
                item['sku_list'] = sku_list

            yield item






# ///////////////////////上文提交普通商品数据，下文提交评论数据，单独在数据库放一个健，以下新建在items.py新建一个新的存放评论数据的item//////////////////////////


    # 获取评论页数链接(将这个函数作为一个循环体，一页一页的爬取评论，)
    def get_comment_link(self, response):
        id_data = response.meta['id_data']
        item2 = response.meta['item2']

        # 有评论
        yes_feedback_len = len(response.xpath('//*[@class="feedback-list-wrap"]'))
        # 无评论
        no_feedback_len = len(response.xpath('//*[@class="no-feedback wholesale-product-feedback"]'))

        # 根据有无节点判断有没有评论
        if yes_feedback_len != 0:
            print('1111111111111111111111111111111')

            # 获取评论节点（用‘//’跳过包含字符串和html嵌套的节点，直接取em）
            comment_total = int(response.xpath('//*[@class="f-star-dropdown"]//em/text()')[0].extract())
            # 每页评论数量
            comment_text_node = response.xpath('//*[@class="buyer-feedback"]')
            comment_len = len(comment_text_node)
            # 页数
            pageSize = comment_total / comment_len
            # 判断页数是否有余数（是否是整型），没余数：页数=页数，有余数：页数=页数+1
            if isinstance(pageSize, int):
                new_pageSize = pageSize
            else:
                new_pageSize = int(pageSize) + 1

            print(comment_total, str(comment_len), str(pageSize), str(new_pageSize))

            # 循环构建评论链接
            # for page in range(1, 5):
            for page in range(1, new_pageSize + 1):
                item2['page'] = page
                # 构建评论数据链接
                comment_data_link = 'https://feedback.aliexpress.com/display/productEvaluation.htm'
                item2['comment_data_link'] = comment_data_link

                params = {'ownerMemberId': str(id_data[0]),
                          'memberType': 'seller',
                          'productId': str(id_data[1]),
                          # 需要可在商品详情获取，不过这里不需要
                          'companyId': '',
                          'evaStarFilterValue': 'all Stars',
                          'evaSortValue': 'sortlarest@feedback',
                          'page': str(page),
                          'currentPage': '',
                          'startValidDate': '',
                          'i18n': 'true',
                          'withPictures': 'false',
                          'withAdditionalFeedback': 'false',
                          'onlyFromMyCountry': 'false',
                          'version': '',
                          'isOpened': 'true',
                          'translate': 'Y',
                          # 是否跳转到顶部，false代表跳转，true代表不跳转,为了获取顶部评星数据,这里是为了评论数据所以不跳转，不过第一页默认false，只需取第一页即可
                          'jumpToTop': 'false',
                          'v': '2'
                          }
                # if page == 1:
                # 根据new_pageSize来判断有无评论数据，用于传递数据到下一个方法后进行数据提交判断
                yield scrapy.FormRequest(url=comment_data_link,
                                         callback=self.get_comment_data,
                                         formdata=params,
                                         meta={'item2': copy.deepcopy(item2),'page':str(page)},
                                         dont_filter=True)
        # 商品没评论直接提交数据
        elif no_feedback_len != 0:
            print('2222222222222222222222222222222')
            item2['page'] = 0
            item2['comment_data_link'] = response.url
            item2['comment_data'] = '该商品暂时没有评论'
            yield item2





    def get_comment_data(self, response):
        item2 = response.meta['item2']

        comment_list_node_len = len(response.xpath('//*[@class="feedback-list-wrap"]//dt[@class="buyer-feedback"]'))
        # 需要用range，直接用列表循环的话会重复
        for comment_i in range(1,comment_list_node_len+1):
            # .extract_first()没有值会返回none,   [0].extract()没有值会报错
            comment = response.xpath('//*[@class="feedback-list-wrap"]/div[' + str(comment_i) + ']//dt/span[1]/text()').extract_first()
            if comment != None:
                item2['comment_data'] = comment
            else:
                item2['comment_data'] = '该用户没有评论'

            yield item2











# 评论测试
#     def parse(self, response):
#         item2 = commentItem()
#
#         item2['type'] = 'Product_Review_Data'
#
#
#         data_obj = response.text
#
#         # \\\\\\\\\\# 详情界面布局有些商品是不同的(所以要捕获异常)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#         try:
#
#             # 匹配数据
#             patter = re.compile("data: (.*),")
#             commodity_htmldata = patter.findall(data_obj)[0]
#             # 匹配数据转为json
#             commodity_json_data = json.loads(commodity_htmldata)
#             # 解析数据
#             # 构建评论数据链接获取评论数据(当地评论请求是get请求，只能看到当地评论数据，全部评论数据是一个post，要构建参数之后使用scrapy.FormRequest方法)
#             ownerMemberId = commodity_json_data['storeModule']['sellerAdminSeq']
#             productId = commodity_json_data['actionModule']['productId']
#
#         # \\\\\\\\\\# 速卖通不同布局商品详情页\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#         except:
#             # 匹配数据
#             patter = re.compile("data: (.*)}")
#             commodity_htmldata = patter.findall(data_obj)[0]
#             # 匹配数据转为json
#             new_commodity_json_data = json.loads(commodity_htmldata)
#             # 解析数据
#             # 构建评论数据链接获取评论数据(当地评论请求是get请求，只能看到当地评论数据，全部评论数据是一个post，要构建参数之后使用scrapy.FormRequest方法)
#             ownerMemberId = new_commodity_json_data['data']['coupon_2261']['fields']['adminSeq']
#             productId = new_commodity_json_data['data']['headerInfo_2442']['fields']['_for_header_info']['storeModule']['productId']
#
#
#
#         # 方便传递下页用
#         id_data = []
#         id_data.append(ownerMemberId)
#         id_data.append(productId)
#
#         # 构建评论数据链接
#         comment_data_link = 'https://feedback.aliexpress.com/display/productEvaluation.htm'
#
#         params = {'ownerMemberId': str(ownerMemberId),
#                   'memberType': 'seller',
#                   'productId': str(productId),
#                   # 需要可在商品详情获取，不过这里不需要
#                   'companyId': '',
#                   'evaStarFilterValue': 'all Stars',
#                   'evaSortValue': 'sortlarest@feedback',
#                   'page': '1',
#                   'currentPage': '0',
#                   'startValidDate': '',
#                   'i18n': 'true',
#                   'withPictures': 'false',
#                   'withAdditionalFeedback': 'false',
#                   'onlyFromMyCountry': 'false',
#                   'version': '',
#                   'isOpened': 'true',
#                   'translate': 'Y',
#                   # 是否跳转到顶部，false代表跳转，true代表不跳转,为了获取顶部评星数据,这里是为了评论数据所以不跳转，不过第一页默认false，只需取第一页即可
#                   'jumpToTop': 'false',
#                   'v': '2'
#                   }
#
#         yield scrapy.FormRequest(url=comment_data_link,
#                                  callback=self.get_comment_link,
#                                  formdata=params,
#                                  meta={'item2': copy.deepcopy(item2), 'id_data': copy.deepcopy(id_data)},
#                                  dont_filter=True)