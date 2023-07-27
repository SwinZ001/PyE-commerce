# Scrapy settings for yamaxun project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'yamaxun'

SPIDER_MODULES = ['yamaxun.spiders']
NEWSPIDER_MODULE = 'yamaxun.spiders'

DOWNLOAD_FAIL_ON_DATALOSS = False
# LOG_LEVEL = 'ERROR'
# LOG_FILE = "amazonLog.log"
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
# redis配置
# 去重容器类配置 作用：redis的set集合来存储请求的指纹数据，从而实现去重的持久化
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 使用scrapy-redis的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
SCHEDULER_PERSIST = True

# 链接redis数据库
# REDIS_HOST = "127.0.0.1"
# REDIS_PORT = 6379

# redis://127.0.0.1:6379/1,后面再加/1表示用第几个数据库
REDIS_URL = 'redis://127.0.0.1:6379'

# # 远程连接本地redis数据库
# REDIS_URL = 'redis://192.168.1.101:6379'



# 下载中间件
ITEM_PIPELINES = {
    # 'scrapy_redis.pipelines.RedisPipeline': 300,
    'yamaxun.pipelines.YamaxunPipeline': 300
}

# 注册随机请求头中间件
DOWNLOADER_MIDDLEWARES = {
    'yamaxun.middlewares.Middlewares': 543,
    # 'yamaxun.middlewares.YamaxunDownloaderMiddleware': 543,
}

# Obey robots.txt rules(遵循机器人文本)
ROBOTSTXT_OBEY = False


# 网络请求报错的是哪个状态码就填哪个状态码,如:[503]，意思是忽略这个错误请求继续进行下一个请求
HTTPERROR_ALLOWED_CODES = [422]
# 加这个亚马逊反爬成功
DOWNLOADER_CLIENT_TLS_CIPHERS = "DEFAULT:!DH"
# 异常状态码
RETRY_HTTP_CODES = [502, 503, 504, 522, 524, 408, 401, 403, 429, 301, 302]
# 重试次数
RETRY_TIMES = 0
#下载延迟
# DOWNLOAD_DELAY = 3.5
# # 编码
# FEED_EXPORT_ENCODING = 'utf-8'


# 请求头
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a"
]
PROXY_LIST = ['60.185.200.25:4226']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# COOKIES_ENABLED设置
# 只是设置cookies，而不是整个请求头headers
# 在中间件设置：
# COOKIES_ENABLED = False时请求头为：（请求头都一样）
# (会使用中间件请求头自定义的Cookie，没写Cookie则没有Cookie）
# （需要设置Cookie）
# （有设置headers就按照设置的headers，没有则自己生成headers，不过会503很久）
# COOKIES_ENABLED =True时请求头为：（请求头都一样）
# (会自己生成Cookie，不管中间件有没有Cookie，都使用自己生成Cookie）
# （不需要设置Cookie）
# （有设置headers就按照设置的headers，没有则自己生成headers，不过会503很久）

# 在spider设置(需要传递，不然下一个函数不可用，传递的过程中cookies不变)：
# COOKIES_ENABLED = False： （有设置headers就按照设置的headers，没有则自己生成headers，不过会503很久）
# （不设置cookies不会生成cookies）
# （只能在header中写才会生成cookies）
# (不可使用cookies=cookies方式，这样也不会生成cookies），
# （不可用在post请求的scrapy.FormRequest中，scrapy.FormRequest只支持cookies=cookies方式）
# COOKIES_ENABLED =True：   （不设置cookies会随机生成cookies）
# （在header中设置cookies，会有cookies，但不是自己设置的cookies，是随机生成）
# （可使用cookies=cookies方式，使用该方式，才会是自己设置的cookie）
# （可用在post请求的scrapy.FormRequest中，scrapy.FormRequest只支持cookies=cookies方式）
# （有设置headers就按照设置的headers，没有则自己生成headers，不过会503很久）

# 多个url时使用cookiejar来保持会话（session），保证每个url独立运行，不会导致数据混乱（可以不设置cookies）
# （可以不设置这部分 cookie_dict）
# cookie_dict = ['session-id=134-0000000-0000001; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=131-6832861-0372514; ',
         #       'session-id=134-0000000-0000002; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=131-6832861-0372514; ']
# urls = ['https://www.amazon.com/-/zh/dp/B08V4Z4VRY?th=1&psc=1','https://www.amazon.com/-/zh/dp/B09GJYM3R8?th=1&psc=1']
# for i in range(len(urls)):
        #     url = urls[i]
        #     temp = cookie_dict[i]（可以不设置这部分）
        #     cookies = {data.split("=")[0]: data.split("=")[-1] for data in temp.split('; ')}（可以不设置这部分）
        #     yield scrapy.Request(
        #         url=url,
        #         cookies=cookies,（可以不设置这部分）
        #         meta={'item': copy.deepcopy(item),'cookies': copy.deepcopy(cookies)（可以不设置这部分）,'cookiejar': i (标识可以是url,或者循环底标）},
        #         callback=self.parse2,
        #         dont_filter=True,
        #     )
COOKIES_ENABLED = True
# 显示cookies
# COOKIES_DEBUG = True

# 自定义headers
# DEFAULT_REQUEST_HEADERS = {}

# # 运行多个py的设置文件
# COMMANDS_MODULE = "yamaxun.commands"
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!













# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 0

# Disable cookies (enabled by default)


# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:










# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'yamaxun.middlewares.YamaxunSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html



# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
# 延迟
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


