# import pymongo
#
# client = pymongo.MongoClient()
# type_set = set()
#
# movies = client.movie3.movies.find({'info.类型': {'$regex': '.*爱情.*'}})
#
# for movie in movies:
#     print(movie)
import csv

# 打印出豆瓣top250电影
titles = []
with open('douban250.csv', encoding='utf8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        titles.append(row.get('name').split()[0])
print(titles)

# 这个文件是写代码时候测试代码片段使用的，可以忽略
