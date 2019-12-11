import scrapy

class TestProxySpider(scrapy.Spider):
    name = 'TestProxySpider'

    def __init__(self):
        super(TestProxySpider, self).__init__()
        self.start_urls = ['https://www.baidu.com',
                           'https://www.baidu.com',
                           'https://www.baidu.com',
                           'https://www.baidu.com',
                           ]
    def parse(self, response):
        print("Hello")
        print(response.body)