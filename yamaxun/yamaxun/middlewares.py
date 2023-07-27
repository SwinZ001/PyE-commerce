# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random
from time import sleep
import re
from scrapy import signals
import undetected_chromedriver.v2 as uc
from lxml import etree
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http import HtmlResponse
from scrapy.utils.request import request_fingerprint
from selenium.webdriver.common.by import By
from twisted.internet import defer
from twisted.web._newclient import ResponseFailed
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError, DNSLookupError, ConnectionDone, ConnectError,ConnectionLost
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.action_chains import ActionChains
from yamaxun.settings import USER_AGENT_LIST,PROXY_LIST,RETRY_HTTP_CODES

# 随机ip
class Middlewares(object):
    # 网络异常错误
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError, ConnectionRefusedError, ConnectionDone, ConnectError,ConnectionLost, TCPTimedOutError, ResponseFailed, IOError, TunnelError, IndexError)

    def __init__(self):
        # 初始化顺序ip
        self.i = 0

    # 请求时调用
    def process_request(self, request, spider):
        # 随机ip
        # proxys = random.choice(PROXY_LIST)
        # proxy = 'https://' + str(proxys)
        # print(proxy)
        # request.meta['proxy'] = proxy
        #  顺序ip
        # proxys = PROXY_LIST[self.i]
        # proxy = 'https://' + str(proxys)
        # print(proxy)
        # request.meta['proxy'] = proxy
        # 随机User-Agent
        ua = random.choice(USER_AGENT_LIST)
        request.headers['User-Agent'] = ua
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Accept-Language'] = 'zh-CN'
        if 'ATVPDKIKX0DER' in request.url:
            request.headers['Accept'] = 'application/vnd.com.amazon.api+json; type="cart.add-items/v1"'
            request.headers['Origin'] = 'https://www.amazon.com'
            request.headers['Content-Type'] = 'application/vnd.com.amazon.api+json; type="cart.add-items.request/v1"'
         # x-api-csrf-token在spider动态生成添加，不在这里添加
            # request.headers['x-api-csrf-token'] = '1@gyVVmZd7rRv4xRA5JmaFRSjX4RNCjI3VGRctj0zjpv07AAAAAQAAAABjgupbcmF3AAAAABVX8CwXqz42z+J7i/ABqA==@NLD_Y47GLU'
         # 不必要参数
            # request.headers['Cookie'] = 'session-id=136-6298940-5529567; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=132-4276056-1407021; skin=noskin; session-token="Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="'
            # request.headers['Connection'] = 'keep-alive'
         # Content-Length在scrapy中加了会访问不到数据返回500，所以不要添加该参数
            # request.headers['Content-Length'] = '100'
            # request.headers['Host'] = 'data.amazon.com'
            # request.headers['Referer'] = 'https://www.amazon.com/'
            # request.headers['sec-ch-ua'] = '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'
            # request.headers['sec-ch-ua-mobile'] = '?0'
            # request.headers['sec-ch-ua-platform'] = 'Windows'
            # request.headers['Sec-Fetch-Dest'] = 'empty'
            # request.headers['Sec-Fetch-Mode'] = 'cors'
            # request.headers['Sec-Fetch-Site'] = 'same-site'
        else:
            request.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            # request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            # request.headers['Cookie'] = 'session-id=136-6298940-5529567; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=132-4276056-1407021; skin=noskin; session-token="Af060Du9+75fbR0qpwWBLgZb5dP2Oo1gwhMEygmn2xaSQ/LeaOv0LtISbckjMU/+xN9UMtBx1HPfGsFgyNdYU3szl8t1SlJNlaTgtkUxb+LdHwmku2eU2YAnxzD3MbBLhv/z5xGt6S78495QnWJ+Gd1cx+rQhO9gflO3/xY1d49uqpQaWmZe+epiYhkcDcvSd74lizgNYRQyb45hxCF0guf3DZsSZVHUH7xoV0dlvWY="',




        # if spider.name == "shopee":
        #     url = request.url
        #
        #     if '1151500' in url:
        #         bro = self.chrome_set()
        #
        #         bro.get(url)
        #
        #         data = bro.page_source
        #
        #         bro.close()
        #
        #         res = HtmlResponse(url=url, body=data, encoding='utf-8', request=request)
        #         return res

    # # 浏览器设置
    # def chrome_set(self):
    #     chrome_options = uc.ChromeOptions()
    #     # 浏览器不显示
    #     # chrome_options.add_argument("--headless")
    #     # --禁用扩展
    #     chrome_options.add_argument("--disable-extensions")
    #     # # --禁用弹出窗口阻止
    #     chrome_options.add_argument("--disable-popup-blocking")
    #     # --配置文件目录=默认值
    #     chrome_options.add_argument("--profile-directory=Default")
    #     # --忽略证书错误
    #     chrome_options.add_argument("--ignore-certificate-errors")
    #     # --禁用插件发现
    #     chrome_options.add_argument("--disable-plugins-discovery")
    #     # --隐姓埋名
    #     chrome_options.add_argument("--incognito")
    #     # --没有第一次运行
    #     chrome_options.add_argument('--no-first-run')
    #     # --无服务自动运行
    #     chrome_options.add_argument('--no-service-autorun')
    #     # --无默认浏览器检查
    #     chrome_options.add_argument('--no-default-browser-check')
    #     # --密码存储=基本
    #     chrome_options.add_argument('--password-store=basic')
    #     # --没有沙箱
    #     chrome_options.add_argument('--no-sandbox')
    #
    #     bro = uc.Chrome(version_main=104, use_subprocess=True, options=chrome_options)
    #     # //浏览器最大化，不覆盖任务栏(有些网页不最大化会出错)
    #     bro.maximize_window()
    #     # 网页加载超时处理
    #     bro.set_page_load_timeout(3)
    #     bro.set_script_timeout(3)
    #
    #     return bro




    # 响应时调用
    def process_response(self, request, response, spider):
        print("status-----------------" + str(response.status))
        if spider.name == "amazon":
            aa = response.xpath('//*[@class="a-last"]/text()')
            if len(aa) != 0:
                print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                fp = request_fingerprint(request, include_headers=None)
                print("指纹：" + fp)
                print(request.url)
                spider.server.srem(spider.name + ':dupefilter', fp)
                return request

        if spider.name == 'aliexpress':
            # 评论滑动验证和页面滑动验证一样，只不过页面滑动验证会返回429，而评论则返回正常200
            # 返回界面html有renderTo代表有滑动验证，重新去请求,没有则正常执行
            try:
                patter = re.compile("renderTo")
                renderTo = patter.findall(response.text)[0]
                print('速卖通滑动验证')
                return request
            except:
                print()


        if 'dataloss' in response.flags:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            fp = request_fingerprint(request, include_headers=None)
            print("指纹：" + fp)
            print(request.url)
            spider.server.srem(spider.name + ':dupefilter', fp)
            return request

        if response.status in RETRY_HTTP_CODES:
            print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC" + str(response.status))
            fp = request_fingerprint(request, include_headers=None)
            print("指纹：" + fp)
            print(request.url)
            spider.server.srem(spider.name + ':dupefilter', fp)
            return request
            # if spider.name == 'aliexpress':
            #     if response.status == 429:
                    # print("哈哈哈哈哈哈哈哈")
                    # bro = self.chrome_set()
                    # bro.get(request.url)
                    # bro.implicitly_wait(30)
                    # Chains = bro.find_element(By.XPATH, '//*[@class="nc_iconfont btn_slide"]')
                    # ActionChains(bro).drag_and_drop_by_offset(Chains, 350, 0).perform()
                    # try:
                    #     title = bro.find_element(By.XPATH, '//*[@class="product-title-text"]').text
                    # except BaseException as e:
                    #     print(bro.page_source)
                    #     bro.execute_script('window.stop()')
                    #     data = bro.page_source
                    #     print(data)
                    #     bro.close()
                    #     res = HtmlResponse(url=request.url, body=data, encoding='utf-8', request=request)
                    #     return res

        return response





    # 请求异常时调用
    def process_exception(self, request, exception, spider):
        print('异常' + str(exception))
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            # 异常则删除请求指纹
            fp = request_fingerprint(request, include_headers=None)
            print("DDDDDDDDDDDDDDDDDDDDDDDD")
            print("指纹：" + fp)
            print(request.url)
            spider.server.srem(spider.name + ':dupefilter', fp)
            return request



