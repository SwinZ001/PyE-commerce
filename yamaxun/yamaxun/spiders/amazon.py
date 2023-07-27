import copy
import json
import re
import scrapy
from yamaxun.items import YamaxunItem
from scrapy_redis.spiders import RedisSpider

#
# 销量排行榜链接
# https://www.amazon.com/gp/bestsellers/ref=zg_bs_unv_pc_0_1
# 左侧隐藏菜单全部分类
# https://www.amazon.com/gp/navigation/ajax/generic.html?ajaxTemplate=hamburgerMainContent&pageType=Gateway&hmDataAjaxHint=1&navDeviceType=desktop&isSmile=0&isPrime=0&isBackup=false&hashCustomerAndSessionId=bbdc9cf40f547948a17d178518f5504c07530ff2&isExportMode=true&languageCode=zh_CN&environmentVFI=AmazonNavigationCards%2Fdevelopment%40B6099827072-AL2_x86_64&secondLayerTreeName=prm_digital_music_hawkfire%2Bkindle%2Bandroid_appstore%2Belectronics_exports%2Bcomputers_exports%2Bsbd_alexa_smart_home%2Barts_and_crafts_exports%2Bautomotive_exports%2Bbaby_exports%2Bbeauty_and_personal_care_exports%2Bwomens_fashion_exports%2Bmens_fashion_exports%2Bgirls_fashion_exports%2Bboys_fashion_exports%2Bhealth_and_household_exports%2Bhome_and_kitchen_exports%2Bindustrial_and_scientific_exports%2Bluggage_exports%2Bmovies_and_television_exports%2Bpet_supplies_exports%2Bsoftware_exports%2Bsports_and_outdoors_exports%2Btools_home_improvement_exports%2Btoys_games_exports%2Bvideo_games_exports%2Bgiftcards%2Bamazon_live%2BAmazon_Global
# 全部分类
# https://www.amazon.com/s?i=specialty-aps
class AmazonSpider(RedisSpider):
    name = 'amazon'
    # allowed_domains = ['amazon.cn']
    # start_urls = ['https://www.amazon.cn/s?srs=1546136071&bbn=1546134071&rh=n%3A1546134071&dc&qid=1651040484&ref=lp_1546136071_ex_n_1']

    redis_key = 'py21'

    def __init__(self,*args,**kwargs):
        domain = kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(AmazonSpider,self).__init__(*args,**kwargs)

    def make_requests_from_url(self, url):
        # 初始化商品数组，存放商品字典
        item = YamaxunItem()
        item['type'] = 'Product_data'
        item['startUrl'] = url
        # 设置cookies（一般直接设置请求头即可）
        # temp = 'session-id=134-2575988-2787004; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=131-6832861-0372514; '
        # cookies = {data.split("=")[0]: data.split("=")[-1] for data in temp.split('; ')}
        # # 一种是在middlewares设置，一种是在这里设置
        # 设置请求头（问题，如何返回中文）
        # 设置请求头
        # headers = {
        #     'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'zh-CN,zh;q=0.9',
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #
        # }
        return scrapy.Request(url,
                              # headers=headers,
                              # cookies=cookies,
                              dont_filter=True,
                              meta={'item': copy.deepcopy(item)}
                              )

    def parse(self, response):
        item = response.meta['item']
        # commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div/div[@class="sg-col-inner"]')
        # print(len(commodity_node_list))
        # for commodity_node in commodity_node_list:
        #     # 过滤推广商品
        #     filter_commodity_node = commodity_node.xpath('.//div[@class="a-row a-spacing-micro"]')
        #     if len(filter_commodity_node) == 0:
        #         # 要改成ref后所有字符清空
        #         patter = re.compile("/ref=\S+")
        #         commodity_link = patter.sub("", response.urljoin(commodity_node.xpath('.//h2/a/@href')[0].extract()))
        #         #不加?th=1&psc=1有些页面数据访问不到，所以统一加
        #         new_commodity_link = commodity_link.replace('/-/zh','') + '?th=1&psc=1'
        #         item['commodity_link'] = new_commodity_link
        #         if 'B0773ZY26F' in new_commodity_link or 'B07MFZXR1B' in new_commodity_link :
        #             yield scrapy.Request(
        #                 url=item['commodity_link'],
        #                 callback=self.parse2,
        #                 meta={'item': copy.deepcopy(item),'cookiejar': new_commodity_link},
        #                 dont_filter=True
        #             )
        commodity_link_dict = ['https://www.amazon.com/-/zh/dp/B09GJYM3R8?th=1&psc=1']
        for commodity_link in commodity_link_dict:
            new_commodity_link = commodity_link
            item['commodity_link'] = new_commodity_link
            yield scrapy.Request(
                url=item['commodity_link'],
                callback=self.parse2,
                meta={'item': copy.deepcopy(item),
                      'cookiejar': new_commodity_link},
                dont_filter=True
            )

    # # 获取一级链接
    # def parse(self, response):
    #     # 判断是否登录成功
    #     item = response.meta['item']
    #     # 存放类别id的列表
    #     category_id_dict = []
    #     # 排除重复的列表名字
    #     filter_classification_dict = ["women's fashion","men's fashion","girls' fashion","boys' fashion"]
    #     # 获取二级目录总链接,通过二级目录id一级目录链接
    #     # 5-27是全部商品分类，只获取全部商品分类
    #     for i in range(5,27):
    #         Secondary_directory_node = response.xpath('//*[@data-menu-id=' +str(i) + ']')
    #         # 大分类名称
    #         big_classification_text = Secondary_directory_node.xpath('./li[2]/div/text()')[0].extract().strip()
    #         item['big_classification_text'] = big_classification_text
    #         print(big_classification_text)
    #         # 获取链接
    #         li_node_list = Secondary_directory_node.xpath('./li/a')
    #         for li_node in li_node_list:
    #             # 因为女童时尚，男童时尚，女士时尚，男士时尚这几个类别子标签都是相互有的，所以为了与大标签区别，就把这些子标签的链接过滤掉
    #             classification_text_node = li_node.xpath('./text()')
    #             if len(classification_text_node) != 0:
    #                 classification_text = li_node.xpath('./text()')[0].extract().strip()
    #                 # 如果子标签名字没有在过滤列表里就获取链接
    #                 if classification_text not in filter_classification_dict:
    #                     #就获取链接
    #                     classification_link_node = li_node.xpath('./@href')
    #                     if len(classification_link_node) != 0:
    #                         classification_link = li_node.xpath('./@href')[0].extract().strip()
    #                         # 匹配链接中的id进行去重，获取唯一一个(|是或者)
    #                         patter = re.compile("[bbn=|node=](\d+)")
    #                         filter_category_id_list = patter.findall(classification_link)
    #                         if len(filter_category_id_list) != 0:
    #                             category_id = filter_category_id_list[0]
    #                             # 过滤重复id
    #                             if category_id not in category_id_dict:
    #                                 category_id_dict.append(category_id)
    #                                 #构建一级列表链接
    #                                 big_classification_link = 'https://www.amazon.com/s?rh=n%3A' + category_id + '%2C&fs=true&language=zh&ref=lp_' + category_id + '_sar'
    #                                 item['big_classification_link'] = big_classification_link
    #                                 print(big_classification_link)
    #                                 # 限制一个类别用于测试
    #                                 if '16225018011' in big_classification_link:
    #                                     yield scrapy.Request(
    #                                                 url=big_classification_link,
    #                                                 callback=self.get_pages,
    #                                                 meta={'item': copy.deepcopy(item)},
    #                                                 dont_filter=True
    #                                             )
    #
    # # 翻页操作
    # def get_pages(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #     item = response.meta['item']
    #
    #     # 批量翻页（在获取商品详情信息时行不通）
    #     # 判断翻页
    #     # 获取页数控件，根据有没有控件来确定请求链接数
    #     sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #     # 没有页数，只有一页则直接请求一页
    #     if len(sum_pages) == 0:
    #         print('无页数')
    #         page_link = response.url
    #         item['page_link'] = page_link
    #         yield scrapy.Request(
    #             url=page_link,
    #             callback=self.get_commodity_link,
    #             meta={'item': copy.deepcopy(item)},
    #             dont_filter=True
    #         )
    #     else:
    #         # 有页数，有页数则构建多页请求
    #         sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #         # 页数组件没有缩减影藏（就是显示所有页数）
    #         if sum_page == '1':
    #             print('有页数')
    #             # sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
    #             # for page in range(1, int(sum_pages) + 1):
    #             #     page_link = response.url + '&page=' + str(page)
    #             #     item['page_link'] = page_link
    #             #     yield scrapy.Request(
    #             #         url=page_link,
    #             #         callback=self.get_commodity_link,
    #             #         meta={'item': copy.deepcopy(item)},
    #             #         dont_filter=True
    #             #     )
    #             for page in range(1):
    #                 page_link = response.url + '&page=' + str(page)
    #                 item['page_link'] = page_link
    #                 yield scrapy.Request(
    #                     url=page_link,
    #                     callback=self.get_commodity_link,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #         else:
    #             print('有页数缩减影藏')
    #             # # 页数组件有缩减影藏(一些页数被影藏，页数中间有...)
    #             # sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #             # for page in range(1, int(sum_pages) + 1):
    #             #     page_link = response.url + '&page=' + str(page)
    #             #     item['page_link'] = page_link
    #             #     yield scrapy.Request(
    #             #         url=page_link,
    #             #         callback=self.get_commodity_link,
    #             #         meta={'item': copy.deepcopy(item)},
    #             #         dont_filter=True
    #             #     )
    #             # 限制一页测试
    #             for page in range(1):
    #                 page_link = response.url + '&page=' + str(page)
    #                 item['page_link'] = page_link
    #                 yield scrapy.Request(
    #                     url=page_link,
    #                     callback=self.get_commodity_link,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #
    #
    #
    # # 获取每个商品链接
    # def get_commodity_link(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #
    #     item = response.meta['item']
    #
    #     commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div/div[@class="sg-col-inner"]')
    #     print(len(commodity_node_list))
    #     for commodity_node in commodity_node_list:
    #         # 过滤推广商品
    #         filter_commodity_node = commodity_node.xpath('.//div[@class="a-row a-spacing-micro"]')
    #         if len(filter_commodity_node) == 0:
    #             # 要改成ref后所有字符清空
    #             patter = re.compile("/ref=\S+")
    #             commodity_link = patter.sub("", response.urljoin(commodity_node.xpath('.//h2/a/@href')[0].extract()))
    #             #不加?th=1&psc=1有些页面数据访问不到，所以统一加
    #             new_commodity_link = commodity_link.replace('/-/zh','') + '?th=1&psc=1'
    #             item['commodity_link'] = new_commodity_link
    #             if 'B001PU9A9Q' in new_commodity_link:
    #                 yield scrapy.Request(
    #                     url=item['commodity_link'],
    #                     callback=self.get_commodity_data,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )

    def parse2(self, response):
    # 获取商品数据（再构造sku链接并请求）
    # def get_commodity_data(self, response):
        item = response.meta['item']

        # 获取商品名
        commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
        item['commodity_name'] = commodity_name

        # 有sku爬取方式dont_filter=True不保存指纹
        try:
            # 匹配数据
            patter = re.compile('"asinVariationValues" : (.*),')
            commodity_htmldata = patter.findall(response.text)[0]
            # # # 匹配数据转为json
            new_commodity_json_data = json.loads(commodity_htmldata)
            # .keys取出字典的健（.keys可以取出字典的健（valuas可以取出字典的值,取出后会是一个元组）
            sku_ids_tuple = new_commodity_json_data.keys()

            # 取出的是一个元组，把元组转成列表（元组转列表list()，列表转元组tuple()）
            sku_ids = list(sku_ids_tuple)

            # 为后面爬取评论数据构建参数
            # 初始化循环次数
            page_i = -1
            # 初始化存放一个商品sku的列表
            sku_list = []
            # 根据sku_id构建sku_url，#不加?th=1&psc=1有些页面数据访问不到，所以统一加
            sku_url = 'https://www.amazon.com/dp/' + sku_ids[0] + '?th=1&psc=1'
            yield scrapy.Request(
                url=sku_url,
                callback=self.get_sku_data,
                meta={'item': copy.deepcopy(item),
                      'cookiejar': response.meta['cookiejar'],
                      'sku_ids': copy.deepcopy(sku_ids),
                      'page_i': copy.deepcopy(page_i),
                      'sku_list': copy.deepcopy(sku_list)},
                dont_filter=True
            )
        # 没有sku爬取方式dont_filter=False保存指纹
        except:
            print('没有sku')
            sku_ids = []
            # 为后面爬取评论数据构建参数
            # 初始化循环次数
            page_i = -1
            # 初始化存放一个商品sku的列表
            sku_list = []
            # sku_url
            sku_url = response.url

            yield scrapy.Request(
                url=sku_url,
                callback=self.get_sku_data,
                meta={'item': copy.deepcopy(item),
                      'cookiejar': response.meta['cookiejar'],
                      'sku_ids': copy.deepcopy(sku_ids),
                      'page_i': copy.deepcopy(page_i),
                      'sku_list': copy.deepcopy(sku_list)},
                # dont_filter=False
                dont_filter=True
            )

    # 获取商品sku数据
    # def parse2(self, response):
    def get_sku_data(self, response):
        item = response.meta['item']
        sku_ids = response.meta['sku_ids']
        page_i = response.meta['page_i']
        sku_list = response.meta['sku_list']

        # 根据sku_ids大小来决定爬取方式：0代表没有sku
        # 有sku爬取方式
        if len(sku_ids) != 0:
            # 为了全部都添加指纹，请求两次传来的url
            if page_i == -1:
                page_i += 1
                # 根据sku_id循环构建sku_url#不加?th=1&psc=1有些页面数据访问不到，所以统一加
                sku_url = 'https://www.amazon.com/dp/' + sku_ids[page_i] + '?th=1&psc=1'
                yield scrapy.Request(
                    url=sku_url,
                    callback=self.get_sku_data,
                    meta={'item': copy.deepcopy(item),
                          'cookiejar': response.meta['cookiejar'],
                          'sku_ids': copy.deepcopy(sku_ids),
                          'page_i': copy.deepcopy(page_i),
                          'sku_list': copy.deepcopy(sku_list)},
                    # dont_filter=False
                    dont_filter=True
                )

            else:
                # 存放单个sku字典
                sku_commodity_datas_dict = {}

                # 获取商品链接
                sku_commodity_datas_dict['sku_link'] = response.url
                # 获取商品名
                sku_commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
                sku_commodity_datas_dict['sku_commodity_name'] = sku_commodity_name

                # 历史销量(没有销量显示，用评论数代替，有多少评论就有多少人买)
                historical_sold_node = response.xpath('//*[@id="acrCustomerReviewText"]/text()')
                if len(historical_sold_node) != 0:
                    historical_sold_text = response.xpath('//*[@id="acrCustomerReviewText"]/text()')[0].extract().strip()
                    if ',' in historical_sold_text:
                        # 获取的是字符串说明，用正则匹配出历史销量
                        patter = re.compile("\d+.\d+")
                        historical_sold = patter.findall(historical_sold_text)[0]
                        sku_commodity_datas_dict['historical_sold'] = int(historical_sold.replace(',', ''))
                    else:
                        patter = re.compile("\d")
                        historical_sold = patter.findall(historical_sold_text)[0]
                        sku_commodity_datas_dict['historical_sold'] = int(historical_sold)
                else:
                    sku_commodity_datas_dict['historical_sold'] = 0

                # 星级
                rating_star_node = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')
                if len(rating_star_node) != 0:
                    rating_star_text = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')[0].extract().strip()
                    if '.' in rating_star_text:
                        # 获取的是字符串说明，用正则匹配出星级数字
                        patter = re.compile("\d.\d")
                        rating_star = patter.findall(rating_star_text)[0]
                        sku_commodity_datas_dict['rating_star'] = rating_star
                    else:
                        patter = re.compile("\d")
                        rating_star = patter.findall(rating_star_text)[0]
                        sku_commodity_datas_dict['rating_star'] = rating_star
                else:
                    sku_commodity_datas_dict['rating_star'] = '0.0'

                # 获取商品图片
                commodityImage_link_list = []
                image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
                for image_link_classification in image_classification:
                    image_link = re.sub("._AC_US40_", "",image_link_classification.xpath('.//img/@src')[0].extract().strip())
                    commodityImage_link_list.append(image_link)
                sku_commodity_datas_dict['commodity_Imge_link'] = commodityImage_link_list

                # 商品规格
                attributes_list = []
                attributes_dict = {}
                attributes_node = response.xpath('//*[@class="a-normal a-spacing-micro"]/tr')
                if len(attributes_node) != 0:
                    attributes_node = response.xpath('//*[@class="a-normal a-spacing-micro"]/tr')
                    for attributes in attributes_node:
                        attribute_name = attributes.xpath('./td[1]/span/text()')[0].extract().strip()
                        attribute_value = attributes.xpath('./td[2]/span/text()')[0].extract().strip()
                        attributes_dict[attribute_name] = attribute_value
                else:
                    attributes_dict['商品规格'] = '无商品规格'
                attributes_list.append(attributes_dict)
                sku_commodity_datas_dict['attributes_list'] = attributes_list

                # 商品描述
                description_node = response.xpath('//*[@class="a-unordered-list a-vertical a-spacing-mini"]/li')
                description = ''
                if len(description_node) != 0:
                    for descriptions in description_node:
                        # 过滤包含id的li，取出不包含该id的li
                        li_id = descriptions.xpath('./@id')
                        if len(li_id) == 0:
                            # 将返回的单条字符串
                            description_Text = descriptions.xpath('./span/text()')[0].extract().strip()
                            if ':' in description_Text:
                                # 正则匹配’:‘右边的句子
                                patter = re.compile(":(.*)")
                                new_description_Text = patter.findall(description_Text)[0]
                                # 将返回的单条字符串拼接成一整段描述
                                description += new_description_Text + '。'
                            else:
                                description += description_Text + '。'
                else:
                    description = '无商品描述'
                sku_commodity_datas_dict['description'] = description

                # 存sku
                # 匹配sku数据节点
                # (sku值数据)variationValues节点数据
                sku_values_patter = re.compile('"variationValues" : (.*),')
                sku_values_htmldata = sku_values_patter.findall(response.text)[0]
                # 匹配数据转为json
                sku_values_json_data = json.loads(sku_values_htmldata)

                # （sku属性数据）variationDisplayLabels节点数据
                sku_types_patter = re.compile('"variationDisplayLabels" : (.*),')
                sku_types_htmldata = sku_types_patter.findall(response.text)[0]
                # 匹配数据转为json
                sku_types_json_data = json.loads(sku_types_htmldata)

                # （sku属性和属性值代号数据）asinVariationValues节点数据
                skuData_patter = re.compile('"asinVariationValues" : (.*),')
                skuData_htmldata = skuData_patter.findall(response.text)[0]
                # # 匹配数据转为json
                skuData_json_data = json.loads(skuData_htmldata)

                # 获取sku属性数据的属性健（是健不是值）
                sku_type_list = list(sku_types_json_data.keys())
                # 存sku的字典
                sku_dict = {}
                # 根据属性值循环配合其他数据节点获取sku属性名属性值
                for sku_type_id in sku_type_list:
                    # 根据属性id获取值id
                    sky_value_id = skuData_json_data[sku_ids[page_i]][sku_type_id]
                    # 获取属性
                    sky_type = sku_types_json_data[sku_type_id]
                    # 获取值
                    sky_value = sku_values_json_data[sku_type_id][int(sky_value_id)]
                    # 构造sku
                    sku_dict[sky_type] = sky_value
                # 添加sku_data
                sku_commodity_datas_dict['sku_data'] = sku_dict
                # 获取判断组件
                # 判断有有无市场价组件（两种布局不同,秒杀价）
                discount_node1 = response.xpath(
                    '//*[@class="a-span12 a-color-secondary a-size-base"]/span/span[1]/text()')
                discount_node2 = response.xpath(
                    '//*[@class="a-size-small a-color-secondary aok-align-center basisPrice"]/span/span[1]/text()')
                # 判断有无打折的组件（两种布局不同，与上面对应）
                No_discount_node1 = response.xpath(
                    '//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')
                No_discount_node2 = response.xpath(
                    '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')
                # 判断有无购物选择的组件
                shopping_options_node = response.xpath('//*[@id="buybox-see-all-buying-choices"]/span/a/text()')

                if len(discount_node1) != 0:
                    # 获取价格
                    print('有打折1')
                    # 原价
                    original_Price = float(
                        response.xpath('//*[@class="a-span12 a-color-secondary a-size-base"]/span[1]/span[1]/text()')[
                            0].extract().strip().replace('US$', ''))
                    # 折后价
                    discount_Price = float(
                        response.xpath(
                            '//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
                            0].extract().strip().replace('US$', ''))
                    # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
                    discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
                    print(original_Price, discount_Price, discount)
                    sku_commodity_datas_dict['original_Price'] = original_Price
                    sku_commodity_datas_dict['discount_Price'] = discount_Price
                    sku_commodity_datas_dict['discount'] = discount

                    # 获取库存
                    # 判断支持地区配送的文本
                    region_Delivery_Text = \
                        response.xpath(
                            '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                            0].extract().strip()
                    if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                        print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    else:
                        print('配送, 预计')
                        # 构造参数
                        Add_Cart_params = {}
                        key_list = response.xpath('//*[@class="a-content"]/input/@name')
                        value_list = response.xpath('//*[@class="a-content"]/input/@value')
                        for i in range(len(key_list)):
                            key = key_list[i].extract().strip()
                            value = value_list[i].extract().strip()
                            Add_Cart_params[key] = value
                        # 发起添加购物车请求进行商品添加购物车
                        Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                        yield scrapy.FormRequest(
                            url=Add_Cart_url,
                            formdata=Add_Cart_params,
                            callback=self.add_Cart,
                            meta={'item': copy.deepcopy(item),
                                  'cookiejar': response.meta['cookiejar'],
                                  'sku_ids': copy.deepcopy(sku_ids),
                                  'page_i': copy.deepcopy(page_i),
                                  'sku_list': copy.deepcopy(sku_list),
                                  'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                            dont_filter=True
                        )

                elif len(discount_node2) != 0:
                    # 获取价格
                    print('有打折2')
                    # 原价
                    original_Price = float(
                        response.xpath('//*[@class="a-price a-text-price"]/span[1]/text()')[
                            0].extract().strip().replace('US$', ''))
                    # 折后价
                    discount_Price = float(response.xpath(
                        '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
                                               0].extract().strip().replace('US$', ''))
                    # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
                    discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
                    print(original_Price, discount_Price, discount)
                    sku_commodity_datas_dict['original_Price'] = original_Price
                    sku_commodity_datas_dict['discount_Price'] = discount_Price
                    sku_commodity_datas_dict['discount'] = discount

                    # 获取库存
                    # 判断支持地区配送的文本
                    region_Delivery_Text = \
                        response.xpath(
                            '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                            0].extract().strip()
                    if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                        print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    else:
                        print('配送, 预计')
                        # 构造参数
                        Add_Cart_params = {}
                        key_list = response.xpath('//*[@class="a-content"]/input/@name')
                        value_list = response.xpath('//*[@class="a-content"]/input/@value')
                        for i in range(len(key_list)):
                            key = key_list[i].extract().strip()
                            value = value_list[i].extract().strip()
                            Add_Cart_params[key] = value
                        # 发起添加购物车请求进行商品添加购物车
                        Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                        yield scrapy.FormRequest(
                            url=Add_Cart_url,
                            formdata=Add_Cart_params,
                            callback=self.add_Cart,
                            meta={'item': copy.deepcopy(item),
                                  'cookiejar': response.meta['cookiejar'],
                                  'sku_ids': copy.deepcopy(sku_ids),
                                  'page_i': copy.deepcopy(page_i),
                                  'sku_list': copy.deepcopy(sku_list),
                                  'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                            dont_filter=True
                        )

                elif len(No_discount_node1) != 0:
                    # 获取价格
                    print('无打折1')
                    original_Price = float(
                        response.xpath(
                            '//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
                            0].extract().strip().replace('US$', ''))
                    discount_Price = original_Price
                    discount = 0
                    print(original_Price, discount_Price, discount)
                    sku_commodity_datas_dict['original_Price'] = original_Price
                    sku_commodity_datas_dict['discount_Price'] = discount_Price
                    sku_commodity_datas_dict['discount'] = discount

                    # 获取库存
                    # 判断支持地区配送的文本
                    region_Delivery_Text = \
                        response.xpath(
                            '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                            0].extract().strip()
                    if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                        print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    else:
                        print('配送, 预计')
                        # 构造参数
                        Add_Cart_params = {}
                        key_list = response.xpath('//*[@class="a-content"]/input/@name')
                        value_list = response.xpath('//*[@class="a-content"]/input/@value')
                        for i in range(len(key_list)):
                            key = key_list[i].extract().strip()
                            value = value_list[i].extract().strip()
                            Add_Cart_params[key] = value
                        # 发起添加购物车请求进行商品添加购物车
                        Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                        yield scrapy.FormRequest(
                            url=Add_Cart_url,
                            formdata=Add_Cart_params,
                            callback=self.add_Cart,
                            meta={'item': copy.deepcopy(item),
                                  'cookiejar': response.meta['cookiejar'],
                                  'sku_ids': copy.deepcopy(sku_ids),
                                  'page_i': copy.deepcopy(page_i),
                                  'sku_list': copy.deepcopy(sku_list),
                                  'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                            dont_filter=True
                        )

                elif len(No_discount_node2) != 0:
                    # 获取价格
                    print('无打折2')
                    original_Price = float(response.xpath(
                        '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
                                               0].extract().strip().replace('US$', ''))
                    discount_Price = original_Price
                    discount = 0
                    print(original_Price, discount_Price, discount)
                    sku_commodity_datas_dict['original_Price'] = original_Price
                    sku_commodity_datas_dict['discount_Price'] = discount_Price
                    sku_commodity_datas_dict['discount'] = discount

                    # 获取库存
                    # 判断支持地区配送的文本
                    region_Delivery_Text = \
                        response.xpath(
                            '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                            0].extract().strip()
                    if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                        print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    else:
                        print('配送, 预计')
                        # 构造参数
                        Add_Cart_params = {}
                        key_list = response.xpath('//*[@class="a-content"]/input/@name')
                        value_list = response.xpath('//*[@class="a-content"]/input/@value')
                        for i in range(len(key_list)):
                            key = key_list[i].extract().strip()
                            value = value_list[i].extract().strip()
                            Add_Cart_params[key] = value
                        # 发起添加购物车请求进行商品添加购物车
                        Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                        yield scrapy.FormRequest(
                            url=Add_Cart_url,
                            formdata=Add_Cart_params,
                            callback=self.add_Cart,
                            meta={'item': copy.deepcopy(item),
                                  'cookiejar': response.meta['cookiejar'],
                                  'sku_ids': copy.deepcopy(sku_ids),
                                  'page_i': copy.deepcopy(page_i),
                                  'sku_list': copy.deepcopy(sku_list),
                                  'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                            dont_filter=True
                        )

                elif len(shopping_options_node) != 0:
                    print('购物选择，价格库存统一到下个方法处理')
                    shopping_options_url = 'https://www.amazon.com/gp/product/ajax/ref=dp_aod_unknown_mbc?asin=' + sku_ids[page_i] + '&experienceId=aodAjaxMain'
                    yield scrapy.Request(
                        url=shopping_options_url,
                        callback=self.get_Shopping_options,
                        meta={'item': copy.deepcopy(item),
                              'cookiejar': response.meta['cookiejar'],
                              'sku_ids': copy.deepcopy(sku_ids),
                              'page_i': copy.deepcopy(page_i),
                              'sku_list': copy.deepcopy(sku_list),
                              'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                        dont_filter=True
                    )

                else:
                    print('目前无货')
                    original_Price = 0
                    discount_Price = 0
                    discount = 0
                    print(original_Price, discount_Price, discount)
                    sku_commodity_datas_dict['original_Price'] = original_Price
                    sku_commodity_datas_dict['discount_Price'] = discount_Price
                    sku_commodity_datas_dict['discount'] = discount
                    sku_commodity_datas_dict['inventory'] = 0

                    # 把sku添加到sku_list列表
                    sku_list.append(sku_commodity_datas_dict)
                    # 获取完一页获取下一页
                    page_i += 1
                    # 次数等于一个商品sku，则提交数据
                    if page_i == len(sku_ids):
                        print(str(page_i), str(len(sku_list)))
                        item['sku_list'] = sku_list
                        stock_response_json = response.json()
                        print(stock_response_json['features']['nav-cart']['cartQty'])
                        yield item
                    # 次数不等于一个商品sku则构造下一个sku链接
                    else:
                        # 根据sku_id循环构建sku_url#不加?th=1&psc=1有些页面数据访问不到，所以统一加
                        sku_url = 'https://www.amazon.com/dp/' + sku_ids[page_i] + '?th=1&psc=1'
                        yield scrapy.Request(
                            url=sku_url,
                            callback=self.get_sku_data,
                            meta={'item': copy.deepcopy(item),
                                  'cookiejar': response.meta['cookiejar'],
                                  'sku_ids': copy.deepcopy(sku_ids),
                                  'page_i': copy.deepcopy(page_i),
                                  'sku_list': copy.deepcopy(sku_list)},
                            # dont_filter=False
                            dont_filter=True
                        )

        # 没有sku爬取方式
        else:
            # 无sku直接爬取
            # 存放单个sku字典
            sku_commodity_datas_dict = {}

            # 获取网址的商品id
            patter = re.compile('dp/(.*)\?')
            commodity_id = patter.findall(response.url)[0]

            # 获取商品链接
            sku_commodity_datas_dict['sku_link'] = response.url
            # 获取商品名
            sku_commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
            sku_commodity_datas_dict['sku_commodity_name'] = sku_commodity_name

            # 历史销量(没有销量显示，用评论数代替，有多少评论就有多少人买)
            historical_sold_node = response.xpath('//*[@id="acrCustomerReviewText"]/text()')
            if len(historical_sold_node) != 0:
                historical_sold_text = response.xpath('//*[@id="acrCustomerReviewText"]/text()')[0].extract().strip()
                if ',' in historical_sold_text:
                    # 获取的是字符串说明，用正则匹配出历史销量
                    patter = re.compile("\d+.\d+")
                    historical_sold = patter.findall(historical_sold_text)[0]
                    sku_commodity_datas_dict['historical_sold'] = int(historical_sold.replace(',', ''))
                else:
                    patter = re.compile("\d")
                    historical_sold = patter.findall(historical_sold_text)[0]
                    sku_commodity_datas_dict['historical_sold'] = int(historical_sold)
            else:
                sku_commodity_datas_dict['historical_sold'] = 0

            # 星级
            rating_star_node = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')
            if len(rating_star_node) != 0:
                rating_star_text = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')[0].extract().strip()
                if '.' in rating_star_text:
                    # 获取的是字符串说明，用正则匹配出星级数字
                    patter = re.compile("\d.\d")
                    rating_star = patter.findall(rating_star_text)[0]
                    sku_commodity_datas_dict['rating_star'] = rating_star
                else:
                    patter = re.compile("\d")
                    rating_star = patter.findall(rating_star_text)[0]
                    sku_commodity_datas_dict['rating_star'] = rating_star
            else:
                sku_commodity_datas_dict['rating_star'] = '0.0'

            #获取商品图片
            commodityImage_link_list = []
            image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
            for image_link_classification in image_classification:
                image_link = re.sub("._AC_US40_","",image_link_classification.xpath('.//img/@src')[0].extract().strip())
                commodityImage_link_list.append(image_link)
            sku_commodity_datas_dict['commodity_Imge_link'] = commodityImage_link_list

            # 商品规格
            attributes_list = []
            attributes_dict = {}
            attributes_node = response.xpath('//*[@class="a-normal a-spacing-micro"]/tr')
            if len(attributes_node) != 0:
                attributes_node = response.xpath('//*[@class="a-normal a-spacing-micro"]/tr')
                for attributes in attributes_node:
                    attribute_name = attributes.xpath('./td[1]/span/text()')[0].extract().strip()
                    attribute_value = attributes.xpath('./td[2]/span/text()')[0].extract().strip()
                    attributes_dict[attribute_name] = attribute_value
            else:
                attributes_dict['商品规格'] = '无商品规格'
            attributes_list.append(attributes_dict)
            sku_commodity_datas_dict['attributes_list'] = attributes_list

            # 商品描述
            description_node = response.xpath('//*[@class="a-unordered-list a-vertical a-spacing-mini"]/li')
            description = ''
            if len(description_node) != 0:
                for descriptions in description_node:
                    # 过滤包含id的li，取出不包含该id的li
                    li_id = descriptions.xpath('./@id')
                    if len(li_id) == 0:
                        # 将返回的单条字符串
                        description_Text = descriptions.xpath('./span/text()')[0].extract().strip()
                        if ':' in description_Text:
                            # 正则匹配’:‘右边的句子
                            patter = re.compile(":(.*)")
                            new_description_Text = patter.findall(description_Text)[0]
                            # 将返回的单条字符串拼接成一整段描述
                            description += new_description_Text + '。'
                        else:
                            description += description_Text + '。'
            else:
                description = '无商品描述'
            sku_commodity_datas_dict['description'] = description

            # 存sku
            sku_dict = {"无sku": "只有一个"}
            # 添加sku_data
            sku_commodity_datas_dict['sku_data'] = sku_dict

            # 添加价格库存
            # 获取判断组件
            # 判断有有无市场价组件（两种布局不同,秒杀价）
            discount_node1 = response.xpath('//*[@class="a-span12 a-color-secondary a-size-base"]/span/span[1]/text()')
            discount_node2 = response.xpath(
                '//*[@class="a-size-small a-color-secondary aok-align-center basisPrice"]/span/span[1]/text()')
            # 判断有无打折的组件（两种布局不同，与上面对应）
            No_discount_node1 = response.xpath(
                '//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')
            No_discount_node2 = response.xpath(
                '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')
            # 判断有无购物选择的组件
            shopping_options_node = response.xpath('//*[@id="buybox-see-all-buying-choices"]/span/a/text()')

            if len(discount_node1) != 0:
                # 获取价格
                print('有打折1')
                # 原价
                original_Price = float(
                    response.xpath('//*[@class="a-span12 a-color-secondary a-size-base"]/span[1]/span[1]/text()')[
                        0].extract().strip().replace('US$', ''))
                # 折后价
                discount_Price = float(
                    response.xpath('//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
                        0].extract().strip().replace('US$', ''))
                # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
                discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
                print(original_Price, discount_Price, discount)
                sku_commodity_datas_dict['original_Price'] = original_Price
                sku_commodity_datas_dict['discount_Price'] = discount_Price
                sku_commodity_datas_dict['discount'] = discount

                # 获取库存
                # 判断支持地区配送的文本
                region_Delivery_Text = \
                    response.xpath(
                        '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                        0].extract().strip()
                if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                    print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    # 无法配送，库存为0
                    sku_commodity_datas_dict['inventory'] = 0
                    # 把sku添加到sku_list列表
                    sku_list.append(sku_commodity_datas_dict)
                    item['sku_list'] = sku_list
                    yield item
                else:
                    print('配送, 预计')
                    # 构造参数
                    Add_Cart_params = {}
                    key_list = response.xpath('//*[@class="a-content"]/input/@name')
                    value_list = response.xpath('//*[@class="a-content"]/input/@value')
                    for i in range(len(key_list)):
                        key = key_list[i].extract().strip()
                        value = value_list[i].extract().strip()
                        Add_Cart_params[key] = value
                    # 发起添加购物车请求进行商品添加购物车
                    Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                    yield scrapy.FormRequest(
                        url=Add_Cart_url,
                        formdata=Add_Cart_params,
                        callback=self.add_Cart,
                        meta={'item': copy.deepcopy(item),
                              'cookiejar': response.meta['cookiejar'],
                              'sku_ids': copy.deepcopy(sku_ids),
                              'page_i': copy.deepcopy(page_i),
                              'sku_list': copy.deepcopy(sku_list),
                              'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                        dont_filter=True
                    )

            elif len(discount_node2) != 0:
                # 获取价格
                print('有打折2')
                # 原价
                original_Price = float(
                    response.xpath('//*[@class="a-price a-text-price"]/span[1]/text()')[0].extract().strip().replace(
                        'US$', ''))
                # 折后价
                discount_Price = float(response.xpath(
                    '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
                                           0].extract().strip().replace('US$', ''))
                # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
                discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
                print(original_Price, discount_Price, discount)
                sku_commodity_datas_dict['original_Price'] = original_Price
                sku_commodity_datas_dict['discount_Price'] = discount_Price
                sku_commodity_datas_dict['discount'] = discount

                # 获取库存
                # 判断支持地区配送的文本
                region_Delivery_Text = \
                    response.xpath(
                        '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                        0].extract().strip()
                if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                    print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    # 无法配送，库存为0
                    sku_commodity_datas_dict['inventory'] = 0
                    # 把sku添加到sku_list列表
                    sku_list.append(sku_commodity_datas_dict)
                    item['sku_list'] = sku_list
                    yield item
                else:
                    print('配送, 预计')
                    # 构造参数
                    Add_Cart_params = {}
                    key_list = response.xpath('//*[@class="a-content"]/input/@name')
                    value_list = response.xpath('//*[@class="a-content"]/input/@value')
                    for i in range(len(key_list)):
                        key = key_list[i].extract().strip()
                        value = value_list[i].extract().strip()
                        Add_Cart_params[key] = value
                    # 发起添加购物车请求进行商品添加购物车
                    Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                    yield scrapy.FormRequest(
                        url=Add_Cart_url,
                        formdata=Add_Cart_params,
                        callback=self.add_Cart,
                        meta={'item': copy.deepcopy(item),
                              'cookiejar': response.meta['cookiejar'],
                              'sku_ids': copy.deepcopy(sku_ids),
                              'page_i': copy.deepcopy(page_i),
                              'sku_list': copy.deepcopy(sku_list),
                              'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                        dont_filter=True
                    )

            elif len(No_discount_node1) != 0:
                # 获取价格
                print('无打折1')
                original_Price = float(
                    response.xpath('//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
                        0].extract().strip().replace('US$', ''))
                discount_Price = original_Price
                discount = 0
                print(original_Price, discount_Price, discount)
                sku_commodity_datas_dict['original_Price'] = original_Price
                sku_commodity_datas_dict['discount_Price'] = discount_Price
                sku_commodity_datas_dict['discount'] = discount

                # 获取库存
                # 判断支持地区配送的文本
                region_Delivery_Text = \
                    response.xpath(
                        '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                        0].extract().strip()
                if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                    print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    # 无法配送，库存为0
                    sku_commodity_datas_dict['inventory'] = 0
                    # 把sku添加到sku_list列表
                    sku_list.append(sku_commodity_datas_dict)
                    item['sku_list'] = sku_list
                    yield item
                else:
                    print('配送, 预计')
                    # 构造参数
                    Add_Cart_params = {}
                    key_list = response.xpath('//*[@class="a-content"]/input/@name')
                    value_list = response.xpath('//*[@class="a-content"]/input/@value')
                    for i in range(len(key_list)):
                        key = key_list[i].extract().strip()
                        value = value_list[i].extract().strip()
                        Add_Cart_params[key] = value
                    # 发起添加购物车请求进行商品添加购物车
                    Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                    yield scrapy.FormRequest(
                        url=Add_Cart_url,
                        formdata=Add_Cart_params,
                        callback=self.add_Cart,
                        meta={'item': copy.deepcopy(item),
                              'cookiejar': response.meta['cookiejar'],
                              'sku_ids': copy.deepcopy(sku_ids),
                              'page_i': copy.deepcopy(page_i),
                              'sku_list': copy.deepcopy(sku_list),
                              'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                        dont_filter=True
                    )

            elif len(No_discount_node2) != 0:
                # 获取价格
                print('无打折2')
                original_Price = float(response.xpath(
                    '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
                                           0].extract().strip().replace('US$', ''))
                discount_Price = original_Price
                discount = 0
                print(original_Price, discount_Price, discount)
                sku_commodity_datas_dict['original_Price'] = original_Price
                sku_commodity_datas_dict['discount_Price'] = discount_Price
                sku_commodity_datas_dict['discount'] = discount

                # 获取库存
                # 判断支持地区配送的文本
                region_Delivery_Text = \
                    response.xpath(
                        '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
                        0].extract().strip()
                if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
                    print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
                    # 无法配送，库存为0
                    sku_commodity_datas_dict['inventory'] = 0
                    # 把sku添加到sku_list列表
                    sku_list.append(sku_commodity_datas_dict)
                    item['sku_list'] = sku_list
                    yield item
                else:
                    print('配送, 预计')
                    # 构造参数
                    Add_Cart_params = {}
                    key_list = response.xpath('//*[@class="a-content"]/input/@name')
                    value_list = response.xpath('//*[@class="a-content"]/input/@value')
                    for i in range(len(key_list)):
                        key = key_list[i].extract().strip()
                        value = value_list[i].extract().strip()
                        Add_Cart_params[key] = value
                    # 发起添加购物车请求进行商品添加购物车
                    Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
                    yield scrapy.FormRequest(
                        url=Add_Cart_url,
                        formdata=Add_Cart_params,
                        callback=self.add_Cart,
                        meta={'item': copy.deepcopy(item),
                              'cookiejar': response.meta['cookiejar'],
                              'sku_ids': copy.deepcopy(sku_ids),
                              'page_i': copy.deepcopy(page_i),
                              'sku_list': copy.deepcopy(sku_list),
                              'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                        dont_filter=True
                    )

            elif len(shopping_options_node) != 0:
                print('购物选择，价格库存统一到下个方法处理')
                shopping_options_url = 'https://www.amazon.com/gp/product/ajax/ref=dp_aod_unknown_mbc?asin=' + commodity_id + '&experienceId=aodAjaxMain'
                yield scrapy.Request(
                    url=shopping_options_url,
                    callback=self.get_Shopping_options,
                    meta={'item': copy.deepcopy(item),
                          'cookiejar': response.meta['cookiejar'],
                          'sku_ids': copy.deepcopy(sku_ids),
                          'page_i': copy.deepcopy(page_i),
                          'sku_list': copy.deepcopy(sku_list),
                          'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
                    dont_filter=True
                )

            else:
                print('目前无货')
                original_Price = 0
                discount_Price = 0
                discount = 0
                print(original_Price, discount_Price, discount)
                sku_commodity_datas_dict['original_Price'] = original_Price
                sku_commodity_datas_dict['discount_Price'] = discount_Price
                sku_commodity_datas_dict['discount'] = discount
                sku_commodity_datas_dict['inventory'] = 0
                # 把sku添加到sku_list列表
                sku_list.append(sku_commodity_datas_dict)
                item['sku_list'] = sku_list
                yield item



        # # 获取网址的商品id
        # patter = re.compile('dp/(.*)\?')
        # commodity_id = patter.findall(response.url)[0]
        # # 获取判断组件
        # 判断有有无市场价组件（两种布局不同,秒杀价）
        # discount_node1 = response.xpath('//*[@class="a-span12 a-color-secondary a-size-base"]/span/span[1]/text()')
        # discount_node2 = response.xpath(
        #     '//*[@class="a-size-small a-color-secondary aok-align-center basisPrice"]/span/span[1]/text()')
        # # 判断有无打折的组件（两种布局不同，与上面对应）
        # No_discount_node1 = response.xpath('//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')
        # No_discount_node2 = response.xpath(
        #     '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')
        # # 判断有无购物选择的组件
        # shopping_options_node = response.xpath('//*[@id="buybox-see-all-buying-choices"]/span/a/text()')
        #
        # if len(discount_node1) != 0:
        #     # 获取价格
        #     print('有打折1')
        #     # 原价
        #     original_Price = float(
        #         response.xpath('//*[@class="a-span12 a-color-secondary a-size-base"]/span[1]/span[1]/text()')[
        #             0].extract().strip().replace('US$', ''))
        #     # 折后价
        #     discount_Price = float(
        #         response.xpath('//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
        #             0].extract().strip().replace('US$', ''))
        #     # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
        #     discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
        #     print(original_Price, discount_Price, discount)
        #     sku_commodity_datas_dict['original_Price'] = original_Price
        #     sku_commodity_datas_dict['discount_Price'] = discount_Price
        #     sku_commodity_datas_dict['discount'] = discount
        #
        #     # 获取库存
        #     # 判断支持地区配送的文本
        #     region_Delivery_Text = \
        #     response.xpath('//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
        #         0].extract().strip()
        #     if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
        #         print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
        #     else:
        #         print('配送, 预计')
        #         # 构造参数
        #         Add_Cart_params = {}
        #         key_list = response.xpath('//*[@class="a-content"]/input/@name')
        #         value_list = response.xpath('//*[@class="a-content"]/input/@value')
        #         for i in range(len(key_list)):
        #             key = key_list[i].extract().strip()
        #             value = value_list[i].extract().strip()
        #             Add_Cart_params[key] = value
        #         # 发起添加购物车请求进行商品添加购物车
        #         Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
        #         yield scrapy.FormRequest(
        #             url=Add_Cart_url,
        #             formdata=Add_Cart_params,
        #             callback=self.add_Cart,
        #             meta={'item': copy.deepcopy(item), 'cookiejar': response.meta['cookiejar'], 'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
        #             dont_filter=True
        #         )
        #
        # elif len(discount_node2) != 0:
        #     # 获取价格
        #     print('有打折2')
        #     # 原价
        #     original_Price = float(
        #         response.xpath('//*[@class="a-price a-text-price"]/span[1]/text()')[0].extract().strip().replace('US$', ''))
        #     # 折后价
        #     discount_Price = float(response.xpath(
        #         '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
        #                                0].extract().strip().replace('US$', ''))
        #     # 折扣：round((1 - discount_Price/original_Price) * 100)) + '%'
        #     discount = str(round((1 - discount_Price / original_Price) * 100)) + '%'
        #     print(original_Price, discount_Price, discount)
        #     sku_commodity_datas_dict['original_Price'] = original_Price
        #     sku_commodity_datas_dict['discount_Price'] = discount_Price
        #     sku_commodity_datas_dict['discount'] = discount
        #
        #     # 获取库存
        #     # 判断支持地区配送的文本
        #     region_Delivery_Text = \
        #     response.xpath('//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
        #         0].extract().strip()
        #     if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
        #         print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
        #     else:
        #         print('配送, 预计')
        #         # 构造参数
        #         Add_Cart_params = {}
        #         key_list = response.xpath('//*[@class="a-content"]/input/@name')
        #         value_list = response.xpath('//*[@class="a-content"]/input/@value')
        #         for i in range(len(key_list)):
        #             key = key_list[i].extract().strip()
        #             value = value_list[i].extract().strip()
        #             Add_Cart_params[key] = value
        #         # 发起添加购物车请求进行商品添加购物车
        #         Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
        #         yield scrapy.FormRequest(
        #             url=Add_Cart_url,
        #             formdata=Add_Cart_params,
        #             callback=self.add_Cart,
        #             meta={'item': copy.deepcopy(item), 'cookiejar': response.meta['cookiejar'], 'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
        #             dont_filter=True
        #         )
        #
        # elif len(No_discount_node1) != 0:
        #     # 获取价格
        #     print('无打折1')
        #     original_Price = float(
        #         response.xpath('//*[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')[
        #             0].extract().strip().replace('US$', ''))
        #     discount_Price = original_Price
        #     discount = 0
        #     print(original_Price, discount_Price, discount)
        #     sku_commodity_datas_dict['original_Price'] = original_Price
        #     sku_commodity_datas_dict['discount_Price'] = discount_Price
        #     sku_commodity_datas_dict['discount'] = discount
        #
        #     # 获取库存
        #     # 判断支持地区配送的文本
        #     region_Delivery_Text = \
        #     response.xpath('//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
        #         0].extract().strip()
        #     if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
        #         print('此商品无法配送至您选择的配送地点。请选择其他配送地点。')
        #     else:
        #         print('配送, 预计')
        #         # 构造参数
        #         Add_Cart_params = {}
        #         key_list = response.xpath('//*[@class="a-content"]/input/@name')
        #         value_list = response.xpath('//*[@class="a-content"]/input/@value')
        #         for i in range(len(key_list)):
        #             key = key_list[i].extract().strip()
        #             value = value_list[i].extract().strip()
        #             Add_Cart_params[key] = value
        #         # 发起添加购物车请求进行商品添加购物车
        #         Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
        #         yield scrapy.FormRequest(
        #             url=Add_Cart_url,
        #             formdata=Add_Cart_params,
        #             callback=self.add_Cart,
        #             meta={'item': copy.deepcopy(item), 'cookiejar': response.meta['cookiejar'], 'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
        #             dont_filter=True
        #         )
        #
        # elif len(No_discount_node2) != 0:
        #     # 获取价格
        #     print('无打折2')
        #     original_Price = float(response.xpath(
        #         '//*[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[1]/text()')[
        #                                0].extract().strip().replace('US$', ''))
        #     discount_Price = original_Price
        #     discount = 0
        #     print(original_Price, discount_Price, discount)
        #     sku_commodity_datas_dict['original_Price'] = original_Price
        #     sku_commodity_datas_dict['discount_Price'] = discount_Price
        #     sku_commodity_datas_dict['discount'] = discount
        #
        #     # 获取库存
        #     # 判断支持地区配送的文本
        #     region_Delivery_Text = \
        #     response.xpath('//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/text()')[
        #         0].extract().strip()
        #     if region_Delivery_Text == '此商品无法配送至您选择的配送地点。请选择其他配送地点。':
        #         print('不可配送当前区域')
        #     else:
        #         print('可配送当前区域')
        #         # 构造参数
        #         Add_Cart_params = {}
        #         key_list = response.xpath('//*[@class="a-content"]/input/@name')
        #         value_list = response.xpath('//*[@class="a-content"]/input/@value')
        #         for i in range(len(key_list)):
        #             key = key_list[i].extract().strip()
        #             value = value_list[i].extract().strip()
        #             Add_Cart_params[key] = value
        #         # 发起添加购物车请求进行商品添加购物车
        #         Add_Cart_url = 'https://www.amazon.com/cart/add-to-cart/ref=dp_start-bbf_1_glance'
        #         yield scrapy.FormRequest(
        #             url=Add_Cart_url,
        #             formdata=Add_Cart_params,
        #             callback=self.add_Cart,
        #             meta={'item': copy.deepcopy(item), 'cookiejar': response.meta['cookiejar'], 'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
        #             dont_filter=True
        #         )
        #
        # elif len(shopping_options_node) != 0:
        #     print('购物选择，价格库存统一到下个方法处理')
        #     shopping_options_url = 'https://www.amazon.com/gp/product/ajax/ref=dp_aod_unknown_mbc?asin=' + commodity_id + '&experienceId=aodAjaxMain'
        #     yield scrapy.Request(
        #         url=shopping_options_url,
        #         callback=self.get_Shopping_options,
        #         meta={'item': copy.deepcopy(item), 'cookiejar': response.meta['cookiejar'], 'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
        #         dont_filter=True
        #     )
        #
        # else:
        #     print('目前无货')
        #     original_Price = 0
        #     discount_Price = 0
        #     discount = 0
        #     print(original_Price, discount_Price, discount)
        #     sku_commodity_datas_dict['original_Price'] = original_Price
        #     sku_commodity_datas_dict['discount_Price'] = discount_Price
        #     sku_commodity_datas_dict['discount'] = discount
        #     sku_commodity_datas_dict['inventory'] = 0


    # 获取更多购物车选择价格（只取第一个测试）
    def get_Shopping_options(self, response):
        item = response.meta['item']
        sku_commodity_datas_dict = response.meta['sku_commodity_datas_dict']

    # 获取价格
        original_Price = float(response.xpath('//*[@id="aod-price-1"]/span/span[1]/text()')[0].extract().strip().replace('US$', ''))
        discount_Price = original_Price
        discount = 0
        print(original_Price, discount_Price, discount)
        sku_commodity_datas_dict['original_Price'] = original_Price
        sku_commodity_datas_dict['discount_Price'] = discount_Price
        sku_commodity_datas_dict['discount'] = discount

    #获取库存
        aod_atc_csrf_token = response.xpath('//*[@id="aod-atc-csrf-token"]/@value')[0].extract().strip()
        # 点开查看所有购物选择，产品有多个商家多个价格库存，这里取第一个做测试。取别的可根据调整[0]获取
        data_aod_atc_action = response.xpath('//*[@id="aod-offer-list"]//span[@data-aod-atc-action]/@data-aod-atc-action')[0].extract().strip()
        data_aod_atc_action_json = json.loads(data_aod_atc_action)
        asin = data_aod_atc_action_json['asin']
        oid = data_aod_atc_action_json['oid']
        print(aod_atc_csrf_token, asin, oid)
        headers = {
            # 其他参数在中间件设置
            'x-api-csrf-token': aod_atc_csrf_token
        }
        Add_Cart_params = {
            "items": [
                {"asin": asin,
                 "offerListingId": oid,
                 # "quantity": 999,
                 "quantity": 1,
                 "additionalParameters": {}
                 }
            ]
        }
        # 发起添加购物车请求进行商品添加购物车
        Add_Cart_url = 'https://data.amazon.com/api/marketplaces/ATVPDKIKX0DER/cart/carts/retail/items'
        yield scrapy.Request(Add_Cart_url,
                             headers=headers,
                             method='POST',
                             body=json.dumps(Add_Cart_params),
                             callback=self.add_Cart,
                             dont_filter=True,
                             meta={'item': copy.deepcopy(item),
                                   'cookiejar': response.meta['cookiejar'],
                                   'sku_ids': copy.deepcopy(response.meta['sku_ids']),
                                   'page_i': copy.deepcopy(response.meta['page_i']),
                                   'sku_list': copy.deepcopy(response.meta['sku_list']),
                                   'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)}
                             )


    # 添加商品到购物车
    def add_Cart(self, response):
        # 根据stockType判断是那种库存类型
        print('跳转购物车界面')
        Cart_url = 'https://www.amazon.com/-/zh/gp/cart/view.html?ref_=sw_gtc'
        yield scrapy.Request(
            url=Cart_url,
            callback=self.get_Cart,
            meta={'item': copy.deepcopy(response.meta['item']),
                  'cookiejar': response.meta['cookiejar'],
                  'sku_ids': copy.deepcopy(response.meta['sku_ids']),
                  'page_i': copy.deepcopy(response.meta['page_i']),
                  'sku_list': copy.deepcopy(response.meta['sku_list']),
                  'sku_commodity_datas_dict': copy.deepcopy(response.meta['sku_commodity_datas_dict'])},
            dont_filter=True
        )


    # 购物车页面
    def get_Cart(self, response):
        print('获取购物车')
        # 匹配timeStamp，requestID，token
        Cart_patter = re.compile('"csrf":(.*),"isInternal"')
        cart_Html_data = Cart_patter.findall(response.text)[0]
        cart_Html_json_data = json.loads(cart_Html_data)
        timeStamp = cart_Html_json_data['timeStamp']
        requestID = cart_Html_json_data['requestID']
        token = cart_Html_json_data['token']
        # 获取actionItemID
        # # 第一种(xpath)
        # actionItemID_node_list = response.xpath('//*[@class="a-section a-spacing-mini sc-list-body sc-java-remote-feature"]//div/@data-itemid')
        # print(len(actionItemID_node_list))
        # for actionItemID_node in actionItemID_node_list:
        #     actionItemID = actionItemID_node.extract().strip()
        # 第二种(正则匹配)
        # 匹配actionItemID
        Cart_patter2 = re.compile('name="quantity\.(.*)" class')
        commodity_htmldata2 = Cart_patter2.findall(response.text)[0]
        actionItemID = commodity_htmldata2
        quantity_actionItemID = 'quantity.' + actionItemID

        stock_params = {
            'actionType': 'update-quantity',
            # 变
            'actionItemID': actionItemID,
            # 数量(键是由quantity. + actionItemID构成)
            quantity_actionItemID: '999',
            'timeStamp': timeStamp,
            'requestID': requestID,
            'token': token,
            # # （其他按需求）
            # 'asin': commodity_id,
            # 'pageAction': 'update-quantity',
            # 'submit.update-quantity.'+ actionItemID: '1',
            # 'displayedSavedItemNum': '0',
            # 'encodedOffering': 'NmBaXa7BQbtuZ3yW3ywFlS%2B9hzD6aVAZQND3CZI%2BD%2BDKlDD9R%2BFlQDE0I%2B4FdIfatkpe0pWLkkW4x2V2p7kKkwDoRytLlL0mlf0pmV0mRjSu6KA9OkGROb8Lon9X%2FaBeI7tpPhHwhhFfpC9MUBI5knhNG0AvRcwFrqlLJeOo2opk9mpOBMaZP%2FZjzCnXKART',
            # 'hasMoreItems': 'false',
            # 'addressId': '',
            # 'addressZip': '',
            # 'closeAddonUpsell': '1',
            # 'displayedSavedItemNum': '0',
            # 'activeItems': '0|' + actionItemID + '|1|0|1|21.5||||||',
            # # 页数
            # 'redirectToFullPage': '1',
        }

        # 传参列表
        meta_list = [actionItemID, timeStamp, requestID, token]

        # 查询库存
        stock_url = 'https://www.amazon.com/cart'
        yield scrapy.FormRequest(
            url=stock_url,
            callback=self.get_stock,
            formdata=stock_params,
            meta={'item': copy.deepcopy(response.meta['item']),
                  'cookiejar': response.meta['cookiejar'],
                  'sku_ids': copy.deepcopy(response.meta['sku_ids']),
                  'page_i': copy.deepcopy(response.meta['page_i']),
                  'sku_list': copy.deepcopy(response.meta['sku_list']),
                  'sku_commodity_datas_dict': copy.deepcopy(response.meta['sku_commodity_datas_dict']),
                  'meta_list': copy.deepcopy(meta_list)},
            dont_filter=True
        )

    # 查询商品库存
    def get_stock(self, response):
        print('获取库存')
        meta_list = response.meta['meta_list']
        sku_commodity_datas_dict = response.meta['sku_commodity_datas_dict']

        stock_response_json = response.json()
        # 获取库存两种方式
        # （1）多条链接对应一个cookies时，购物车不止有一个商品，可用（会出错）
        # stock_quantity = stock_response_json['features']['active-cart']['manipulations'][0]['content']
        # stock_patter = re.compile('data-quantity="(\d+)')
        # cart_Html_data = stock_patter.findall(stock_quantity)[0]
        # print(cart_Html_data)
        # （2）一条链接对应一个cookies时，购物车只有一个商品，可用cartQty（购物车总库存）
        inventory = stock_response_json['features']['nav-cart']['cartQty']
        sku_commodity_datas_dict['inventory'] = inventory

        # 从购物车删除商品
        cart_Remove_commodity_url = 'https://www.amazon.com/cart/ref=ox_sc_cart_actions_1'
        # 没有注释掉的是必须要有的参数（其他按需求）
        cart_Remove_commodity_params = {
            'submit.cart-actions': '1',
            'pageAction': 'cart-actions',
            'actionPayload': '[{"type":"DELETE_START","payload":{"itemId":"' + meta_list[0] + '","list":"activeItems","relatedItemIds":[],"isPrimeAsin":false}}]',
            'timeStamp': meta_list[1],
            'requestID': meta_list[2],
            'token': meta_list[3],
        }
        yield scrapy.FormRequest(
            url=cart_Remove_commodity_url,
            callback=self.cart_Remove_commodity,
            formdata=cart_Remove_commodity_params,
            meta={'item': copy.deepcopy(response.meta['item']),
                  'cookiejar': response.meta['cookiejar'],
                  'sku_ids': copy.deepcopy(response.meta['sku_ids']),
                  'page_i': copy.deepcopy(response.meta['page_i']),
                  'sku_list': copy.deepcopy(response.meta['sku_list']),
                  'sku_commodity_datas_dict': copy.deepcopy(sku_commodity_datas_dict)},
            dont_filter=True
        )

    # 从购物车删除商品
    def cart_Remove_commodity(self, response):
        print('从购物车删除商品')
        item = response.meta['item']
        sku_ids = response.meta['sku_ids']
        sku_list = response.meta['sku_list']
        page_i = response.meta['page_i']
        sku_commodity_datas_dict = response.meta['sku_commodity_datas_dict']
        # 有sku爬取方式
        if len(sku_ids) != 0:
            # 把sku添加到sku_list列表
            sku_list.append(sku_commodity_datas_dict)
            # 获取完一页获取下一页
            page_i += 1
            # 次数等于一个商品sku，则提交数据
            if page_i == len(sku_ids):
                print(str(page_i),str(len(sku_list)))
                item['sku_list'] = sku_list
                stock_response_json = response.json()
                print(stock_response_json['features']['nav-cart']['cartQty'])
                yield item
            # 次数不等于一个商品sku则构造下一个sku链接
            else:
                # 根据sku_id循环构建sku_url#不加?th=1&psc=1有些页面数据访问不到，所以统一加
                sku_url = 'https://www.amazon.com/dp/' + sku_ids[page_i] + '?th=1&psc=1'
                yield scrapy.Request(
                    url=sku_url,
                    callback=self.get_sku_data,
                    meta={'item': copy.deepcopy(item),
                          'cookiejar': response.meta['cookiejar'],
                          'sku_ids': copy.deepcopy(sku_ids),
                          'page_i': copy.deepcopy(page_i),
                          'sku_list': copy.deepcopy(sku_list)},
                    # dont_filter=False
                    dont_filter=True
                )
        else:
            # 把sku添加到sku_list列表
            sku_list.append(sku_commodity_datas_dict)
            item['sku_list'] = sku_commodity_datas_dict
            stock_response_json = response.json()
            print(stock_response_json['features']['nav-cart']['cartQty'])
            yield item






































# （amazon中国站）
# 全部分类不是这个列表（这个列表只是全部分类的一部分），真的全部分类是没规律的

# 全部分类（旧）# https://www.amazon.cn/s?srs=1546136071&bbn=1546134071&rh=n%3A1546134071&dc&qid=1651040484&ref=lp_1546136071_ex_n_1)

    # import copy
    # import json
    # import re
    # import scrapy
    # from yamaxun.items import YamaxunItem
    # from scrapy_redis.spiders import RedisSpider
    # import numpy as np

    # 调用数据库
    # 添加数据lpush就是添加一个list,'ratings'就是健名，相当于ratings = ['aaa']
    # self.server.lpush('ratings', 'aaa')
    # 查看健对应数据大小
    # aa = self.server.llen('ratings')

    # 全部分类（旧）
    # https://www.amazon.cn/s?srs=1546136071&bbn=1546134071&rh=n%3A1546134071&dc&qid=1651040484&ref=lp_1546136071_ex_n_1
    # 全部分类（新）
    # https://www.amazon.cn/s?k=a
    # 销量排行榜链接
    # https://www.amazon.cn/gp/bestsellers/ref=zg_bs_unv_pc_0_1
    # 左侧隐藏菜单全部分类
    # https://www.amazon.de/gp/navigation/ajax/generic.html?ajaxTemplate=hamburgerMainContent&pageType=Gateway&hmDataAjaxHint=1&navDeviceType=desktop&isSmile=0&isPrime=0&isBackup=false&hashCustomerAndSessionId=8d12024d387a8c5e038c18434c0e0e4d048a64cc&isExportMode=true&languageCode=en_GB&environmentVFI=AmazonNavigationCards%2Fdevelopment%40B6099827072-AL2_x86_64&secondLayerTreeName=PrimeVideo%2BAmazonMusic%2BAmazonAppStore%2BAmazonPhoto%2BEchoAndAlexa%2BFireTV%2BFireTablet%2BKindleAndEbooks%2BMusicGameMovieTV%2BElectronic%2BHomeGardenPetsDIY%2BBeautyHealthGrocery%2BChildrenToyBaby%2BApparelSoftline%2BSportsOutdoor%2BAutomotiveMotorcycleIndustrial%2BHandmadeLaunchpad%2BStorefronts%2BAmazon_Business

    # class AmazonSpider(RedisSpider):
    #     name = 'amazon'
    #     # allowed_domains = ['amazon.cn']
    #     # start_urls = ['https://www.amazon.cn/s?srs=1546136071&bbn=1546134071&rh=n%3A1546134071&dc&qid=1651040484&ref=lp_1546136071_ex_n_1']
    #
    #     redis_key = 'py21'
    #
    #     def __init__(self, *args, **kwargs):
    #         domain = kwargs.pop('domain', '')
    #         self.allowed_domains = list(filter(None, domain.split(',')))
    #         super(AmazonSpider, self).__init__(*args, **kwargs)
    #
    #     def make_requests_from_url(self, url):
    #
    #         # 初始化商品数组，存放商品字典
    #         item = YamaxunItem()
    #         item['type'] = 'Product_data'
    #         item['startUrl'] = url
    #         # temp = 'session-id=457-8661111-8163056; ubid-acbcn=458-7313919-3569065; session-token=3RD0ohrjinQEUFIpjNXj1MZ13p0r2Y5xRsa4QgP/yEtmRvbfmmPK4XNLMteeff54pf0rQdAkSBZ818uSl0OS6fgdWEFvUX3OXSPSc0mxQiSdqR6zWNTt9ULQEIhPR64CDh3akqkp6qg9tM/f6Fj3VwslOvSH2KjO+XWv0Si3FT/AUkJo8VRMlJdT2toeSFxTVGb8v8DAGKWzq1vVkVIi4cPWq5nFON0vF378x8Eh4uSMq1UkGEYDd99tJIzYwL/6; x-acbcn="M816yCvA?eNmP90R3SAPePe?wL@ploXvwPxXUYeDsj@sP4Djl3RA0zmBKAW35JP7"; at-main=Atza|IwEBIA74ph_bCnR0vQrdzEZbfeKYSCTxsrzBLLsREXHP3ZwocCrzF-8CF1QjTDIDPNnMionKq199ec-xqd118AoOTPQrEFmCy8Yn23WV49zp6xgqjqUVFvPKw7QoY1FeEzOzppzKsAXuiwrV0vN1H1g4v4DnmYdI2zNOjg4ZdlPWaZcoJYbNTu3sud-mqxe3W5rI1jx_6Zokq7jsf1cnk5RGVg6N; sess-at-main="bdOGurp9f8Q/Ydt0t4Qch/SaJtyxmC4lC9FjgHcbUVI="; sst-main=Sst1|PQFfp167ZHYf1g9EZQkFIBFQCTLJbo2GssE00WrypApVaXjUz9zd3PobqmbNhcGkwVZ1aLXbANQtMh2wf4kV0xtoLQu-EfRA0Ilt8baAdfB7BFXF8L93Ke5RnsIdSSPz-hiUqd6x1errb-yOEAY8nBdSjKFfrIbgUU9betWpvInob73nCRZnc81G09Qck8HOvycLeMdYobHdv0oszAqhs9DFl50WK_wLlC3rXZCzjFE8fyrMNAF0bg5q5bMICtmuk4Wc9lW2QGvDUnKuOZIKLAmI_SZnlA7OiKNZA9ZQX3TQWxk; lc-acbcn=zh_CN; i18n-prefs=CNY; session-id-time=2082729601l; csm-hit=tb:Y0M74NJJZGB1GND7ZEXE+s-3GGY43HV1GPEWWKHX7MM|1654282325679&t:1654282325679&adb:adblk_no'
    #         # cookies = {data.split("=")[0]: data.split("=")[-1]for data in temp.split('; ')}
    #         return scrapy.Request(url,
    #                               dont_filter=True,
    #                               meta={'item': copy.deepcopy(item)},
    #                               # cookies=cookies
    #                               )

        # # 获取一级链接数据
        # def parse(self, response):
        #     # 判断是否登录成功
        #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
        #     item = response.meta['item']
        #     # 获取二级目录总链接
        #     node_list = response.xpath('//*[@id="departments"]/ul/li[@class="a-spacing-micro"]')
        #     # 判断二级目录为空则进行一级目录爬取，不为空则爬取商品
        #     if len(node_list) != 0:
        #         classification_node_list = response.xpath('//*[@class="a-spacing-micro"]')
        #         for classification_node in classification_node_list:
        #             item['big_classification_text'] = classification_node.xpath('./span/a/span/text()')[0].extract().strip()
        #             patter = re.compile("&qid=\d+")
        #             big_classification_link = patter.sub("",response.urljoin(classification_node.xpath('./span/a/@href')[0].extract()))
        #             item['big_classification_link'] = big_classification_link
        #             yield scrapy.Request(
        #                 url=item['big_classification_link'],
        #                 callback=self.get_pages,
        #                 meta={'item': copy.deepcopy(item)},
        #                 dont_filter=True
        #             )
        #     else:
        #         # 批量翻页（在获取商品详情信息时行不通）
        #         # 判断翻页
        #         #获取页数控件，根据有没有控件来确定请求链接数
        #         sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
        #         # 没有页数，只有一页则直接请求一页
        #         if len(sum_pages) == 0:
        #             patter = re.compile("qid=\d+")
        #             page_link = patter.sub("", item['startUrl'])
        #             item['page_link'] = page_link
        #             yield scrapy.Request(
        #                 url=item['page_link'],
        #                 callback=self.get_commodity_link,
        #                 meta={'item': copy.deepcopy(item)},
        #                 dont_filter=True
        #             )
        #         else:
        #             # 有页数，有页数则构建多页请求
        #             sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
        #             # 页数组件没有缩减影藏
        #             if sum_page == '1':
        #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
        #                 for page in range(1, int(sum_pages) + 1):
        #                     patter = re.compile("qid=\d+")
        #                     page_link = patter.sub("", item['startUrl'])
        #                     item['page_link'] = page_link + '&page=' + str(page)
        #                     print(item['page_link'])
        #                     # 构造商品页数链接，批量发起请求
        #                     yield scrapy.Request(
        #                         url=item['page_link'],
        #                         callback=self.get_commodity_link,
        #                         meta={'item': copy.deepcopy(item)},
        #                         dont_filter=True
        #                     )
        #             else:
        #                 # 页数组件有缩减影藏
        #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
        #                 for page in range(1, int(sum_pages) + 1):
        #                     patter = re.compile("qid=\d+")
        #                     page_link = patter.sub("", item['startUrl'])
        #                     item['page_link'] = page_link + '&page=' + str(page)
        #                     print(item['page_link'])
        #                     # 构造商品页数链接，批量发起请求
        #                     yield scrapy.Request(
        #                         url=item['page_link'],
        #                         callback=self.get_commodity_link,
        #                         meta={'item': copy.deepcopy(item)},
        #                         dont_filter=True
        #                     )
        #
        #
        #
        # # 翻页操作
        # def get_pages(self, response):
        #     # 判断是否登录成功
        #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
        #     item = response.meta['item']
        #     # 批量翻页（在获取商品详情信息时行不通）
        #     # 判断翻页
        #     # 获取页数控件，根据有没有控件来确定请求链接数
        #     sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
        #     # 没有页数，只有一页则直接请求一页
        #     if len(sum_pages) == 0:
        #         patter = re.compile("qid=\d+")
        #         page_link = patter.sub("", item['startUrl'])
        #         item['page_link'] = page_link
        #         yield scrapy.Request(
        #             url=item['page_link'],
        #             callback=self.get_commodity_link,
        #             meta={'item': copy.deepcopy(item)},
        #             dont_filter=True
        #         )
        #     else:
        #         # 有页数，有页数则构建多页请求
        #         sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
        #         # 页数组件没有缩减影藏
        #         if sum_page == '1':
        #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
        #             for page in range(1, int(sum_pages) + 1):
        #                 patter = re.compile("qid=\d+")
        #                 page_link = patter.sub("", item['startUrl'])
        #                 item['page_link'] = page_link + '&page=' + str(page)
        #                 print(item['page_link'])
        #                 # 构造商品页数链接，批量发起请求
        #                 yield scrapy.Request(
        #                     url=item['page_link'],
        #                     callback=self.get_commodity_link,
        #                     meta={'item': copy.deepcopy(item)},
        #                     dont_filter=True
        #                 )
        #         else:
        #             # 页数组件有缩减影藏
        #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
        #             for page in range(1, int(sum_pages) + 1):
        #                 patter = re.compile("qid=\d+")
        #                 page_link = patter.sub("", item['startUrl'])
        #                 item['page_link'] = page_link + '&page=' + str(page)
        #                 print(item['page_link'])
        #                 # 构造商品页数链接，批量发起请求
        #                 yield scrapy.Request(
        #                     url=item['page_link'],
        #                     callback=self.get_commodity_link,
        #                     meta={'item': copy.deepcopy(item)},
        #                     dont_filter=True
        #                 )
        #
        #
        # # 获取每个商品链接
        # # def parse(self, response):
        # def get_commodity_link(self, response):
        #     # 判断是否登录成功
        #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
        #     item = response.meta['item']
        #     commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]//h2')
        #     for commodity_node in commodity_node_list:
        #         # 去重有错，要改成ref后所有字符清空
        #         patter = re.compile("/ref=\S+")
        #         commodity_link = patter.sub("", response.urljoin(commodity_node.xpath('./a/@href')[0].extract()))
        #         # 不加?th=1&psc=1有些页面数据访问不到，所以统一加
        #         item['commodity_link'] = commodity_link + '?th=1&psc=1'
        #         print(commodity_link)
        #         yield scrapy.Request(
        #             url=item['commodity_link'],
        #             callback=self.get_commodity_data,
        #             meta={'item': copy.deepcopy(item)},
        #             dont_filter=True
        #         )
        #
        # # 获取商品数据（再构造sku链接并请求）
        # # def parse(self, response):
        # def get_commodity_data(self, response):
        #     item = response.meta['item']
        #
        #     # 获取商品名
        #     commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
        #     item['commodity_name'] = commodity_name
        #
        #     # 没有sku爬取方式dont_filter=True不保存指纹
        #     try:
        #         # 匹配数据
        #         patter = re.compile('"asinVariationValues" : (.*),')
        #         commodity_htmldata = patter.findall(response.text)[0]
        #         # # # 匹配数据转为json
        #         new_commodity_json_data = json.loads(commodity_htmldata)
        #         # .keys取出字典的健（.keys可以取出字典的健（valuas可以取出字典的值,取出后会是一个元组）
        #         sku_ids_tuple = new_commodity_json_data.keys()
        #
        #         # 取出的是一个元组，把元组转成列表（元组转列表list()，列表转元组tuple()）
        #         sku_ids = list(sku_ids_tuple)
        #
        #         # 为后面爬取评论数据构建参数
        #         # 初始化循环次数
        #         page_i = -1
        #         # 初始化存放一个商品sku的列表
        #         sku_list = []
        #         # 根据sku_id构建sku_url，#不加?th=1&psc=1有些页面数据访问不到，所以统一加
        #         sku_url = 'https://www.amazon.cn/dp/' + sku_ids[0] + '?th=1&psc=1'
        #
        #         yield scrapy.Request(
        #             url=sku_url,
        #             callback=self.get_sku_data,
        #             meta={'item': copy.deepcopy(item),
        #                   'sku_ids': copy.deepcopy(sku_ids),
        #                   'page_i': copy.deepcopy(page_i),
        #                   'sku_list': copy.deepcopy(sku_list)},
        #             dont_filter=True
        #         )
        #     # 没有sku爬取方式dont_filter=False保存指纹
        #     except:
        #         sku_ids = []
        #         # 为后面爬取评论数据构建参数
        #         # 初始化循环次数
        #         page_i = -1
        #         # 初始化存放一个商品sku的列表
        #         sku_list = []
        #         # sku_url
        #         sku_url = response.url
        #
        #         yield scrapy.Request(
        #             url=sku_url,
        #             callback=self.get_sku_data,
        #             meta={'item': copy.deepcopy(item),
        #                   'sku_ids': copy.deepcopy(sku_ids),
        #                   'page_i': copy.deepcopy(page_i),
        #                   'sku_list': copy.deepcopy(sku_list)},
        #             # dont_filter=False
        #             dont_filter=True
        #         )
        #
        # # 获取商品sku数据
        # def get_sku_data(self, response):
        #     # 判断是否登录成功
        #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
        #
        #     item = response.meta['item']
        #     sku_ids = response.meta['sku_ids']
        #     page_i = response.meta['page_i']
        #     sku_list = response.meta['sku_list']
        #
        #     # 根据sku_ids大小来决定爬取方式：0代表没有sku
        #     # 有sku爬取方式
        #     if len(sku_ids) != 0:
        #         # 为了全部都添加指纹，请求两次传来的url
        #         if page_i == -1:
        #             page_i += 1
        #             # 根据sku_id循环构建sku_url#不加?th=1&psc=1有些页面数据访问不到，所以统一加
        #             sku_url = 'https://www.amazon.cn/dp/' + sku_ids[page_i] + '?th=1&psc=1'
        #             yield scrapy.Request(
        #                 url=sku_url,
        #                 callback=self.get_sku_data,
        #                 meta={'item': copy.deepcopy(item),
        #                       'sku_ids': copy.deepcopy(sku_ids),
        #                       'page_i': copy.deepcopy(page_i),
        #                       'sku_list': copy.deepcopy(sku_list)},
        #                 # dont_filter=False
        #                 dont_filter=True
        #             )
        #
        #         else:
        #             # 存放单个sku字典
        #             sku_commodity_datas_dict = {}
        #
        #             # 获取商品链接
        #             sku_commodity_datas_dict['sku_link'] = response.url
        #             # 获取商品名
        #             sku_commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
        #             sku_commodity_datas_dict['sku_commodity_name'] = sku_commodity_name
        #
        #             # 历史销量(没有销量显示，用评论数代替，有多少评论就有多少人买)
        #             historical_sold_node = response.xpath('//*[@id="acrCustomerReviewText"]/text()')
        #             if len(historical_sold_node) != 0:
        #                 historical_sold_text = response.xpath('//*[@id="acrCustomerReviewText"]/text()')[
        #                     0].extract().strip()
        #                 # 获取的是字符串说明，用正则匹配出星级数字
        #                 patter = re.compile("\d")
        #                 historical_sold = patter.findall(historical_sold_text)[0]
        #                 sku_commodity_datas_dict['historical_sold'] = int(historical_sold)
        #             else:
        #                 sku_commodity_datas_dict['historical_sold'] = 0
        #
        #             # 获取价格数据
        #             price_data_node = response.xpath(
        #                 '//*[@class="a-section aok-hidden twister-plus-buying-options-price-data"]/text()')
        #             if len(price_data_node) != 0:
        #                 price_data = response.xpath(
        #                     '//*[@class="a-section aok-hidden twister-plus-buying-options-price-data"]/text()')[
        #                     0].extract().strip()
        #                 price_json_data = json.loads(price_data)
        #                 sku_commodity_price = price_json_data[0]['priceAmount']
        #                 sku_commodity_datas_dict['sku_commodity_price'] = int(sku_commodity_price)
        #             else:
        #                 # 价格0代表没有货
        #                 sku_commodity_datas_dict['sku_commodity_price'] = 0
        #
        #             # 星级
        #             rating_star_node = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')
        #             if len(rating_star_node) != 0:
        #                 rating_star_text = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')[
        #                     0].extract().strip()
        #                 # 获取的是字符串说明，用正则匹配出星级数字
        #                 patter = re.compile("\d.\d")
        #                 rating_star = patter.findall(rating_star_text)[0]
        #                 sku_commodity_datas_dict['rating_star'] = rating_star
        #             else:
        #                 sku_commodity_datas_dict['rating_star'] = '0.0'
        #
        #             # 库存
        #             inventory_node = response.xpath('//*[@id="quantity"]/option[last()]/text()')
        #             if len(inventory_node) != 0:
        #                 inventory = response.xpath('//*[@id="quantity"]/option[last()]/text()')[0].extract().strip()
        #                 sku_commodity_datas_dict['inventory'] = int(inventory)
        #             else:
        #                 inventory_text = response.xpath('//*[@class="a-size-medium a-color-success"]/text()')[
        #                     0].extract().strip()
        #                 # 获取的是字符串说明，用正则匹配出库存
        #                 patter = re.compile("\d")
        #                 inventory = patter.findall(inventory_text)[0]
        #                 sku_commodity_datas_dict['inventory'] = int(inventory)
        #
        #             # 获取商品图片
        #             commodityImage_link_list = []
        #             image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
        #             for image_link_classification in image_classification:
        #                 image_link = re.sub("._AC_US40_", "",
        #                                     image_link_classification.xpath('.//img/@src')[0].extract().strip())
        #                 commodityImage_link_list.append(image_link)
        #             sku_commodity_datas_dict['commodity_Imge_link'] = commodityImage_link_list
        #
        #             # 商品规格
        #             attributes_list = []
        #             attributes_dict = {}
        #             attributes_node = response.xpath('//*[@id="productDetails_techSpec_section_1"]/tr')
        #             if len(attributes_node) != 0:
        #                 attributes_node = response.xpath('//*[@id="productDetails_techSpec_section_1"]/tr')
        #                 for attributes in attributes_node:
        #                     attribute_name = attributes.xpath('./th/text()')[0].extract().strip()
        #                     attribute_value = attributes.xpath('./td/text()')[0].extract().strip()
        #                     attributes_dict[attribute_name] = attribute_value.replace('\u200e', '')
        #                 attributes_list.append(attributes_dict)
        #                 sku_commodity_datas_dict['attributes_list'] = attributes_list
        #             else:
        #                 attributes_node = response.xpath('//*[@id="detailBullets_feature_div"]/ul/li/span')
        #                 for attributes in attributes_node:
        #                     attribute_name = attributes.xpath('./span[1]/text()')[0].extract().strip().replace(
        #                         '\n                                    \u200f\n                                        :\n                                    \u200e',
        #                         '')
        #                     attribute_value = attributes.xpath('./span[2]/text()')[0].extract().strip()
        #                     attributes_dict[attribute_name] = attribute_value
        #                 attributes_list.append(attributes_dict)
        #                 sku_commodity_datas_dict['attributes_list'] = attributes_list
        #
        #             # 商品描述字符串<br>分段，返回的是字符串列表
        #             description_node = response.xpath('//*[@id="productDescription"]/p/span')
        #             for descriptions in description_node:
        #                 # 返回的是字符串列表
        #                 description_Selector = descriptions.xpath('./text()')
        #                 # 提取description_Selector列表中的Selector组件对应的值
        #                 description_dict = description_Selector.extract()
        #                 # 把列表里的值组成一句字符串
        #                 description = "".join(description_dict)
        #                 sku_commodity_datas_dict['description'] = description
        #
        #             # 存sku
        #             # 匹配sku数据节点
        #             # (sku值数据)variationValues节点数据
        #             sku_values_patter = re.compile('"variationValues" : (.*),')
        #             sku_values_htmldata = sku_values_patter.findall(response.text)[0]
        #             # 匹配数据转为json
        #             sku_values_json_data = json.loads(sku_values_htmldata)
        #
        #             # （sku属性数据）variationDisplayLabels节点数据
        #             sku_types_patter = re.compile('"variationDisplayLabels" : (.*),')
        #             sku_types_htmldata = sku_types_patter.findall(response.text)[0]
        #             # 匹配数据转为json
        #             sku_types_json_data = json.loads(sku_types_htmldata)
        #
        #             # （sku属性和属性值代号数据）asinVariationValues节点数据
        #             skuData_patter = re.compile('"asinVariationValues" : (.*),')
        #             skuData_htmldata = skuData_patter.findall(response.text)[0]
        #             # # 匹配数据转为json
        #             skuData_json_data = json.loads(skuData_htmldata)
        #
        #             # 获取sku属性数据的属性健（是健不是值）
        #             sku_type_list = list(sku_types_json_data.keys())
        #             # 存sku的字典
        #             sku_dict = {}
        #             # 根据属性值循环配合其他数据节点获取sku属性名属性值
        #             for sku_type_id in sku_type_list:
        #                 # 根据属性id获取值id
        #                 sky_value_id = skuData_json_data[sku_ids[page_i]][sku_type_id]
        #                 # 获取属性
        #                 sky_type = sku_types_json_data[sku_type_id]
        #                 # 获取值
        #                 sky_value = sku_values_json_data[sku_type_id][int(sky_value_id)]
        #                 # 构造sku
        #                 sku_dict[sky_type] = sky_value
        #             # 添加sku_data
        #             sku_commodity_datas_dict['sku_data'] = sku_dict
        #             # 把sku添加到sku_list列表
        #             sku_list.append(sku_commodity_datas_dict)
        #
        #             # 获取完一页获取下一页
        #             page_i += 1
        #             # 次数等于一个商品sku，则提交数据
        #             if page_i == len(sku_ids):
        #                 print(str(page_i), str(len(sku_list)))
        #                 item['sku_list'] = sku_list
        #                 yield item
        #             # 次数不等于一个商品sku则构造下一个sku链接
        #             else:
        #                 # 根据sku_id循环构建sku_url#不加?th=1&psc=1有些页面数据访问不到，所以统一加
        #                 sku_url = 'https://www.amazon.cn/dp/' + sku_ids[page_i] + '?th=1&psc=1'
        #                 yield scrapy.Request(
        #                     url=sku_url,
        #                     callback=self.get_sku_data,
        #                     meta={'item': copy.deepcopy(item),
        #                           'sku_ids': copy.deepcopy(sku_ids),
        #                           'page_i': copy.deepcopy(page_i),
        #                           'sku_list': copy.deepcopy(sku_list)},
        #                     # dont_filter=False
        #                     dont_filter=True
        #                 )
        #
        #     # 没有sku爬取方式
        #     else:
        #         # 无sku直接爬取
        #         # 存放单个sku字典
        #         sku_commodity_datas_dict = {}
        #
        #         # 获取商品链接
        #         sku_commodity_datas_dict['sku_link'] = response.url
        #         # 获取商品名
        #         sku_commodity_name = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
        #         sku_commodity_datas_dict['sku_commodity_name'] = sku_commodity_name
        #
        #         # 历史销量(没有销量显示，用评论数代替，有多少评论就有多少人买)
        #         historical_sold_node = response.xpath('//*[@id="acrCustomerReviewText"]/text()')
        #         if len(historical_sold_node) != 0:
        #             historical_sold_text = response.xpath('//*[@id="acrCustomerReviewText"]/text()')[
        #                 0].extract().strip()
        #             # 获取的是字符串说明，用正则匹配出星级数字
        #             patter = re.compile("\d")
        #             historical_sold = patter.findall(historical_sold_text)[0]
        #             sku_commodity_datas_dict['historical_sold'] = int(historical_sold)
        #         else:
        #             sku_commodity_datas_dict['historical_sold'] = 0
        #
        #         # 获取价格数据（有打折显示打折价，没打折显示原价）
        #         price_data_node = response.xpath(
        #             '//*[@class="a-section aok-hidden twister-plus-buying-options-price-data"]/text()')
        #         if len(price_data_node) != 0:
        #             price_data = \
        #             response.xpath('//*[@class="a-section aok-hidden twister-plus-buying-options-price-data"]/text()')[
        #                 0].extract().strip()
        #             price_json_data = json.loads(price_data)
        #             sku_commodity_price = price_json_data[0]['priceAmount']
        #             sku_commodity_datas_dict['sku_commodity_price'] = int(sku_commodity_price)
        #         else:
        #             # 价格0代表没有货
        #             sku_commodity_datas_dict['sku_commodity_price'] = 0
        #
        #         # 星级
        #         rating_star_node = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')
        #         if len(rating_star_node) != 0:
        #             rating_star_text = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')[
        #                 0].extract().strip()
        #             # 获取的是字符串说明，用正则匹配出星级数字
        #             patter = re.compile("\d.\d")
        #             rating_star = patter.findall(rating_star_text)[0]
        #             sku_commodity_datas_dict['rating_star'] = rating_star
        #         else:
        #             sku_commodity_datas_dict['rating_star'] = '0.0'
        #
        #         # 库存
        #         inventory_node = response.xpath('//*[@id="quantity"]/option[last()]/text()')
        #         if len(inventory_node) != 0:
        #             inventory = response.xpath('//*[@id="quantity"]/option[last()]/text()')[0].extract().strip()
        #             sku_commodity_datas_dict['inventory'] = int(inventory)
        #         else:
        #             inventory_text = response.xpath('//*[@class="a-size-medium a-color-success"]/text()')[
        #                 0].extract().strip()
        #             patter = re.compile("\d")
        #             inventory = patter.findall(inventory_text)[0]
        #             sku_commodity_datas_dict['inventory'] = int(inventory)
        #
        #         # 获取商品图片
        #         commodityImage_link_list = []
        #         image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
        #         for image_link_classification in image_classification:
        #             image_link = re.sub("._AC_US40_", "",
        #                                 image_link_classification.xpath('.//img/@src')[0].extract().strip())
        #             commodityImage_link_list.append(image_link)
        #         sku_commodity_datas_dict['commodity_Imge_link'] = commodityImage_link_list
        #
        #         # 商品规格
        #         attributes_list = []
        #         attributes_dict = {}
        #         attributes_node = response.xpath('//*[@id="productDetails_techSpec_section_1"]/tr')
        #         if len(attributes_node) != 0:
        #             attributes_node = response.xpath('//*[@id="productDetails_techSpec_section_1"]/tr')
        #             for attributes in attributes_node:
        #                 attribute_name = attributes.xpath('./th/text()')[0].extract().strip()
        #                 attribute_value = attributes.xpath('./td/text()')[0].extract().strip()
        #                 attributes_dict[attribute_name] = attribute_value.replace('\u200e', '')
        #             attributes_list.append(attributes_dict)
        #             sku_commodity_datas_dict['attributes_list'] = attributes_list
        #         else:
        #             attributes_node = response.xpath('//*[@id="detailBullets_feature_div"]/ul/li/span')
        #             for attributes in attributes_node:
        #                 attribute_name = attributes.xpath('./span[1]/text()')[0].extract().strip().replace(
        #                     '\n                                    \u200f\n                                        :\n                                    \u200e',
        #                     '')
        #                 attribute_value = attributes.xpath('./span[2]/text()')[0].extract().strip()
        #                 attributes_dict[attribute_name] = attribute_value
        #             attributes_list.append(attributes_dict)
        #             sku_commodity_datas_dict['attributes_list'] = attributes_list
        #
        #         # 商品描述
        #         # 字符串<br>分段，返回的是字符串列表
        #         description_node = response.xpath('//*[@id="productDescription"]/p/span')
        #         for descriptions in description_node:
        #             # 返回的是字符串组件列表
        #             description_Selector = descriptions.xpath('./text()')
        #             # 提取description_Selector列表中的Selector组件对应的值
        #             description_dict = description_Selector.extract()
        #             # 把列表里的值组成一句字符串
        #             description = "".join(description_dict)
        #             sku_commodity_datas_dict['description'] = description
        #
        #         # 存sku
        #         sku_dict = {"无sku": "只有一个"}
        #         # 添加sku_data
        #         sku_commodity_datas_dict['sku_data'] = sku_dict
        #         # 把sku添加到sku_list列表
        #         sku_list.append(sku_commodity_datas_dict)
        #         item['sku_list'] = sku_list
        #         yield item












    # 另一种sku处理（不用获取静态页面json的方法）

    #    # 获取一级链接数据
    # def parse(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #     item = response.meta['item']
    #     # 获取二级目录总链接
    #     node_list = response.xpath('//*[@id="departments"]/ul/li[@class="a-spacing-micro"]')
    #     # 判断二级目录为空则进行一级目录爬取，不为空则爬取商品
    #     if len(node_list) != 0:
    #         classification_node_list = response.xpath('//*[@class="a-spacing-micro"]')
    #         for classification_node in classification_node_list:
    #             item['big_classification_text'] = classification_node.xpath('./span/a/span/text()')[0].extract().strip()
    #             patter = re.compile("&qid=\d+")
    #             big_classification_link = patter.sub("",response.urljoin(classification_node.xpath('./span/a/@href')[0].extract()))
    #             item['big_classification_link'] = big_classification_link
    #             yield scrapy.Request(
    #                 url=item['big_classification_link'],
    #                 callback=self.get_pages,
    #                 meta={'item': copy.deepcopy(item)},
    #                 dont_filter=True
    #             )
    #     else:
    #         # 批量翻页（在获取商品详情信息时行不通）
    #         # 判断翻页
    #         #获取页数控件，根据有没有控件来确定请求链接数
    #         sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #         # 没有页数，只有一页则直接请求一页
    #         if len(sum_pages) == 0:
    #             patter = re.compile("qid=\d+")
    #             page_link = patter.sub("", item['startUrl'])
    #             item['page_link'] = page_link
    #             yield scrapy.Request(
    #                 url=item['page_link'],
    #                 callback=self.get_commodity_link,
    #                 meta={'item': copy.deepcopy(item)},
    #                 dont_filter=True
    #             )
    #         else:
    #             # 有页数，有页数则构建多页请求
    #             sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #             # 页数组件没有缩减影藏
    #             if sum_page == '1':
    #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
    #                 for page in range(1, int(sum_pages) + 1):
    #                     patter = re.compile("qid=\d+")
    #                     page_link = patter.sub("", item['startUrl'])
    #                     item['page_link'] = page_link + '&page=' + str(page)
    #                     print(item['page_link'])
    #                     # 构造商品页数链接，批量发起请求
    #                     yield scrapy.Request(
    #                         url=item['page_link'],
    #                         callback=self.get_commodity_link,
    #                         meta={'item': copy.deepcopy(item)},
    #                         dont_filter=True
    #                     )
    #             else:
    #                 # 页数组件有缩减影藏
    #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #                 for page in range(1, int(sum_pages) + 1):
    #                     patter = re.compile("qid=\d+")
    #                     page_link = patter.sub("", item['startUrl'])
    #                     item['page_link'] = page_link + '&page=' + str(page)
    #                     print(item['page_link'])
    #                     # 构造商品页数链接，批量发起请求
    #                     yield scrapy.Request(
    #                         url=item['page_link'],
    #                         callback=self.get_commodity_link,
    #                         meta={'item': copy.deepcopy(item)},
    #                         dont_filter=True
    #                     )
    #
    #
    #
    # # 翻页操作
    # def get_pages(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #     item = response.meta['item']
    #     # 批量翻页（在获取商品详情信息时行不通）
    #     # 判断翻页
    #     # 获取页数控件，根据有没有控件来确定请求链接数
    #     sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #     # 没有页数，只有一页则直接请求一页
    #     if len(sum_pages) == 0:
    #         patter = re.compile("qid=\d+")
    #         page_link = patter.sub("", item['startUrl'])
    #         item['page_link'] = page_link
    #         yield scrapy.Request(
    #             url=item['page_link'],
    #             callback=self.get_commodity_link,
    #             meta={'item': copy.deepcopy(item)},
    #             dont_filter=True
    #         )
    #     else:
    #         # 有页数，有页数则构建多页请求
    #         sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #         # 页数组件没有缩减影藏
    #         if sum_page == '1':
    #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
    #             for page in range(1, int(sum_pages) + 1):
    #                 patter = re.compile("qid=\d+")
    #                 page_link = patter.sub("", item['startUrl'])
    #                 item['page_link'] = page_link + '&page=' + str(page)
    #                 print(item['page_link'])
    #                 # 构造商品页数链接，批量发起请求
    #                 yield scrapy.Request(
    #                     url=item['page_link'],
    #                     callback=self.get_commodity_link,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #         else:
    #             # 页数组件有缩减影藏
    #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #             for page in range(1, int(sum_pages) + 1):
    #                 patter = re.compile("qid=\d+")
    #                 page_link = patter.sub("", item['startUrl'])
    #                 item['page_link'] = page_link + '&page=' + str(page)
    #                 print(item['page_link'])
    #                 # 构造商品页数链接，批量发起请求
    #                 yield scrapy.Request(
    #                     url=item['page_link'],
    #                     callback=self.get_commodity_link,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #
    #
    # # # 获取每个商品链接
    # # def parse(self, response):
    # def get_commodity_link(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #     item = response.meta['item']
    #     commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]//h2')
    #     for commodity_node in commodity_node_list:
    #         # 去重有错，要改成ref后所有字符清空
    #         patter = re.compile("/ref=\S+")
    #         commodity_link = patter.sub("", response.urljoin(commodity_node.xpath('./a/@href')[0].extract()))
    #         item['commodity_link'] = commodity_link + '?th=1&psc=1'
    #         print(commodity_link + '?th=1&psc=1')
    #         yield scrapy.Request(
    #             url=item['commodity_link'],
    #             callback=self.getSkulink,
    #             meta={'item': copy.deepcopy(item)},
    #             dont_filter=True
    #         )
    #
    # # 有下拉选择框的要链接后加'?th=1&psc=1'，不然不会做出选择，会返回none
    # # 获取sku链接
    # # def parse(self, response):
    # def getSkulink(self, response):
    # #判断不同sku列表参数
    #     judge_skuList_type = ''
    #
    #     item = response.meta['item']
    #
    #     # 不同的sku列表格式不同
    #     judge_nodes = response.xpath('//*[@id="twister"]')
    #     judge_nodes2 = response.xpath('//*[@id="twister-plus-inline-twister"]')
    #     # 根据不同的sku列表进行不同操作
    #     # 第一种sku列表
    #     if len(judge_nodes) != 0:
    #         judge_nodes1 = response.xpath('//*[@id="twister"]//li')
    #         # 有些有列表但是没有li,判断是否有li
    #         # 有li构建请求链接
    #         if len(judge_nodes1) != 0:
    #             # 带有选择下拉框sku列表
    #             select_nodes = response.xpath('//*[@id="twister"]//select')
    #             # 如果有选择下拉框sku列表
    #             if len(select_nodes) != 0:
    #                 print('66666666666')
    #                 judge_skuList_type = 'judge_nodes6'
    #                 select_nodes2=response.xpath('//*[@id="twister"]//select/option')
    #                 # 存放select_skuLink和li_skuLink所有链接的列表，最后再一起发送请求
    #                 select_list = []
    #                 for select_skuLink in select_nodes2:
    #                     select_value = select_skuLink.xpath('./@value').extract_first()
    #                     if select_value!='-1':
    #                         # 匹配sku码正则（value="1,B09RK3FT98"）
    #                         patter = re.compile("\S+,")
    #                         newselect_value = patter.sub("",select_value)
    #                         newselect_skuLink = "https://www.amazon.cn/dp/"+newselect_value+"?th=1&psc=1"
    #                         select_list.append(newselect_skuLink)
    #                 # li列表
    #                 sku_nodes = response.xpath('//*[@id="twister"]//li')
    #                 for skuLink in sku_nodes:
    #                     # 匹配sku链接正则,修改链接（舍弃）
    #                     # patter = re.compile("/ref=\S+")
    #                     # newskuLink = patter.sub("", response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #                     # newskuLink2 = newskuLink + '?th=1&psc=1'
    #                     # select_list.append(newskuLink2)
    #
    #                     # 利用split切割网址返回列表取sku码
    #                     patter = re.compile("/")
    #                     newskuLink = patter.split(skuLink.xpath('./@data-dp-url').extract_first())
    #                     # 有些data-dp-url为空的，就取另外属性data-defaultasin
    #                     if (len(newskuLink) == 1):
    #                         sku_number = skuLink.xpath('./@data-defaultasin').extract_first()
    #                     else:
    #                         sku_number = newskuLink[2]
    #
    #                     newskuLink2 = "https://www.amazon.cn/dp/" + sku_number + '?th=1&psc=1'
    #                     select_list.append(newskuLink2)
    #                 for select_list_sku in select_list:
    #                     yield scrapy.Request(
    #                         url=select_list_sku,
    #                         callback=self.filter_Skulink,
    #                         meta={'item': copy.deepcopy(item),
    #                               'judge_skuList_type': judge_skuList_type},
    #                         dont_filter=True
    #                     )
    #
    #
    #             else:
    #                 # 没有选择下拉框sku列表则按照正长li爬取
    #                 judge_skuList_type = 'judge_nodes1'
    #                 print('111111111')
    #                 sku_nodes = response.xpath('//*[@id="twister"]//li')
    #                 for skuLink in sku_nodes:
    #                     # 匹配sku链接正则,修改链接（舍弃）
    #                     # patter = re.compile("/ref=\S+")
    #                     # newskuLink = patter.sub("", response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #                     # newskuLink2 = newskuLink + '?th=1&psc=1'
    #                     # select_list.append(newskuLink2)
    #
    #                     # 利用split切割网址返回列表取sku码
    #                     patter = re.compile("/")
    #                     newskuLink = patter.split(skuLink.xpath('./@data-dp-url').extract_first())
    #                     # 有些data-dp-url为空的，就取另外属性data-defaultasin
    #                     if(len(newskuLink) == 1):
    #                         sku_number = skuLink.xpath('./@data-defaultasin').extract_first()
    #                     else:
    #                         sku_number = newskuLink[2]
    #
    #                     newskuLink2 = "https://www.amazon.cn/dp/" + sku_number + '?th=1&psc=1'
    #                     yield scrapy.Request(
    #                         url=newskuLink2,
    #                         callback=self.filter_Skulink,
    #                         meta={'item': copy.deepcopy(item),
    #                               'judge_skuList_type': judge_skuList_type},
    #                         dont_filter=True
    #                     )
    #         # 没有li直接爬取数据
    #         else:
    #             judge_skuList_type = 'judge_nodes5'
    #             print('5555555')
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.filter_Skulink,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': judge_skuList_type},
    #                 dont_filter=True
    #             )
    #     # 第二种sku列表
    #     elif len(judge_nodes2) != 0:
    #         judge_skuList_type = 'judge_nodes2'
    #         judge_nodes3 = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #         # 有些有列表但是没有li,判断是否有li
    #         # 有li构建请求链接
    #         if len(judge_nodes3) != 0:
    #             print('222222222')
    #             sku_nodes = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #             for skuLink in sku_nodes:
    #                 # 有多余的没有编码的li
    #                 skuLink2 = skuLink.xpath('./@data-asin')
    #                 # 去除多余的没有编码的li
    #                 if len(skuLink2) != 0:
    #                     newskuLink = "https://www.amazon.cn/dp/"+skuLink2.extract_first()+"?th=1&psc=1"
    #                     yield scrapy.Request(
    #                         url=newskuLink,
    #                         callback=self.filter_Skulink,
    #                         meta={'item': copy.deepcopy(item),
    #                               'judge_skuList_type': judge_skuList_type},
    #                         dont_filter=True
    #                     )
    #         # 没有li直接爬取数据
    #         else:
    #             judge_skuList_type = 'judge_nodes3'
    #             print('333333333')
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.filter_Skulink,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': judge_skuList_type},
    #                 dont_filter=True
    #             )
    #     # 没有sku列表直接爬取数据
    #     else:
    #         judge_skuList_type = 'judge_nodes4'
    #         print('44444444')
    #         yield scrapy.Request(
    #             url=item['commodity_link'],
    #             callback=self.filter_Skulink,
    #             meta={'item': copy.deepcopy(item),
    #                   'judge_skuList_type': judge_skuList_type},
    #             dont_filter=True
    #         )
    #
    #
    #
    # # 过滤重复url
    # def filter_Skulink(self, response):
    #     item = response.meta['item']
    #     judge_skuList_type = response.meta['judge_skuList_type']
    #
    #
    #     # 根据不同的sku列表进行不同操作
    #     if judge_skuList_type == 'judge_nodes1':
    #         item['judge_skuList_type'] = judge_skuList_type
    #
    #         print(judge_skuList_type)
    #         # 定义去重后数组
    #         sku_nodes = response.xpath('//*[@id="twister"]//li')
    #         for skuLink in sku_nodes:
    #             # 匹配sku链接正则,修改链接（舍弃）
    #             # patter = re.compile("/ref=\S+")
    #             # newskuLink = patter.sub("", response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #             # newskuLink2 = newskuLink + '?th=1&psc=1'
    #             # select_list.append(newskuLink2)
    #
    #             # 利用split切割网址返回列表取sku码
    #             patter = re.compile("/")
    #             newskuLink = patter.split(skuLink.xpath('./@data-dp-url').extract_first())
    #             # 有些data-dp-url为空的，就取另外属性data-defaultasin
    #             if (len(newskuLink) == 1):
    #                 sku_number = skuLink.xpath('./@data-defaultasin').extract_first()
    #             else:
    #                 sku_number = newskuLink[2]
    #
    #             newskuLink2 = "https://www.amazon.cn/dp/" + sku_number + '?th=1&psc=1'
    #             yield scrapy.Request(
    #                 url=newskuLink2,
    #                 callback=self.get_commodity_data,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #                 dont_filter=False
    #             )
    #     elif judge_skuList_type == 'judge_nodes2':
    #         item['judge_skuList_type'] = judge_skuList_type
    #
    #         print(judge_skuList_type)
    #         sku_nodes = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #         for skuLink in sku_nodes:
    #             # 有多余的没有编码的li
    #             skuLink2 = skuLink.xpath('./@data-asin')
    #             # 去除多余的没有编码的li
    #             if len(skuLink2) != 0:
    #                 newskuLink = "https://www.amazon.cn/dp/" + skuLink2.extract_first() + "?th=1&psc=1"
    #                 yield scrapy.Request(
    #                     url=newskuLink,
    #                     callback=self.get_commodity_data,
    #                     meta={'item': copy.deepcopy(item),
    #                           'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #                     dont_filter=False
    #                 )
    #
    #     elif judge_skuList_type == 'judge_nodes3':
    #         item['judge_skuList_type'] = judge_skuList_type
    #
    #         # 因为3和2提取数据方式一样，所以3重定向到2
    #         judge_skuList_type = 'judge_nodes2'
    #         print(judge_skuList_type)
    #         yield scrapy.Request(
    #             url=item['commodity_link'],
    #             callback=self.get_commodity_data,
    #             meta={'item': copy.deepcopy(item),
    #                   'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #             dont_filter=False
    #         )
    #     elif judge_skuList_type == 'judge_nodes5':
    #         item['judge_skuList_type'] = judge_skuList_type
    #         # 因为5和1提取数据方式一样，所以5重定向到1
    #         judge_skuList_type = 'judge_nodes1'
    #         print(judge_skuList_type)
    #         yield scrapy.Request(
    #             url=item['commodity_link'],
    #             callback=self.get_commodity_data,
    #             meta={'item': copy.deepcopy(item),
    #                   'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #             dont_filter=False
    #         )
    #     elif judge_skuList_type == 'judge_nodes4':
    #         item['judge_skuList_type'] = judge_skuList_type
    #
    #         print(judge_skuList_type)
    #         yield scrapy.Request(
    #             url=item['commodity_link'],
    #             callback=self.get_commodity_data,
    #             meta={'item': copy.deepcopy(item),
    #                   'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #             dont_filter=False
    #         )
    #     elif judge_skuList_type == 'judge_nodes6':
    #         item['judge_skuList_type'] = judge_skuList_type
    #
    #         print(judge_skuList_type)
    #         select_nodes2 = response.xpath('//*[@id="twister"]//select/option')
    #         # 存放select_skuLink和li_skuLink所有链接的列表，最后再一起发送请求
    #         select_list = []
    #         for select_skuLink in select_nodes2:
    #             select_value = select_skuLink.xpath('./@value').extract_first()
    #             if select_value != '-1':
    #                 patter = re.compile("\S+,")
    #                 newselect_value = patter.sub("", select_value)
    #                 newselect_skuLink = "https://www.amazon.cn/dp/" + newselect_value + "?th=1&psc=1"
    #                 select_list.append(newselect_skuLink)
    #         #li列表
    #         sku_nodes = response.xpath('//*[@id="twister"]//li')
    #         for skuLink in sku_nodes:
    #             # 匹配sku链接正则,修改链接（舍弃）
    #             # patter = re.compile("/ref=\S+")
    #             # newskuLink = patter.sub("", response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #             # newskuLink2 = newskuLink + '?th=1&psc=1'
    #             # select_list.append(newskuLink2)
    #
    #             # 利用split切割网址返回列表取sku码
    #             patter = re.compile("/")
    #             newskuLink = patter.split(skuLink.xpath('./@data-dp-url').extract_first())
    #             # 有些data-dp-url为空的，就取另外属性data-defaultasin
    #             if (len(newskuLink) == 1):
    #                 sku_number = skuLink.xpath('./@data-defaultasin').extract_first()
    #             else:
    #                 sku_number = newskuLink[2]
    #
    #             newskuLink2 = "https://www.amazon.cn/dp/" + sku_number + '?th=1&psc=1'
    #             select_list.append(newskuLink2)
    #
    #         for select_list_sku in select_list:
    #             yield scrapy.Request(
    #                 url=select_list_sku,
    #                 callback=self.get_commodity_data,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': copy.deepcopy(judge_skuList_type)},
    #                 dont_filter=False
    #             )
    #
    # # 获取商品数据
    # def get_commodity_data(self, response):
    #     # 判断是否登录成功
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #
    #     item = response.meta['item']
    #     judge_skuList_type = response.meta['judge_skuList_type']
    #
    #
    #     # sku字典
    #     commodity_data_dict={}
    #
    #     # 图片列表
    #     commodityImage_link_list = []
    #
    #     # sku_link链接
    #     item['sku_link'] = response.url
    #
    #     # 根据不同的sku列表进行不同操作
    #     if judge_skuList_type == 'judge_nodes1':
    #         # sku_属性：值
    #         sku_classification = response.xpath('//*[@id="twister"]/div/div')
    #         for sku_type_classification in sku_classification:
    #             sku_type = sku_type_classification.xpath('.//label/text()').extract_first().strip()
    #             sku_value = sku_type_classification.xpath('.//span/text()').extract_first().strip()
    #             commodity_data_dict[sku_type] = sku_value
    #         item['sku_type'] = str(commodity_data_dict)
    #
    #     elif judge_skuList_type == 'judge_nodes2':
    #         # sku_属性：值
    #         sku_classification = response.xpath('//*[@id="twister-plus-inline-twister"]/div')
    #         for sku_type_classification in sku_classification:
    #             classification = sku_type_classification.xpath('./span/div/div/div/span[1]/text()')
    #             if len(classification) != 0:
    #                 sku_type = sku_type_classification.xpath('./span/div/div/div/span[1]/text()').extract_first().strip()
    #                 sku_value = sku_type_classification.xpath('./span/div/div/div/span[2]/text()').extract_first().strip()
    #                 commodity_data_dict[sku_type] = sku_value
    #             else:
    #                 sku_type = sku_type_classification.xpath('./span[1]/text()').extract_first().strip()
    #                 sku_value = sku_type_classification.xpath('./span[2]/text()').extract_first().strip()
    #                 commodity_data_dict[sku_type] = sku_value
    #             item['sku_type'] = str(commodity_data_dict)
    #     # 因为judge_nodes3的处理方式和judge_nodes2一致，所以在这里不用考虑judge_nodes3
    #     elif judge_skuList_type == 'judge_nodes4':
    #         commodity_data_dict['sku_type'] = '无sku，只有一个'
    #         item['sku_type'] = str(commodity_data_dict)
    #
    #     elif judge_skuList_type == 'judge_nodes6':
    #         # sku_属性：值
    #         sku_classification = response.xpath('//*[@id="twister"]/div')
    #         for sku_type_classification in sku_classification:
    #             sku1_classification = sku_type_classification.xpath('.//select')
    #             sku2_classification = sku_type_classification.xpath('./ul')
    #             if len(sku1_classification)!=0:
    #                 sku_type = sku_type_classification.xpath('./div[2]/label/text()').extract_first().strip()
    #                 sku_value = sku_type_classification.xpath('.//option[@class="dropdownSelect"]/text()').extract_first()
    #                 commodity_data_dict[sku_type] = sku_value
    #             elif len(sku2_classification)!=0:
    #                 sku_type = sku_type_classification.xpath('./div/label/text()').extract_first().strip()
    #                 sku_value = sku_type_classification.xpath('./div/span/text()').extract_first().strip()
    #                 commodity_data_dict[sku_type] = sku_value
    #             item['sku_type'] = str(commodity_data_dict)
    #
    #
    #
    #
    #
    #     # 商品名
    #     item['commodity_name'] = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
    #     if len(response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')) != 0:
    #         # 商品价格
    #         # 把¥字符替换成空
    #         commodity_price = re.sub('¥', "", response.xpath(
    #             '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')[0].extract().strip())
    #         item['commodity_price'] = commodity_price
    #     elif len(response.xpath('//*[@id="corePrice_desktop"]/div/table/tr[1]/td[2]/span[1]/span[1]/text()')) != 0:
    #         # 商品价格
    #         # 把¥字符替换成空
    #         commodity_price = re.sub('¥', "", response.xpath(
    #             '//*[@id="corePrice_desktop"]/div/table/tr[1]/td[2]/span[1]/span[1]/text()')[0].extract().strip())
    #         item['commodity_price'] = commodity_price
    #     else:
    #         item['commodity_price'] = '商品目前无货'
    #
    #     #商品图片
    #     image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
    #     for image_link_classification in image_classification:
    #         image_link = re.sub("._AC_US40_","",image_link_classification.xpath('.//img/@src').extract_first())
    #         commodityImage_link_list.append(image_link)
    #     item['commodity_Imge_link'] = str(commodityImage_link_list)
    #
    #     yield item


























    # 把单个商品信息封装成json
    # class AmazonSpider(RedisSpider):
    #     name = 'amazon'
    #     # allowed_domains = ['amazon.cn']
    #     # start_urls = ['https://www.amazon.cn/s?srs=1546136071&bbn=1546134071&rh=n%3A1546134071&dc&qid=1651040484&ref=lp_1546136071_ex_n_1']
    #     redis_key = 'py21'
    #
    #     def __init__(self, *args, **kwargs):
    #         domain = kwargs.pop('domain', '')
    #         self.allowed_domains = list(filter(None, domain.split(',')))
    #         super(AmazonSpider, self).__init__(*args, **kwargs)
    #
    #     def make_requests_from_url(self, url):
    #         # {0: ['11111', '2222']}
    #         # 创建临时储存文件并初始化
    #         dict = {'np_i': -1, 'filter_result_dict': {}, 'filter_commodity_dict': {}}
    #         np.save('E:\my_file.npy', dict)
    #
    #         # 初始化商品数组，存放商品字典
    #         item = YamaxunItem()
    #         item['startUrl'] = url
    #         # temp = 'session-id=457-8661111-8163056; ubid-acbcn=458-7313919-3569065; session-token=3RD0ohrjinQEUFIpjNXj1MZ13p0r2Y5xRsa4QgP/yEtmRvbfmmPK4XNLMteeff54pf0rQdAkSBZ818uSl0OS6fgdWEFvUX3OXSPSc0mxQiSdqR6zWNTt9ULQEIhPR64CDh3akqkp6qg9tM/f6Fj3VwslOvSH2KjO+XWv0Si3FT/AUkJo8VRMlJdT2toeSFxTVGb8v8DAGKWzq1vVkVIi4cPWq5nFON0vF378x8Eh4uSMq1UkGEYDd99tJIzYwL/6; x-acbcn="M816yCvA?eNmP90R3SAPePe?wL@ploXvwPxXUYeDsj@sP4Djl3RA0zmBKAW35JP7"; at-main=Atza|IwEBIA74ph_bCnR0vQrdzEZbfeKYSCTxsrzBLLsREXHP3ZwocCrzF-8CF1QjTDIDPNnMionKq199ec-xqd118AoOTPQrEFmCy8Yn23WV49zp6xgqjqUVFvPKw7QoY1FeEzOzppzKsAXuiwrV0vN1H1g4v4DnmYdI2zNOjg4ZdlPWaZcoJYbNTu3sud-mqxe3W5rI1jx_6Zokq7jsf1cnk5RGVg6N; sess-at-main="bdOGurp9f8Q/Ydt0t4Qch/SaJtyxmC4lC9FjgHcbUVI="; sst-main=Sst1|PQFfp167ZHYf1g9EZQkFIBFQCTLJbo2GssE00WrypApVaXjUz9zd3PobqmbNhcGkwVZ1aLXbANQtMh2wf4kV0xtoLQu-EfRA0Ilt8baAdfB7BFXF8L93Ke5RnsIdSSPz-hiUqd6x1errb-yOEAY8nBdSjKFfrIbgUU9betWpvInob73nCRZnc81G09Qck8HOvycLeMdYobHdv0oszAqhs9DFl50WK_wLlC3rXZCzjFE8fyrMNAF0bg5q5bMICtmuk4Wc9lW2QGvDUnKuOZIKLAmI_SZnlA7OiKNZA9ZQX3TQWxk; lc-acbcn=zh_CN; i18n-prefs=CNY; session-id-time=2082729601l; csm-hit=tb:Y0M74NJJZGB1GND7ZEXE+s-3GGY43HV1GPEWWKHX7MM|1654282325679&t:1654282325679&adb:adblk_no'
    #         # cookies = {data.split("=")[0]: data.split("=")[-1]for data in temp.split('; ')}
    #         return scrapy.Request(url,
    #                               dont_filter=True,
    #                               meta={'item': copy.deepcopy(item)},
    #                               # cookies=cookies
    #                               )
    #
    #         # 获取一级链接数据
    #
    #     def parse(self, response):
    #         # 判断是否登录成功
    #         print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #         item = response.meta['item']
    #         # 获取二级目录总链接
    #         node_list = response.xpath('//*[@id="departments"]/ul/li[@class="a-spacing-micro"]')
    #         # 判断二级目录为空则进行一级目录爬取，不为空则爬取商品
    #         if len(node_list) != 0:
    #             classification_node_list = response.xpath('//*[@class="a-spacing-micro"]')
    #             for classification_node in classification_node_list:
    #                 item['big_classification_text'] = classification_node.xpath('./span/a/span/text()')[
    #                     0].extract().strip()
    #                 patter = re.compile("&qid=\d+")
    #                 big_classification_link = patter.sub("", response.urljoin(
    #                     classification_node.xpath('./span/a/@href')[0].extract()))
    #                 item['big_classification_link'] = big_classification_link
    #                 yield scrapy.Request(
    #                     url=item['big_classification_link'],
    #                     callback=self.get_pages,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #         else:
    #             # 批量翻页（在获取商品详情信息时行不通）
    #             # 判断翻页
    #             # 获取页数控件，根据有没有控件来确定请求链接数
    #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #             # 没有页数，只有一页则直接请求一页
    #             if len(sum_pages) == 0:
    #                 patter = re.compile("qid=\d+")
    #                 page_link = patter.sub("", item['startUrl'])
    #                 item['page_link'] = page_link
    #                 yield scrapy.Request(
    #                     url=item['page_link'],
    #                     callback=self.get_commodity_link,
    #                     meta={'item': copy.deepcopy(item)},
    #                     dont_filter=True
    #                 )
    #             else:
    #                 # 有页数，有页数则构建多页请求
    #                 sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #                 # 页数组件没有缩减影藏
    #                 if sum_page == '1':
    #                     sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
    #                     for page in range(1, int(sum_pages) + 1):
    #                         patter = re.compile("qid=\d+")
    #                         page_link = patter.sub("", item['startUrl'])
    #                         item['page_link'] = page_link + '&page=' + str(page)
    #                         print(item['page_link'])
    #                         # 构造商品页数链接，批量发起请求
    #                         yield scrapy.Request(
    #                             url=item['page_link'],
    #                             callback=self.get_commodity_link,
    #                             meta={'item': copy.deepcopy(item)},
    #                             dont_filter=True
    #                         )
    #                 else:
    #                     # 页数组件有缩减影藏
    #                     sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #                     for page in range(1, int(sum_pages) + 1):
    #                         patter = re.compile("qid=\d+")
    #                         page_link = patter.sub("", item['startUrl'])
    #                         item['page_link'] = page_link + '&page=' + str(page)
    #                         print(item['page_link'])
    #                         # 构造商品页数链接，批量发起请求
    #                         yield scrapy.Request(
    #                             url=item['page_link'],
    #                             callback=self.get_commodity_link,
    #                             meta={'item': copy.deepcopy(item)},
    #                             dont_filter=True
    #                         )
    #
    #     # 翻页操作
    #     def get_pages(self, response):
    #         # 判断是否登录成功
    #         print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #         item = response.meta['item']
    #         # 批量翻页（在获取商品详情信息时行不通）
    #         # 判断翻页
    #         # 获取页数控件，根据有没有控件来确定请求链接数
    #         sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #         # 没有页数，只有一页则直接请求一页
    #         if len(sum_pages) == 0:
    #             patter = re.compile("qid=\d+")
    #             page_link = patter.sub("", item['startUrl'])
    #             item['page_link'] = page_link
    #             yield scrapy.Request(
    #                 url=item['page_link'],
    #                 callback=self.get_commodity_link,
    #                 meta={'item': copy.deepcopy(item)},
    #                 dont_filter=True
    #             )
    #         else:
    #             # 有页数，有页数则构建多页请求
    #             sum_page = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #             # 页数组件没有缩减影藏
    #             if sum_page == '1':
    #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/a[last()-1]/text()')[0].extract()
    #                 for page in range(1, int(sum_pages) + 1):
    #                     patter = re.compile("qid=\d+")
    #                     page_link = patter.sub("", item['startUrl'])
    #                     item['page_link'] = page_link + '&page=' + str(page)
    #                     print(item['page_link'])
    #                     # 构造商品页数链接，批量发起请求
    #                     yield scrapy.Request(
    #                         url=item['page_link'],
    #                         callback=self.get_commodity_link,
    #                         meta={'item': copy.deepcopy(item)},
    #                         dont_filter=True
    #                     )
    #             else:
    #                 # 页数组件有缩减影藏
    #                 sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #                 for page in range(1, int(sum_pages) + 1):
    #                     patter = re.compile("qid=\d+")
    #                     page_link = patter.sub("", item['startUrl'])
    #                     item['page_link'] = page_link + '&page=' + str(page)
    #                     print(item['page_link'])
    #                     # 构造商品页数链接，批量发起请求
    #                     yield scrapy.Request(
    #                         url=item['page_link'],
    #                         callback=self.get_commodity_link,
    #                         meta={'item': copy.deepcopy(item)},
    #                         dont_filter=True
    #                     )
    #
    #     # 获取每个商品链接
    #     def get_commodity_link(self, response):
    #         # 判断是否登录成功
    #         print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #         item = response.meta['item']
    #         commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]//h2')
    #         for commodity_node in commodity_node_list:
    #             patter = re.compile("qid=\d+")
    #             commodity_link = patter.sub("", response.urljoin(commodity_node.xpath('./a/@href')[0].extract()))
    #             item['commodity_link'] = commodity_link
    #             print(item['commodity_link'])
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.getSkulink,
    #                 meta={'item': copy.deepcopy(item)},
    #                 dont_filter=True
    #             )
    #
    #     # 获取sku链接
    #     def getSkulink(self, response):
    #         load_dict = np.load('E:\my_file.npy', allow_pickle=True).item()
    #         filter_result_dict = load_dict['filter_result_dict']
    #         filter_commodity_dict = load_dict['filter_commodity_dict']
    #         np_i = load_dict['np_i']
    #         np_i += 1
    #         filter_result_dict[np_i] = []
    #         filter_commodity_dict[np_i] = []
    #         # 实时保存
    #         new_dict = {'np_i': np_i, 'filter_result_dict': filter_result_dict,
    #                     'filter_commodity_dict': filter_commodity_dict}
    #         np.save('E:\my_file.npy', new_dict)
    #         print(np_i)
    #         # 判断不同sku列表参数
    #         judge_skuList_type = ''
    #
    #         item = response.meta['item']
    #
    #         # 不同的sku列表格式不同
    #         judge_nodes = response.xpath('//*[@id="twister"]')
    #         judge_nodes2 = response.xpath('//*[@id="twister-plus-inline-twister"]')
    #         # 根据不同的sku列表进行不同操作
    #         # 第一种sku列表
    #         if len(judge_nodes) != 0:
    #
    #             judge_nodes = response.xpath('//*[@id="twister"]//li')
    #             # 有些有列表但是没有li,判断是否有li
    #             # 有li构建请求链接
    #             if len(judge_nodes) != 0:
    #                 # 带有选择下拉框sku列表
    #                 select_nodes = response.xpath('//*[@id="twister"]//select')
    #                 # 如果有选择下拉框sku列表
    #                 if len(select_nodes) != 0:
    #                     print('66666666666')
    #                     judge_skuList_type = 'judge_nodes6'
    #                     select_nodes2 = response.xpath('//*[@id="twister"]//select/option')
    #                     # 存放select_skuLink和li_skuLink所有链接的列表，最后再一起发送请求
    #                     select_list = []
    #                     for select_skuLink in select_nodes2:
    #                         select_value = select_skuLink.xpath('./@value').extract_first()
    #                         if select_value != '-1':
    #                             patter = re.compile("\S+,")
    #                             newselect_value = patter.sub("", select_value)
    #                             newselect_skuLink = "https://www.amazon.cn/dp/" + newselect_value + "?th=1&psc=1"
    #                             select_list.append(newselect_skuLink)
    #                     sku_nodes = response.xpath('//*[@id="twister"]//li')
    #                     for skuLink in sku_nodes:
    #                         # 匹配sku链接正则,修改链接
    #                         patter = re.compile("ref=\S+")
    #                         newskuLink = patter.sub("",
    #                                                 response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #                         select_list.append(newskuLink)
    #                     for select_list_sku in select_list:
    #                         yield scrapy.Request(
    #                             url=select_list_sku,
    #                             callback=self.filter_Skulink,
    #                             meta={'item': copy.deepcopy(item),
    #                                   'judge_skuList_type': judge_skuList_type,
    #                                   'np_i': copy.deepcopy(np_i)},
    #                             dont_filter=True
    #                         )
    #
    #
    #                 else:
    #                     # 没有选择下拉框sku列表则按照正长li爬取
    #                     judge_skuList_type = 'judge_nodes1'
    #                     print('111111111')
    #                     sku_nodes = response.xpath('//*[@id="twister"]//li')
    #                     for skuLink in sku_nodes:
    #                         # 匹配sku链接正则,修改链接
    #                         patter = re.compile("ref=\S+")
    #                         newskuLink = patter.sub("",
    #                                                 response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #                         yield scrapy.Request(
    #                             url=newskuLink,
    #                             callback=self.filter_Skulink,
    #                             meta={'item': copy.deepcopy(item),
    #                                   'judge_skuList_type': judge_skuList_type,
    #                                   'np_i': copy.deepcopy(np_i)},
    #                             dont_filter=True
    #                         )
    #             # 没有li直接爬取数据
    #             else:
    #                 judge_skuList_type = 'judge_nodes5'
    #                 print('5555555')
    #                 yield scrapy.Request(
    #                     url=item['commodity_link'],
    #                     callback=self.filter_Skulink,
    #                     meta={'item': copy.deepcopy(item),
    #                           'judge_skuList_type': judge_skuList_type,
    #                           'np_i': copy.deepcopy(np_i)},
    #                     dont_filter=True
    #                 )
    #         # 第二种sku列表
    #         elif len(judge_nodes2) != 0:
    #             judge_skuList_type = 'judge_nodes2'
    #             judge_nodes = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #             # 有些有列表但是没有li,判断是否有li
    #             # 有li构建请求链接
    #             if len(judge_nodes) != 0:
    #                 print('222222222')
    #                 sku_nodes = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #                 for skuLink in sku_nodes:
    #                     # 有多余的没有编码的li
    #                     skuLink2 = skuLink.xpath('./@data-asin')
    #                     # 去除多余的没有编码的li
    #                     if len(skuLink2) != 0:
    #                         newskuLink = "https://www.amazon.cn/dp/" + skuLink2.extract_first() + "?th=1&psc=1"
    #                         yield scrapy.Request(
    #                             url=newskuLink,
    #                             callback=self.filter_Skulink,
    #                             meta={'item': copy.deepcopy(item),
    #                                   'judge_skuList_type': judge_skuList_type,
    #                                   'np_i': copy.deepcopy(np_i)},
    #                             dont_filter=True
    #                         )
    #             # 没有li直接爬取数据
    #             else:
    #                 judge_skuList_type = 'judge_nodes3'
    #                 print('333333333')
    #                 yield scrapy.Request(
    #                     url=item['commodity_link'],
    #                     callback=self.filter_Skulink,
    #                     meta={'item': copy.deepcopy(item),
    #                           'judge_skuList_type': judge_skuList_type,
    #                           'np_i': copy.deepcopy(np_i)},
    #                     dont_filter=True
    #                 )
    #         # 没有sku列表直接爬取数据
    #         else:
    #             judge_skuList_type = 'judge_nodes4'
    #             print('44444444')
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.filter_Skulink,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': judge_skuList_type,
    #                       'np_i': copy.deepcopy(np_i)},
    #                 dont_filter=True
    #             )
    #
    #     # 过滤重复url
    #     def filter_Skulink(self, response):
    #         np_i = response.meta['np_i']
    #         item = response.meta['item']
    #         judge_skuList_type = response.meta['judge_skuList_type']
    #
    #         # # 读取保存sku数据列表（用来存储sku数据）
    #         load_dict = np.load('E:\my_file.npy', allow_pickle=True).item()
    #         np_filter_result_dict = load_dict['filter_result_dict'][np_i]
    #
    #         # 根据不同的sku列表进行不同操作
    #         if judge_skuList_type == 'judge_nodes1':
    #             print(judge_skuList_type)
    #             # 定义去重后数组
    #             sku_nodes2 = response.xpath('//*[@id="twister"]//li')
    #             for skuLink2 in sku_nodes2:
    #                 patter = re.compile("ref=\S+")
    #                 newskuLink2 = patter.sub("", response.urljoin(skuLink2.xpath('./@data-dp-url').extract_first()))
    #                 # 如果链接在去重数组中存在，则不添加，不存在则添加,(为了得到去重后的数量数组，可以在后面getskudata时进行判断什么时候提交数据)
    #                 if newskuLink2 not in np_filter_result_dict:
    #                     # 把不重复的链接存入数组
    #                     np_filter_result_dict.append(newskuLink2)
    #                     # 实时保存sku数据列表（不保存会为空）
    #                     np.save('E:\my_file.npy', load_dict)
    #                     yield scrapy.Request(
    #                         url=newskuLink2,
    #                         callback=self.get_commodity_data,
    #                         meta={'item': copy.deepcopy(item),
    #                               'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                               'np_i': copy.deepcopy(np_i)},
    #                         dont_filter=False,
    #                     )
    #         elif judge_skuList_type == 'judge_nodes2':
    #             sku_nodes = response.xpath('//*[@id="twister-plus-inline-twister"]//li')
    #             for skuLink in sku_nodes:
    #                 # 有多余的没有编码的li
    #                 skuLink2 = skuLink.xpath('./@data-asin')
    #                 # 去除多余的没有编码的li
    #                 if len(skuLink2) != 0:
    #                     newskuLink = "https://www.amazon.cn/dp/" + skuLink2.extract_first() + "?th=1&psc=1"
    #                     if newskuLink not in np_filter_result_dict:
    #                         # 把不重复的链接存入数组
    #                         np_filter_result_dict.append(newskuLink)
    #                         # 实时保存sku数据列表（不保存会为空）
    #                         np.save('E:\my_file.npy', load_dict)
    #                         yield scrapy.Request(
    #                             url=newskuLink,
    #                             callback=self.get_commodity_data,
    #                             meta={'item': copy.deepcopy(item),
    #                                   'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                                   'np_i': copy.deepcopy(np_i)},
    #                             dont_filter=False,
    #                         )
    #
    #         elif judge_skuList_type == 'judge_nodes3':
    #             # 因为3和2提取数据方式一样，所以3重定向到2
    #             judge_skuList_type = 'judge_nodes2'
    #             print(judge_skuList_type)
    #             # 把不重复的链接存入数组（这里其实不用，为了统一后面操作）
    #             np_filter_result_dict.append(item['commodity_link'])
    #             # 实时保存sku数据列表（不保存会为空）
    #             np.save('E:\my_file.npy', load_dict)
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.get_commodity_data,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                       'np_i': copy.deepcopy(np_i)},
    #                 dont_filter=False
    #             )
    #         elif judge_skuList_type == 'judge_nodes5':
    #             # 因为5和1提取数据方式一样，所以5重定向到1
    #             judge_skuList_type = 'judge_nodes1'
    #             print(judge_skuList_type)
    #             # 把不重复的链接存入数组（这里其实不用，为了统一后面操作）
    #             np_filter_result_dict.append(item['commodity_link'])
    #             # 实时保存sku数据列表（不保存会为空）
    #             np.save('E:\my_file.npy', load_dict)
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.get_commodity_data,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                       'np_i': copy.deepcopy(np_i)},
    #                 dont_filter=False
    #             )
    #         elif judge_skuList_type == 'judge_nodes4':
    #             print(judge_skuList_type)
    #             # 把不重复的链接存入数组（这里其实不用，为了统一后面操作）
    #             np_filter_result_dict.append(item['commodity_link'])
    #             # 实时保存sku数据列表（不保存会为空）
    #             np.save('E:\my_file.npy', load_dict)
    #             yield scrapy.Request(
    #                 url=item['commodity_link'],
    #                 callback=self.get_commodity_data,
    #                 meta={'item': copy.deepcopy(item),
    #                       'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                       'np_i': copy.deepcopy(np_i)},
    #                 dont_filter=False
    #             )
    #         elif judge_skuList_type == 'judge_nodes6':
    #             # 因为6和1提取数据方式一样，所以6重定向到1
    #             print(judge_skuList_type)
    #             select_nodes2 = response.xpath('//*[@id="twister"]//select/option')
    #             # 存放select_skuLink和li_skuLink所有链接的列表，最后再一起发送请求
    #             select_list = []
    #             for select_skuLink in select_nodes2:
    #                 select_value = select_skuLink.xpath('./@value').extract_first()
    #                 if select_value != '-1':
    #                     patter = re.compile("\S+,")
    #                     newselect_value = patter.sub("", select_value)
    #                     newselect_skuLink = "https://www.amazon.cn/dp/" + newselect_value + "?th=1&psc=1"
    #                     select_list.append(newselect_skuLink)
    #             sku_nodes = response.xpath('//*[@id="twister"]//li')
    #             for skuLink in sku_nodes:
    #                 # 匹配sku链接正则,修改链接
    #                 patter = re.compile("ref=\S+")
    #                 newskuLink = patter.sub("", response.urljoin(skuLink.xpath('./@data-dp-url').extract_first()))
    #                 select_list.append(newskuLink)
    #             for select_list_sku in select_list:
    #                 # 如果链接在去重数组中存在，则不添加，不存在则添加,(为了得到去重后的数量数组，可以在后面getskudata时进行判断什么时候提交数据)
    #                 if select_list_sku not in np_filter_result_dict:
    #                     # 把不重复的链接存入数组
    #                     np_filter_result_dict.append(select_list_sku)
    #                     # 实时保存sku数据列表（不保存会为空）
    #                     np.save('E:\my_file.npy', load_dict)
    #                     yield scrapy.Request(
    #                         url=select_list_sku,
    #                         callback=self.get_commodity_data,
    #                         meta={'item': copy.deepcopy(item),
    #                               'judge_skuList_type': copy.deepcopy(judge_skuList_type),
    #                               'np_i': copy.deepcopy(np_i)},
    #                         dont_filter=False
    #                     )
    #
    #     # 获取商品数据
    #     def get_commodity_data(self, response):
    #         # 判断是否登录成功
    #         print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #
    #         np_i = response.meta['np_i']
    #         # 读取sku数据列表和存储商品数据列表，通过两者对比，相等就提交数据到数据库
    #         load_dict = np.load('E:\my_file.npy', allow_pickle=True).item()
    #         filter_result_dict = load_dict['filter_result_dict']
    #         np_filter_result_dict = filter_result_dict[np_i]
    #         filter_commodity_dict = load_dict['filter_commodity_dict']
    #         np_filter_commodity_dict = filter_commodity_dict[np_i]
    #
    #         item = response.meta['item']
    #         judge_skuList_type = response.meta['judge_skuList_type']
    #         # getSku_data存放整体数据字典
    #         commodity_data_dict = {}
    #         # 图片列表
    #         commodityImage_link_list = []
    #
    #         # sku_link链接
    #         commodity_data_dict['sku_link'] = response.url
    #
    #         # 根据不同的sku列表进行不同操作
    #         if judge_skuList_type == 'judge_nodes1':
    #             # sku_属性：值
    #             sku_classification = response.xpath('//*[@id="twister"]/div/div')
    #             for sku_type_classification in sku_classification:
    #                 sku_type = sku_type_classification.xpath('.//label/text()').extract_first().strip()
    #                 sku_value = sku_type_classification.xpath('.//span/text()').extract_first().strip()
    #                 commodity_data_dict[sku_type] = sku_value
    #
    #         elif judge_skuList_type == 'judge_nodes2':
    #             # sku_属性：值
    #             sku_classification = response.xpath('//*[@id="twister-plus-inline-twister"]/div')
    #             for sku_type_classification in sku_classification:
    #                 classification = sku_type_classification.xpath('./span/div/div/div/span[1]/text()')
    #                 if len(classification) != 0:
    #                     sku_type = sku_type_classification.xpath(
    #                         './span/div/div/div/span[1]/text()').extract_first().strip()
    #                     sku_value = sku_type_classification.xpath(
    #                         './span/div/div/div/span[2]/text()').extract_first().strip()
    #                     commodity_data_dict[sku_type] = sku_value
    #                 else:
    #                     sku_type = sku_type_classification.xpath('./span[1]/text()').extract_first().strip()
    #                     sku_value = sku_type_classification.xpath('./span[2]/text()').extract_first().strip()
    #                     commodity_data_dict[sku_type] = sku_value
    #         # 因为judge_nodes3的处理方式和judge_nodes2一致，所以在这里不用考虑judge_nodes3
    #         elif judge_skuList_type == 'judge_nodes4':
    #             commodity_data_dict['sku_type'] = '无sku，只有一个'
    #
    #         elif judge_skuList_type == 'judge_nodes6':
    #             # sku_属性：值
    #             sku_classification = response.xpath('//*[@id="twister"]/div')
    #             for sku_type_classification in sku_classification:
    #                 sku1_classification = sku_type_classification.xpath('.//select')
    #                 sku2_classification = sku_type_classification.xpath('./ul')
    #                 if len(sku1_classification) != 0:
    #                     sku_type = sku_type_classification.xpath('./div[2]/label/text()').extract_first().strip()
    #                     sku_value = sku_type_classification.xpath(
    #                         './/option[@class="dropdownSelect"]/text()').extract_first()
    #                     commodity_data_dict[sku_type] = sku_value
    #                 elif len(sku2_classification) != 0:
    #                     sku_type = sku_type_classification.xpath('./div/label/text()').extract_first().strip()
    #                     sku_value = sku_type_classification.xpath('./div/span/text()').extract_first().strip()
    #                     commodity_data_dict[sku_type] = sku_value
    #
    #         # 商品名
    #         commodity_data_dict['commodity_name'] = response.xpath('//*[@id="productTitle"]/text()')[
    #             0].extract().strip()
    #         if len(response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')) != 0:
    #             # 商品价格
    #             # 把¥字符替换成空
    #             commodity_price = re.sub('¥', "", response.xpath(
    #                 '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')[0].extract().strip())
    #             commodity_data_dict['commodity_price'] = commodity_price
    #         elif len(response.xpath('//*[@id="corePrice_desktop"]/div/table/tr[1]/td[2]/span[1]/span[1]/text()')) != 0:
    #             # 商品价格
    #             # 把¥字符替换成空
    #             commodity_price = re.sub('¥', "", response.xpath(
    #                 '//*[@id="corePrice_desktop"]/div/table/tr[1]/td[2]/span[1]/span[1]/text()')[0].extract().strip())
    #             commodity_data_dict['commodity_price'] = commodity_price
    #         else:
    #             commodity_data_dict['commodity_price'] = '商品目前无货'
    #
    #         # 商品图片
    #         image_classification = response.xpath('//*[@id="altImages"]/ul/li[@class="a-spacing-small item"]')
    #         for image_link_classification in image_classification:
    #             image_link = re.sub("._AC_US40_", "", image_link_classification.xpath('.//img/@src').extract_first())
    #             commodityImage_link_list.append(image_link)
    #         commodity_data_dict['commodityImage_link'] = commodityImage_link_list
    #
    #         # 把商品数据统一添加到商品数组
    #         np_filter_commodity_dict.append(commodity_data_dict)
    #         # 实时保存存储商品数据列表（不保存会为空）
    #         np.save('E:\my_file.npy', load_dict)
    #         print(str(np_i) + '\n' + str(len(np_filter_result_dict)) + '\n' + str(len(np_filter_commodity_dict)))
    #
    #         # 根据商品数据数组大小和去重的sku数据数组大小是否相等来判断提交数据
    #         if len(np_filter_commodity_dict) == len(np_filter_result_dict):
    #             item['commodity_data'] = np_filter_commodity_dict
    #             yield item



















    # # 获取每个商品数据
    # def get_commodity_data(self, response):
    #     print(response.xpath('//*[@id="nav-link-accountList-nav-line-1"]/text()').extract_first())
    #     item = response.meta['item']
    #     # 获取sku参数列表xpath
    #     print(str(len(response.xpath('//*[@id="twister"]'))))
    #
    #     # 如果没有sku参数列表，则直接爬取数据
    #     if len(response.xpath('//*[@id="twister"]')) == 0:
    #         item['commodity_name'] = response.xpath('//*[@id="productTitle"]/text()')[0].extract().strip()
    #         if len(response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')) != 0:
    #             # 把¥字符替换成空
    #             commodity_price = re.sub('¥', "", response.xpath(
    #                 '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span/span[1]/text()')[0].extract().strip())
    #             item['commodity_price'] = commodity_price
    #         else:
    #             # 把¥字符替换成空
    #             commodity_price = re.sub('¥', "", response.xpath(
    #                 '//*[@id="corePrice_desktop"]/div/table/tr[1]/td[2]/span[1]/span[1]/text()')[0].extract().strip())
    #             item['commodity_price'] = commodity_price
    #
    #         # item['commodity_Imge_link'] = response.xpath('//*[@class="a-spacing-small item imageThumbnail a-declarative"]//img/@src')[0].extract()
    #         yield item
    #
    #     # 如果有sku参数列表，则构建每一个sku链接
    #     # else:

































    #逐级链接爬取 批量翻页
    # def make_requests_from_url(self, url):
    #     # 存放数据
    #     item = {}
    #     # 数据名字标识
    #     i = 0
    #     return scrapy.Request(url,
    #                           dont_filter=False,
    #                           meta={'item1': item,"i":i},
    #                           )
    #
    #
    #
    #
    #
    # # 处理链接数据
    # def parse(self, response):
    #     item = response.meta['item1']
    #     i = response.meta['i']
    #
    #     # 判断目录
    #     # 根据最后一个目录有没有链接来判断是不是最后一级目录
    #     last_classification = response.xpath('//*[@id="departments"]/ul/li[last()]/span/a')
    #
    #     # 目录到底则爬取对应商品数据
    #     if len(last_classification) == 0:
    #         # 判断翻页
    #         #获取页数控件，根据有没有控件来确定请求链接数
    #         sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')
    #         # 没有页数，只有一页则直接请求一页
    #         if len(sum_pages) == 0:
    #             yield scrapy.Request(
    #                 # url="https://www.amazon.cn/s?i=toys&srs=1546136071&bbn=1546134071&dc&page="+str(page)+"&qid=1651988262&ref=sr_pg_23",
    #                 url=item['big_classification_link' + str(i - 1)] + '&page=1',
    #                 callback=self.get_commodity_data,
    #                 meta={'item1': copy.deepcopy(item)},
    #                 dont_filter=False
    #             )
    #         else:
    #             # 有页数，有页数则构建多页请求
    #             sum_pages = response.xpath('//*[@class="s-pagination-strip"]/span[last()]/text()')[0].extract()
    #             print("1111111111111111111111111111111111111111111111111" + str(sum_pages))
    #             for page in range(1, int(sum_pages) + 1):
    #                 print("1111111111111111111111" + item['big_classification_link' + str(i - 1)] + '&page=' + str(page))
    #                 # 构造商品页数链接，批量发起请求
    #                 yield scrapy.Request(
    #                     # url="https://www.amazon.cn/s?i=toys&srs=1546136071&bbn=1546134071&dc&page="+str(page)+"&qid=1651988262&ref=sr_pg_23",
    #                     url=item['big_classification_link' + str(i - 1)] + '&page=' + str(page),
    #                     callback=self.get_commodity_data,
    #                     meta={'item1': copy.deepcopy(item)},
    #                     dont_filter=False
    #                 )
    #
    #
    #     # 目录没到底则继续请求下一目录
    #     else:
    #         # 获取二级目录总链接
    #         node_list = response.xpath('//*[@class="a-spacing-micro s-navigation-indent-2"]')
    #
    #         # 判断二级目录为空则进行一级目录爬取，不为空则进行二级目录爬取，防止二级目录中存在一级目录而导致重复爬取
    #         if len(node_list) == 0:
    #             # 一级
    #             classification_node_list = response.xpath('//*[@class="a-spacing-micro"]')
    #         else:
    #             # 二级
    #             classification_node_list = response.xpath('//*[@class="a-spacing-micro s-navigation-indent-2"]')
    #
    #         for classification_node in classification_node_list:
    #             item['big_classification_text'+str(i)] = classification_node.xpath('./span/a/span/text()')[0].extract().strip()
    #             item['big_classification_link'+str(i)] = response.urljoin(classification_node.xpath('./span/a/@href')[0].extract())
    #             yield scrapy.Request(
    #                 url=item['big_classification_link'+str(i)],
    #                 callback=self.parse,
    #                 meta={'item1': copy.deepcopy(item),"i":i+1},
    #                 dont_filter = False
    #             )
    #
    #
    # # 处理商品数据
    # # 没有目录了则抓取商品数据
    # def get_commodity_data(self, response):
    #     print("ccccccccccccccccccccccccccccccccccccccccccccc", response.request.headers['User-Agent'])
    #     item = response.meta['item1']
    #     commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div[@class="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"]')
    #     for commodity_node in commodity_node_list:
    #         item['commodity_link'] = response.urljoin(commodity_node.xpath('.//h2/a/@href')[0].extract())
    #         yield item

















#逐级链接爬取 一页一页翻
# #一级目录
#     def parse(self, response):
#         item = response.meta['item1']
#         i =response.meta['i']
#
#         classification_node_list=response.xpath('//*[@id="departments"]/ul/li/span/a')
#
#
#         if len(classification_node_list) == 0:
#             commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div[@class="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"]')
#             for commodity_node in commodity_node_list:
#                 item['commodity_link'] = response.urljoin(commodity_node.xpath('.//h2/a/@href')[0].extract())
#                 yield item
#
#             # 翻页
#             # 判断是否是最后一页的依据
#             aa = response.xpath('//*[@class="s-pagination-strip"]/a[last()]/@class').extract_first()
#             # 翻页请求链接
#             part_url = response.xpath('//*[@class="s-pagination-strip"]/a[last()]/@href').extract_first()
#             # 判断是否是最后一页
#             if aa != 's-pagination-item s-pagination-button':
#                 print("1111111111111111111111111111111111111111111111111111111111111111111111111下一页")
#                 next_url = response.urljoin(part_url)
#                 yield scrapy.Request(
#                     url=next_url,
#                     callback=self.get_commodity_data,
#                     meta={'item1': copy.deepcopy(item)}
#                 )
#
#         for classification_node in classification_node_list:
#             item['big_classification_text'+str(i)] = classification_node.xpath('./span/text()')[0].extract().strip()
#             item['big_classification_link'+str(i)] = response.urljoin(classification_node.xpath('./@href')[0].extract())
#             yield scrapy.Request(
#                 url=item['big_classification_link'+str(i)],
#                 callback=self.parse,
#                 meta={'item1': copy.deepcopy(item),"i":i+1}
#             )
#
#
#     # 没有目录了则抓取商品数据
#     def get_commodity_data(self, response):
#         print("ccccccccccccccccccccccccccccccccccccccccccccc", response.request.headers['User-Agent'])
#         item = response.meta['item1']
#         commodity_node_list = response.xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div[@class="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"]')
#         for commodity_node in commodity_node_list:
#             item['commodity_link'] = response.urljoin(commodity_node.xpath('.//h2/a/@href')[0].extract())
#             yield item
#         # 判断是否是最后一页的依据
#         aa=response.xpath('//*[@class="s-pagination-strip"]/a[last()]/@class').extract_first()
#         # 翻页请求链接
#         part_url = response.xpath('//*[@class="s-pagination-strip"]/a[last()]/@href').extract_first()
#         # 判断是否是最后一页
#         if aa != 's-pagination-item s-pagination-button':
#             next_url = response.urljoin(part_url)
#             yield scrapy.Request(
#                 url=next_url,
#                 callback=self.get_commodity_data,
#                 meta={'item1': copy.deepcopy(item)}
#             )
