import json
import re
from pprint import pprint
from lxml import etree

import requests

# skuLink = 'https://www.aliexpress.com/category/6/home-appliances.html?spm=a2g0o.category_nav.1.21.6b6548b6TfpGQq'
# 两者一样效果
# 第一种
# patter = re.compile("spm=\S+")
# aa = patter.findall(skuLink)[0]
# print(aa)

#
# newskuLink= patter.sub("", skuLink)
# newskuLink2 = newskuLink + '?th=1&psc=1'

# 第二种
# patter2 = re.compile("/ref=\w.+")
#
# newsku = patter2.sub("", skuLink)
#
# print(newsku)

# 分割字符，返回列表，取sku码

# skuLink = '/dp/B01E5279IO/ref=twister_B01HHOY15Q?_encoding=UTF8&psc=1'
#
# patter = re.compile("/")
#
# newskuLink= patter.split(skuLink)
#
# print(newskuLink[2])


# file = open("als.json", 'w', encoding='utf-8')
# file.write(str(new_commodity_json_data))
# file.close()


# 速卖通
url = 'https://www.aliexpress.com/item/1005003728774060.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
}
response = requests.get(url=url, headers=headers)
data_obj = response.text
# print(data_obj)
# 匹配数据
patter = re.compile("data: (.*),")
commodity_htmldata = patter.findall(data_obj)[0]
# print(commodity_htmldata)
# 匹配数据转为json
new_commodity_json_data = json.loads(commodity_htmldata)
print(new_commodity_json_data)
# # 解析数据
# # 属性大小（有多少个属性）
# productSKUPropertyList_len = len(new_commodity_json_data['skuModule']['productSKUPropertyList'])
# # 属性对应价格数量（有多少个属性价格）
# skuPriceList_len = len(new_commodity_json_data['skuModule']['skuPriceList'])
# # 存放所有sku的列表
# sku_list = []
# # 根据属性对应价格数量循环
# for k in range(skuPriceList_len):
#     # 存sku的字典
#     commodity_data_dict = {}
#     # 根据属性大小（有多少个属性）循环
#     for i in range(productSKUPropertyList_len):
#         # 获取属性id和属性
#         skuPropertyId = new_commodity_json_data['skuModule']['productSKUPropertyList'][i]['skuPropertyId']
#         skuPropertyName = new_commodity_json_data['skuModule']['productSKUPropertyList'][i]['skuPropertyName']
#         # 获取属性值大小
#         skuPropertyValues_len = len(new_commodity_json_data['skuModule']['productSKUPropertyList'][i]['skuPropertyValues'])
#         # 根据属性值大小循环（一个属性对应多个属性值）
#         for j in range(skuPropertyValues_len):
#             # 获取属性值id和属性值
#             propertyValueId = new_commodity_json_data['skuModule']['productSKUPropertyList'][i]['skuPropertyValues'][j]['propertyValueId']
#             propertyValueName = new_commodity_json_data['skuModule']['productSKUPropertyList'][i]['skuPropertyValues'][j]['propertyValueDisplayName']
#             # 结合属性id和属性值id去匹配价格对应搭配的sku，再把属性id和属性值id替换成对应的属性和属性值，形成整体的sku字典
#             if str(skuPropertyId) + ':' + str(propertyValueId) in new_commodity_json_data['skuModule']['skuPriceList'][k]['skuAttr']:
#                 # 单个sku，每循环一次就匹配取出一个sku,直到价格的所有sku匹配完毕
#                 commodity_data_dict[skuPropertyName] = propertyValueName
#             # 获取sku搭配价格(有两种，一种是打折前skuAmount，一种是打折后skuActivityAmount，有些没打折的会出错，所以要捕获错误)
#             try:
#                 # 打折后（有些没有打折）
#                 skuPrice = new_commodity_json_data['skuModule']['skuPriceList'][0]['skuVal']['skuActivityAmount']['value']
#             except:
#                 # 没打折
#                 skuPrice = new_commodity_json_data['skuModule']['skuPriceList'][0]['skuVal']['skuAmount']['value']
#             commodity_data_dict['skuPrice'] = skuPrice
#     # 循环结束再输出完整的sku字典，再把完整的sku添加到sku列表
#     # print(commodity_data_dict)
#     sku_list.append(commodity_data_dict)
# print(sku_list)




