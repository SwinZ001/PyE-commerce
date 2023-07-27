import json

import MySQLdb
import redis
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf8",line_buffering=True)
def process_item():
    rediscli = redis.Redis(host="127.0.0.1",port=6379,db=0)

    mysqlcli = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="123456",db="test")

    # while True:
        # list
        # source,data = rediscli.blpop("amazon:items")
        # source, data = rediscli.blpop("aliexpress:items")
        # source, data = rediscli.blpop("shopee:items")
        # source, data = rediscli.blpop("aliexpress:comments")
        # source, data = rediscli.blpop("shopee:comments")
        # item = json.loads(data)

    # set
    # data_dict = rediscli.smembers("shopee:items")
    # data_dict = rediscli.smembers("aliexpress:items")
    # data_dict = rediscli.smembers("shopee:comments")
    data_dict = rediscli.smembers("amazon:items")
    for data in data_dict:
        new_data = data.decode('utf-8')
        item = json.loads(new_data)
        print(item)


        cursor = mysqlcli.cursor()

        # cursor.execute('insert into amazon_data (page_link,commodity_link,judge_skuList_type,sku_link,sku_type,commodity_name,commodity_price,commodity_Imge_link) value (%s,%s,%s,%s,%s,%s,%s,%s)',(item['page_link'],item['commodity_link'],item['judge_skuList_type'],item['sku_link'],item['sku_type'],item['commodity_name'],item['commodity_price'],item['commodity_Imge_link']))
        # cursor.execute('insert into AMAZON (commodity_link,judge_skuList_type,sku_link,sku_type,commodity_name,commodity_price,commodity_Imge_link) value (%s,%s,%s,%s,%s,%s,%s)',
        #     (item['commodity_link'], item['judge_skuList_type'], item['sku_link'], item['sku_type'],
        #      item['commodity_name'], item['commodity_price'], item['commodity_Imge_link']))
        # cursor.execute('insert into aliexpress (commodity_link,sku_list) value (%s,%s)',(item['commodity_link'], item['sku_list']))

        # cursor.execute('insert into comments (page,commentcs_link,comments) value (%s,%s,%s)',(item['page'], item['comment_data_link'], item['comment_data']))
        # cursor.execute('insert into aliexpress (commodity_link,commodity_name,historical_sold,discount,rating_star,commodity_Imge_link,attributes,description,store_data,sku_list) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (item['commodity_link'], item['commodity_name'], item['historical_sold'], item['discount'],
        #                                                                                                     str(item['rating_star']), str(item['commodity_Imge_link']), str(item['attributes']), item['description'],
        #                                                                                                     str(item['store_data']), str(item['sku_list'])))
        cursor.execute('insert into amazon (startUrl,commodity_link,commodity_name,skulist) value (%s,%s,%s,%s)',(item['startUrl'], item['commodity_link'], item['commodity_name'], str(item['sku_list'])))
        mysqlcli.commit()




if __name__ == '__main__':
    process_item()

