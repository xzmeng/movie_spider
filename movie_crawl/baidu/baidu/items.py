# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 演员/导演
class ActorItem(scrapy.Item):
    # 演员/导演
    type = scrapy.Field()
    name = scrapy.Field()
    info = scrapy.Field()
    relations = scrapy.Field()
    baike_url = scrapy.Field()
    image_url = scrapy.Field()
    latest_product_year = scrapy.Field()


# 电影
class MovieItem(scrapy.Item):
    type = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()
    director_list = scrapy.Field()
    major_actor_list = scrapy.Field()
    actor_list = scrapy.Field()
    baike_url = scrapy.Field()
    image_url = scrapy.Field()
    year = scrapy.Field()
