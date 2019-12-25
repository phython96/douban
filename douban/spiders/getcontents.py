import scrapy
import json
import re
import logging
from douban.items import DoubanItem, CommmentItem

class CommentSpider(scrapy.Spider):
    name = 'CommentSpider'

    def __init__(self):
        super(CommentSpider, self).__init__()
        self.allowed_domains = ["douban.com"]

    def start_requests(self):

        movie_list = ["27668250","26832891","26834248","26389069","26947198","26899304","26387939","26926703"]
        file = open('Json/movielist2.json')
        content = file.read()
        movie_list = re.findall('\"([0-9]{8})\"',content)
        logging.info("电影列表总数: {}".format(len(movie_list)))
        for i in range(200,400):
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

        comments_count = 0
        try:
            comments_count = response.xpath("//a[re:match(@href, 'comments\?sort=new_score')]//text()").re('[0-9]+')[0]
            comments_count = int(comments_count)
        except:
            logging.info('movie id:{} 无短评'.format(movie_id))
            return
        logging.info("电影ID{}, imdb: {}, 短评数量：{}".format(movie_id, imdb_tconst, comments_count))
        if comments_count == 0:
            return
        page_num = comments_count // 20
        for i in range(min(11,page_num+1)):
            start = i * 20
            url = "https://movie.douban.com/subject/{}/comments?start={}&limit=20&sort=new_score&status=P".format(movie_id, start)
            yield scrapy.Request(url = url, callback =
                                 lambda response, movie_id = movie_id, imdb_tconst = imdb_tconst:
                                 self.parse_page(response, movie_id, imdb_tconst))

    def parse_page(self, response, movie_id, imdb_tconst):
        comments_count = len(response.xpath("//span[@class='comment-info']/a//text()").extract())
        comments_users = response.xpath("//span[@class='comment-info']/a//text()").extract()
        comments_texts = response.xpath("//span[@class='short']/text()").extract()
        comments_votes = response.xpath("//span[@class='votes']/text()").extract()
        comments_stars = response.xpath("//span[re:match(@class, 'star')]/@title").extract()
        comments_dates = response.xpath("//span[re:match(@class, 'comment-time')]/text()").re('[0-9\-]+')
        for i in range(comments_count):
            item = CommmentItem()
            item['movie_id'] = movie_id
            item['imdb_tconst'] = imdb_tconst
            try:
                item['comment_user'] = comments_users[i]
            except:
                pass
            try:
                item['comment_text'] = comments_texts[i]
            except:
                pass
            try:
                item['comment_vote'] = comments_votes[i]
            except:
                pass
            try:
                item['comment_star'] = comments_stars[i]
            except:
                pass
            try:
                item['comment_date'] = comments_dates[i]
            except:
                pass

            yield item




