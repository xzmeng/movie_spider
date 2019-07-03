# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from urllib.parse import urljoin

import scrapy
from scrapy.cmdline import execute
from baidu.items import MovieItem, ActorItem


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['baidu.com']

    # 由于部分词条的编写不规范,导致一部分演员的url既有标准url(带唯一标识符)又有不标准的(只有名字)
    # 使用名字集合来过滤演员/导演/电影的名字
    # (同时放弃了所有重名)
    actor_set = set()
    director_set = set()
    movie_set = set()

    def start_requests(self):
        # 入口可以选择任意一部电影或者任意一个演员
        # 六度空间...
        url = 'https://baike.baidu.com/item/赵丽颖'
        yield scrapy.Request(url, self.parse_actor)

    def parse(self, response):
        print(response.text)

    def parse_actor(self, response):
        actor_item = ActorItem()
        # 演员图片
        image_url = response.css('.summary-pic img::attr(src)').get()
        if not image_url:
            image_url = response.css('.poster-absolute style').re_first(
                r"background-image: url\('(.*?.jpg)'\);"
            )
        if not image_url:
            image_url = response.css('.lemma-picture img::attr(src)').get()
        if not image_url:
            image_url = response.css('.album-wrap img::attr(src)').get()
        if not image_url:
            print('no image', actor_item.get('baike_url'))
        actor_item['image_url'] = image_url
        # 该演员演过的所有电影和电视剧url
        try:
            actor_item['latest_product_year'] = int(response.css('.starWorksList .title + b::text').get()[:4])
        except:
            actor_item['latest_product_year'] = 0
        movie_urls = response.css(
            '.starWorksList .title a::attr(href)').getall()


        # # 如果一部都没有，那么视为不是演员
        # if not movie_urls:
        #     return
        # 太多龙套的页面还真一部没有..

        # 解析所有电影
        for movie_url in movie_urls:
            yield response.follow(movie_url, self.parse_movie)

        type = response.meta.get('type')
        if type:
            actor_item['type'] = type
        else:
            actor_item['type'] = 'actor'
        actor_item['name'] = response.css('h1::text').get()
        if actor_item['type'] == 'actor':
            if actor_item['name'] in self.actor_set:
                return
            else:
                self.actor_set.add(actor_item['name'])
        info = {}
        item_names = response.css('.basicInfo-block dt')
        item_values = response.css('.basicInfo-block dd')
        items = zip(item_names, item_values)
        for item_name, item_value in items:
            name = item_name.css('::text').get()
            value = item_value.css('::text').get()
            name = name.replace('\xa0', '').strip()
            value = value.strip()
            if not value:
                value_list = item_value.css('a::text').getall()
                value = '、'.join(value_list)
            info[name] = value
            info[name] = value
        actor_item['info'] = info
        actor_item['baike_url'] = response.url



        # 解析演员关系
        relation_divs = response.css('#slider_relations li .name')
        relations = []
        for div in relation_divs:
            name = div.css('::attr(title)').get()
            relationship = div.css('::text').get()
            relations.append((name, relationship))
        actor_item['relations'] = relations

        # 解析有关系的演员
        for url in response.css('#slider_relations li a::attr(href)').getall():
            yield response.follow(url, self.parse_actor)

        yield actor_item

    def parse_movie(self, response):
        movie_item = MovieItem()
        movie_item['title'] = response.css('h1::text').get()
        if movie_item['title'] in self.movie_set:
            return
        else:
            self.movie_set.add(movie_item['title'])
        if not movie_item.get('title'):
            return
        info = {}
        item_names = response.css('.basicInfo-block dt')
        item_values = response.css('.basicInfo-block dd')
        items = zip(item_names, item_values)
        for item_name, item_value in items:
            name = item_name.css('::text').get()
            value = item_value.css('::text').get()
            name = name.replace('\xa0', '').strip()
            value = value.strip()
            if not value:
                value_list = item_value.css('a::text').getall()
                value = '、'.join(value_list)
            info[name] = value
        movie_item['info'] = info
        movie_item['baike_url'] = response.url

        # 电影图片
        # 海报/随便什么图片

        # 背景的那个大图片
        image_url = response.css('.poster-absolute style').re_first(
            r"background-image: url\('(.*?.jpg)'\);"
        )
        # 如果没有的话..右侧可能有一个(电视剧)..
        if not image_url:
            image_url = response.css('.summary-pic img::attr(src)').get()
        movie_item['image_url'] = image_url
        # 如果还没有的话..lemma-picture这个类很多词条都有图片
        if not image_url:
            image_url = response.css('.lemma-picture img::attr(src)').get()
        # 如果还没有的话..随便找一张相册封面
        if not image_url:
            image_url = response.css('.album-wrap img::attr(src)').get()
        # 如果还没有的话..
        if not image_url:
            print('no movie image:', movie_item.get('baike_url'))
        # 电影的主要演员
        major_actor_list_movie = response.css(
            '.lemmaWgt-majorActors_viewport dd a::text').getall()
        # 电视剧的主要演员
        major_actor_list_tv = response.css(
            '.f_baseInfo_wrap dd p::text').getall()

        # 判断是电影还是电视剧
        if major_actor_list_movie:
            major_actor_list = major_actor_list_movie
            # 顺手把主要演员的链接提取出来
            major_actor_urls = response.css(
                '.lemmaWgt-majorActors_viewport dd a::attr(href)').getall()
            movie_item['type'] = 'movie'
        elif major_actor_list_tv:
            major_actor_list = major_actor_list_tv
            # 顺手把主要演员的链接提取出来
            major_actor_urls = response.css(
                '.f_baseInfo_wrap dd a::attr(href)').getall()
            movie_item['type'] = 'tv'
        # 啥都不是(写词条的人太不负责，年代久远，过于小众)： 直接丢弃
        else:
            return

        movie_item['major_actor_list'] = [
            actor for actor in major_actor_list if actor.strip()
        ]

        # 获取所有演员列表
        dts = response.css(
            '#marqueeViewport_actor .listItem dt')

        movie_item['actor_list'] = [dt.css('a::text').get() for dt in dts if dt.css('a::text')]
        yield movie_item

        # 解析每个主要演员
        for url in major_actor_urls:
            yield response.follow(url, self.parse_actor)

        # 解析所有演员(主要是龙套),提取出baike链接
        actor_url_list = response.css(
            '#marqueeViewport_actor .listItem > a::attr(href)').getall()
        for url in actor_url_list:
            yield response.follow(url, self.parse_actor)

        # 解析导演
        director_str = movie_item.get('info').get('导演')
        if not director_str:
            return
        directors = director_str.split('、')
        base_url = 'https://baike.baidu.com/item/'
        for director in directors:
            if director in self.director_set:
                continue
            else:
                self.director_set.add(director)
            url = urljoin(base_url, director)
            meta = {'type': 'director'}
            yield response.follow(url, self.parse_actor, meta=meta, dont_filter=True)


if __name__ == '__main__':
    cmd = ['scrapy', 'crawl', 'spider']
    execute(cmd)
