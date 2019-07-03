# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import DropItem

from .items import ActorItem, MovieItem

class BaiduPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):

    def __init__(self):
        pass

    def open_spider(self, spider):
        self.client = pymongo.MongoClient()
        self.db = self.client.movie_fx

    def close_spider(self, spider):
        movies = self.db.movies.find({})
        for movie in movies:
            pass


        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, ActorItem):
            self.db.actors.insert_one(dict(item))
            return item
        elif isinstance(item, MovieItem):
            try:
                if item.get('info'):
                    if item['info'].get('首播时间'):
                        item['year'] = int(item['info'].get('首播时间')[:4])
                    elif item['info'].get('上映时间'):
                        item['year'] = int(item['info'].get('上映时间')[:4])
                    elif item['info'].get('出品时间'):
                        item['year'] = int(item['info'].get('出品时间')[:4])
            except:
                item['year'] = 0
            self.db.movies.insert_one(dict(item))
            return item
        else:
            raise DropItem('Item type: {} unknown!'.format(type(item)))