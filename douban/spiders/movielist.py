import scrapy
import json
from douban.items import DoubanItem, BasicItem

class MovieListSpider(scrapy.Spider):
    name = 'MovieListSpider'

    def __init__(self):
        super(MovieListSpider, self).__init__()
        self.allowed_domains = ["douban.com"]

    def start_requests(self):
        # https://movie.douban.com/j/new_search_subjects?sort=R&tags=%E7%94%B5%E5%BD%B1&start=200&year_range=2016,2016
        start_year = '2010'
        end_year = '2018'
        for i in range(499):
            url = "https://movie.douban.com/j/new_search_subjects?sort=R&tags=%E7%94%B5%E5%BD%B1&start={}&year_range={},{}".format(i * 20,start_year,end_year)
            yield scrapy.Request(url = url, priority = 10)

    def parse(self, response):
        js = json.loads(response.body)
        print(js)
        for line in js['data']:
            print(line)
            item = BasicItem()
            item['directors'] = line['directors']
            item['rate'] = line['rate']
            item['cover_x'] = line['cover_x']
            item['star'] = line['star']
            item['title'] = line['title']
            item['url'] = line['url']
            item['casts'] = line['casts']
            item['cover'] = line['cover']
            item['id'] = line['id']
            item['cover_y'] = line['cover_y']
            yield item
