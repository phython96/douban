# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    json = scrapy.Field()

class BasicItem(scrapy.Item):
    directors = scrapy.Field()
    rate = scrapy.Field()
    cover_x = scrapy.Field()
    star = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    casts = scrapy.Field()
    cover = scrapy.Field()
    id = scrapy.Field()
    cover_y = scrapy.Field()

class CommmentItem(scrapy.Item):
    movie_id = scrapy.Field()
    imdb_tconst = scrapy.Field()
    comment_user = scrapy.Field()
    comment_text = scrapy.Field()
    comment_vote = scrapy.Field()
    comment_star = scrapy.Field()
    comment_date = scrapy.Field()