# ebay

# # ebay获取全部数据
# # url = 'https://www.ebay.com/itm/393654174887'
# url = 'https://www.ebay.com/itm/263152510858'
# # url = 'https://www.ebay.com/itm/133170599663'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
# }
# response = requests.get(url=url, headers=headers)
# data_obj = response.text
# # print(data_obj)
#
# # 匹配数据
# patter = re.compile('rwidgets\((.*)\);new')
# commodity_htmldata = patter.findall(data_obj)[0]
# # print(commodity_htmldata)
#
# # '会导致转json失败，所以把'替换成“
# patter2 = re.compile("'")
# newcommodity_htmldata = patter2.sub('"', commodity_htmldata)
# # print(newcommodity_htmldata)
#
# # 匹配数据转为json
# new_commodity_json_data = json.loads("["+newcommodity_htmldata+"]")
# # print(new_commodity_json_data)
#
# # 不同商品页面数据大小不一，按顺序查找会出错，所以通过循环数据第一个数据来确定数据节点
# for i in range(len(new_commodity_json_data)):
#     # 获取sku节点
#     if new_commodity_json_data[i][0] == "com.ebay.raptor.vi.msku.ItemVariations":
#         ItemVariations = new_commodity_json_data[i]
#     # 获取物品状况（新旧二手）节点
#     elif new_commodity_json_data[i][0] == "raptor.vi.ActionPanel":
#         ActionPanel = new_commodity_json_data[i]
#
# # 属性名称存入列表）
# sku_type_dict = []
# # 储存去重的matchingVariationIds的列表
# matchingVariationId_duplicate_dict = []
# # 存放所有sku的列表
# sku_list = []
# # 属性字典大小
# menuModels_len = len(ItemVariations[2]['itmVarModel']['menuModels'])
# # 根据属性字典大小循环
# for menuModel in range(menuModels_len):
#     # 获取属性名称存入列表为后面备用
#     sku_type_dict.append(ItemVariations[2]['itmVarModel']['menuModels'][menuModel]['displayName'])
#     # 获取属性id列表
#     menuItemValueIds = ItemVariations[2]['itmVarModel']['menuModels'][menuModel]['menuItemValueIds']
#     # 根据属性id列表大小循环获取对应skuid列表
#     for menuItemValueId in menuItemValueIds:
#         # 获取每个skuid
#         matchingVariationIds = ItemVariations[2]['itmVarModel']['menuItemMap'][str(menuItemValueId)]['matchingVariationIds']
#         # 把获取的skuid去重存入新skuid列表
#         for matchingVariationId in matchingVariationIds:
#             if matchingVariationId not in matchingVariationId_duplicate_dict:
#                 matchingVariationId_duplicate_dict.append(matchingVariationId)
#
# # 循环新skuid列表取出对应sku数据
# for matchingVariationId in matchingVariationId_duplicate_dict:
#     # 存放sku字典
#     sku_And_price_dict = {}
#     # 循环新前面备用的属性列表匹配对应sku属性值
#     for sku_type in sku_type_dict:
#         sku_type_id = ItemVariations[2]['itmVarModel']['itemVariationsMap'][str(matchingVariationId)]['traitValuesMap'][sku_type]
#         # 属性值
#         sku_value = ItemVariations[2]['itmVarModel']['menuItemMap'][str(sku_type_id)]['valueName']
#         # 存入字典
#         sku_And_price_dict[sku_type] = sku_value
#     # 物品状况
#     sku_And_price_dict['物品状况'] = ActionPanel[2]['isModel']['itmCondition']
#     # 价格
#     price = ItemVariations[2]['itmVarModel']['itemVariationsMap'][str(matchingVariationId)]['price']
#     sku_And_price_dict['price'] = price
#     # 存入所有sku的列表
#     sku_list.append(sku_And_price_dict)
#
# print(sku_list)




