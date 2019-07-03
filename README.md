电影数据库
========
从百度百科上搜集数万部电影和电视剧，数万名演员导演信息，可视化显示演员之间的关系。

运行平台
-------
Windows 10, python 3.7.2, MongoDB 4.0.6。(其他平台应该也能运行，未经过测试)

1.安装依赖
-------
    (在代码根目录下) pip install -r requirements.txt -i https://pypi.doubanio.com/simple

2.爬取数据
--------
    cd movie_crawl/baidu
    (在movie_crawl/baidu目录下) scrapy crawl spider

等待程序运行结束

3.启动网站
--------
    cd ../flask_movie
    (在flask_movie目录下) set FLASK_APP=app.py
    (在flask_movie目录下) flask run

4.访问网站
---------
在 http://localhost:5000 访问网站


关于Scrapy在Windows下的安装
------------------------
Scrapy依赖的Twisted在没有安装vc++开发工具的windows上使用默认是安装不成功,解决方法请参考官方文档。

所用技术
------
- 爬虫和网站都是使用Python编写。
- 爬虫使用到了Scrapy框架。
- 网站后台使用到了Flask框架。
- 网站前端使用了Bootstrap 4框架。
- 数据库使用MongoDB。
- 关系图谱使用到了relation-chart库(基于d3.js),做了一些轻微改动。


爬虫思路简介
---------
- 网站选取百度百科。
- 爬虫可以以任意一部电影或者任意一位演员为入口。
- 解析到一部电影时：
    1. 提取电影信息,存入数据库。
    2. 提取所有演员/导演链接,加入到解析队列。
- 解析到一名演员时：
    1. 提取演员信息和人物关系,存入数据库。
    2. 提取所有作品链接,加入到解析队列.
    
爬虫实现说明：
----------
- 演员链接是直接从网页提取的,因此只要词条编写者的信息正确，就能得到正确的页面。
- 导演信息是根据导演姓名手动生成的,在导演名字存在重复词条(同时导演知名度低，默认不跳转)时,
会发生爬取不到的现象。
- 网站上每部电影显示4名主演，实际上数据库里面有所有的演员列表，考虑到龙套的信息量比较低，没有在网页列出。
- 电影图片和演员图片用到了比较繁琐的分析方法，确保爬到图片，但是由于一部分电影和演员一张图片都没有，
所以无法获取图片。
- 在数据库存储上：所有电影信息存储到movies集合中,演员和导演信息存储到actors集合中,
演员和导演的区别用type字段标识出来,有不少人物会同时有演员页面和导演页面。
- 爬取演员和导演其实使用到了同一个函数，两者信息也几乎一样，导演的执导作品列表是通过查询
数据库中电影的导演信息获得的。
- 使用电影/导演/演员的名字作为其唯一标识,虽然有可能会出现重复,但是其比率应该相当低。

![screenshot1](https://github.com/xzmeng/movie_spider/blob/master/screenshot/movie1.png)

![screenshot2](https://github.com/xzmeng/movie_spider/blob/master/screenshot/movie2.png)

![screenshot3](https://github.com/xzmeng/movie_spider/blob/master/screenshot/movie3.png)

![screenshot4](https://github.com/xzmeng/movie_spider/blob/master/screenshot/movie4.png)
