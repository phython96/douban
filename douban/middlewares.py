# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware, response_status_message
from scrapy import signals
import requests
import redis
import hashlib
import time
from fake_useragent import UserAgent

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError

from scrapy.http import HtmlResponse
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError


red = redis.Redis(host = 'localhost', port = 6379, db = 1)



def get_proxy():
    while True:
        res = requests.get("http://127.0.0.1:5010/get/").json()
        proxy = res['proxy']
        nowtime = int(time.time())
        oldtime = red.get(proxy)
        if oldtime is None or nowtime - int(oldtime) >= 30:
            red.set(proxy, nowtime)
            time.sleep(0.075)
            return proxy

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))



class ProxyMiddleware(object):
    '''
    def process_request(self, request, spider):
        proxy = get_proxy()
        print("获取代理IP：", proxy)
        proxy = "https://{}/".format(proxy)
        request.meta["proxy"] = proxy
        agent = str(UserAgent().random)
        #print(agent)
        request.headers["User-Agent"] = agent
    '''
    # 动态转发
    def process_request(self, request, spider):

        #url = request.url

        ip = 'forward.xdaili.cn'
        port = "80"
        ip_port = ip + ':' + port
        timestamp = str(int(time.time()))

        orderno = "ZF201912255648Jkkwbe"
        secret = "8a53d9893862454fb9aaab575d127e35"

        string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
        proxy = "https://" + ip_port
        headers = {"Proxy-Authorization": auth, "User-Agent": str(UserAgent().random)}

        request.headers['User-Agent'] = headers['User-Agent']
        request.headers['Proxy-Authorization'] = headers['Proxy-Authorization']
        request.meta['proxy'] = proxy
        #print(request.headers)




class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class DoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