# 亚马逊
#
# url = 'https://www.amazon.cn/dp/B0B4646SBH'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
# }
# response = requests.get(url=url, headers=headers)
# data_obj = response.text
# # print(data_obj)
#
# # 匹配数据
# # patter = re.compile('jQuery.parseJSON\(\'(.*)\'\);')
# patter = re.compile('"asinVariationValues" : (.*),')
# commodity_htmldata = patter.findall(data_obj)[0]
# # print(commodity_htmldata)
#
# # # # 匹配数据转为json
# commodity_json_data = json.loads(commodity_htmldata)
# # print(new_commodity_json_data)
# # .keys取出字典的健（.keys可以取出字典的健（valuas可以取出字典的值,取出后会是一个元组）
# sku_ids_tuple = commodity_json_data.keys()
# # 取出的是一个元组，把元组转成列表（元组转列表list()，列表转元组tuple()）
# sku_ids = list(sku_ids_tuple)
# print(len(sku_ids))
#
# commodity_datas_list = []
# for sku_id in sku_ids:
#     commodity_datas_dict = {}
#
#     commodity_url = 'https://www.amazon.cn/dp/'+sku_id
#     response = requests.get(url=commodity_url, headers=headers)
#     data_obj = response.text
#     tree = etree.HTML(data_obj)
#     # 获取商品名
#     commodity_name = tree.xpath('//*[@id="productTitle"]/text()')[0]
#     commodity_datas_dict['commodity_name'] = commodity_name
#     # 获取价格数据
#     price_data = tree.xpath('//*[@class="a-section aok-hidden twister-plus-buying-options-price-data"]/text()')[0]
#     price_json_data = json.loads(price_data)
#     commodity_price = price_json_data[0]['priceAmount']
#     commodity_datas_dict['commodity_price'] = commodity_price
#     # print(commodity_name,commodity_price)
#
#     # 匹配sku数据节点
#     #(sku值数据)variationValues节点数据
#     sku_values_patter = re.compile('"variationValues" : (.*),')
#     sku_values_htmldata = sku_values_patter.findall(data_obj)[0]
#     # 匹配数据转为json
#     sku_values_json_data = json.loads(sku_values_htmldata)
#     # print(sku_values_json_data)
#
#     #（sku属性数据）variationDisplayLabels节点数据
#     sku_types_patter = re.compile('"variationDisplayLabels" : (.*),')
#     sku_types_htmldata =sku_types_patter.findall(data_obj)[0]
#     # 匹配数据转为json
#     sku_types_json_data = json.loads(sku_types_htmldata)
#     print(sku_types_json_data)
#
#     # （sku属性和属性值代号数据）asinVariationValues节点数据
#     skuData_patter = re.compile('"asinVariationValues" : (.*),')
#     skuData_htmldata =skuData_patter.findall(data_obj)[0]
#     # # 匹配数据转为json
#     skuData_json_data = json.loads(skuData_htmldata)
#     # print(skuData_json_data)
#     # 获取sku_id对应sku数据
#
#     sku_type_list = list(sku_types_json_data.keys())
#
#     sku_dict = {}
#     for sku_type_id in sku_type_list:
#         print(sku_type_id)
#         sky_value_id = skuData_json_data[sku_id][sku_type_id]
#
#         sky_type = sku_types_json_data[sku_type_id]
#         sky_value = sku_values_json_data[sku_type_id][int(sky_value_id)]
#         sku_dict[sky_type] = sky_value
#
#     commodity_datas_dict['sku_data'] = sku_dict
#
#
#     commodity_datas_list.append(commodity_datas_dict)
#
# print(commodity_datas_list)