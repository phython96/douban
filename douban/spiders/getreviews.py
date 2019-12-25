import scrapy
import logging
import json
import re
from douban.items import DoubanItem, ReviewItem
from douban.middlewares import ProxyMiddleware

import torch.multiprocessing
torch.multiprocessing.set_sharing_strategy('file_system')

class ReviewSpider(scrapy.Spider):
    name = 'ReviewSpider'

    def __init__(self):
        super(ReviewSpider, self).__init__()
        self.allowed_domains = ["douban.com"]

    def start_requests(self):

        movie_list = ["27668250","26832891","26834248","26389069","26947198","26899304","26387939","26926703"]
        file = open('Json/movielist2.json')
        content = file.read()
        movie_list = re.findall('\"([0-9]{8})\"',content)
        logging.info("电影列表总数: {}".format(len(movie_list)))
        for i in range(600,800):
            movie_id = movie_list[i]
            logging.info("电影枚举第{}个，id为:{}".format(i, movie_id))
            movie_url = "https://movie.douban.com/subject/{}/".format(movie_id)
            yield scrapy.Request(url = movie_url, callback = lambda response, movie_id = movie_id : self.parse(response, movie_id))

    def parse(self, response, movie_id):
        if str(response.body).find('window.location.href') == -1:
            logging.info("电影id{}发现重定向检测，重新申请访问".format(movie_id))
            yield scrapy.Request(url = response.url, callback = lambda response, movie_id = movie_id : self.parse(response, movie_id))
            return
        #print(response.body)
        imdb_tconst = 0
        try:
            imdb_tconst = response.xpath("//a[re:match(@href, 'imdb')]//text()").extract()[0]
        except:
            logging.info('movie id:{} 无 imdb tconst'.format(movie_id))

        reviews_count = 0
        try:
            reviews_count = response.xpath("//a[@href = 'reviews']/text()").re('[0-9]+')[0]
            reviews_count = int(reviews_count)
        except:
            logging.info('movie id:{} 无影评'.format(movie_id))
            return 
        logging.info("电影ID{}, imdb: {}, 影评数量：{}".format(movie_id, imdb_tconst, reviews_count))
        if reviews_count == 0:
            return

        page_num = reviews_count // 20
        for i in range(page_num+1):
            start = i * 20
            url = "https://movie.douban.com/subject/{}/reviews?start={}".format(movie_id, start)
            yield scrapy.Request(url = url, callback =
                                 lambda response, movie_id = movie_id, imdb_tconst = imdb_tconst:
                                 self.parse_page(response, movie_id, imdb_tconst))

    def parse_page(self, response, movie_id, imdb_tconst):
        reviews_count = len(response.xpath("//a[@class='name']/text()").extract()) ###
        reviews_users = response.xpath("//a[@class='name']/text()").extract() ###
        reviews_shorts = response.xpath("//div[@class='short-content']/text()").extract() ###
        reviews_id = response.xpath("//div[@class='main review-item']/@id").extract()

        reviews_dates = response.xpath("//span[@class='main-meta']/@content").extract() ###
        for i in range(reviews_count):
            item = ReviewItem()
            item['movie_id'] = movie_id
            item['imdb_tconst'] = imdb_tconst
            try:
                item['review_user'] = reviews_users[i]
            except:
                pass
            try:
                item['review_date'] = reviews_dates[i]
            except:
                pass
            try:
                item['review_short'] = reviews_shorts[i]
            except:
                pass
            try:
                item['review_id'] = reviews_id[i]
            except:
                pass
            try:
                item['review_short'] = reviews_shorts[i]
            except:
                pass
            '''
            try:
                url = "https://movie.douban.com/j/review/{}/full".format(reviews_id[i])
                yield scrapy.Request(url = url, callback = lambda response, item = item : self.parse_review(response, item))
            except:
                pass
            '''
            yield item

    def parse_review(self, response, item):
        js = json.loads(response.body)
        re_h = re.compile('</?\w+[^>]*>')  # 匹配HTML标签
        review = re_h.sub('',js['html'])
        item['review_text'] = review
        yield item


