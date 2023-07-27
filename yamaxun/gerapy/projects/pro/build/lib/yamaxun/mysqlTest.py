import json

import MySQLdb
import redis
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf8",line_buffering=True)
def process_item():
    rediscli = redis.Redis(host="127.0.0.1",port=6379,db=0)

    mysqlcli = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="123456",db="test")
    while True:

        source,data = rediscli.blpop("amazon:items")
        item = json.loads(data)
        print(item)


        cursor = mysqlcli.cursor()

        cursor.execute('insert into amazon_data (page_link,commodity_link,judge_skuList_type,sku_link,sku_type,commodity_name,commodity_price,commodity_Imge_link) value (%s,%s,%s,%s,%s,%s,%s,%s)',(item['page_link'],item['commodity_link'],item['judge_skuList_type'],item['sku_link'],item['sku_type'],item['commodity_name'],item['commodity_price'],item['commodity_Imge_link']))
        # cursor.execute('insert into AMAZON (commodity_link,judge_skuList_type,sku_link,sku_type,commodity_name,commodity_price,commodity_Imge_link) value (%s,%s,%s,%s,%s,%s,%s)',
        #     (item['commodity_link'], item['judge_skuList_type'], item['sku_link'], item['sku_type'],
        #      item['commodity_name'], item['commodity_price'], item['commodity_Imge_link']))
        mysqlcli.commit()




if __name__ == '__main__':
    process_item()
