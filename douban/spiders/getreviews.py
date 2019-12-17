import scrapy
import json
import re
from douban.items import DoubanItem, ReviewItem

class ReviewSpider(scrapy.Spider):
    name = 'ReviewSpider'

    def __init__(self):
        super(ReviewSpider, self).__init__()
        self.allowed_domains = ["douban.com"]

    def start_requests(self):

        movie_list = ["27668250","26832891","26834248","26389069","26947198","26899304","26387939","26926703"]
        file = open('Json/movielist.json')
        content = file.read()
        movie_list = re.findall('\"([0-9]{8})\"',content)
        print("tot count: {}", len(movie_list))
        for movie_id in movie_list:
            movie_url = "https://movie.douban.com/subject/{}/".format(movie_id)
            yield scrapy.Request(url = movie_url, callback = lambda response, movie_id = movie_id : self.parse(response, movie_id))

    def parse(self, response, movie_id):
        #print(response.body)
        imdb_tconst = 0
        try:
            imdb_tconst = response.xpath("//a[re:match(@href, 'imdb')]//text()").extract()[0]
        except:
            print('movie id:{} 无 imdb tconst'.format(movie_id))

        reviews_count = 0
        try:
            reviews_count = response.xpath("//a[@href = 'reviews']/text()").re('[0-9]+')[0]
            reviews_count = int(reviews_count)
        except:
            print('movie id:{} 无 短评'.format(movie_id))

        page_num = reviews_count // 20
        for i in range(page_num // 2):
            start = i * 20
            url = "https://movie.douban.com/subject/{}/reviews?start={}".format(movie_id, start)
            yield scrapy.Request(url = url, callback =
                                 lambda response, movie_id = movie_id, imdb_tconst = imdb_tconst:
                                 self.parse_page(response, movie_id, imdb_tconst))

    def parse_page(self, response, movie_id, imdb_tconst):
        reviews_count = len(response.xpath("//a[@class='name']/text()").extract()) ###
        reviews_users = response.xpath("//a[@class='name']/text()").extract() ###
        reviews_texts = response.xpath("//span[@class='short']/text()").extract()
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
                item['review_text'] = reviews_texts[i]
            except:
                pass
            try:
                item['review_date'] = reviews_dates[i]
            except:
                pass

            yield item




