from urllib.parse import quote

from flask import Flask, render_template, request, abort, flash, redirect, url_for
from flask_paginate import Pagination, get_parameter, get_page_parameter
from utils import hot_movies
import pymongo

client = pymongo.MongoClient()
db = client.movie_fx

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('movie_list', category='hot'))


@app.route('/movie_list/<string:category>')
def movie_list(category):
    # 获取类别，生成mongo查询语句
    if category == 'all':
        query = {}
        cat = '全部影视'
    elif category == 'hot':
        query = {'title': {'$in': hot_movies}}
        cat = '热门电影'
    else:
        query = {'info.类型': {'$regex': '.*%s.*' % category}}
        cat = category

    page = request.args.get(get_parameter(), type=int, default=1)
    # 每页显示几个
    per_page = 20
    start = (page - 1) * per_page
    end = page * per_page

    # 获取作品列表
    movies = db.movies.find(query).sort([('year', -1)])[start:end]
    pagination = Pagination(
        css_framework='bootstrap4',
        page=page,
        total=db.movies.count_documents(query),
        per_page=per_page,
        record_name='movies',
        alignment='center',
        inner_window=6,
        outer_window=3,
    )
    return render_template('movie_list.html',
                           movies=movies,
                           pagination=pagination,
                           category=cat)


@app.route('/movie_detail/<string:title>')
def movie_detail(title):
    movie = db.movies.find_one({'title': title})
    major_actor_list = movie.get('major_actor_list')
    actors = []
    for name in major_actor_list:
        actor = db.actors.find_one({'name': name})
        if actor:
            actors.append(actor)
    director_name = None
    try:
        director_name = movie.get('info').get('导演')
    except Exception as e:
        print(e)
    director = None
    if director_name:
        director = db.actors.find_one({'name': director_name, 'type': 'director'})
    if not director:
        director = db.actors.find_one({'name': director_name, 'type': 'actor'})
    return render_template('movie_detail.html',
                           movie=movie,
                           actors=actors,
                           director=director)


@app.route('/actor_list/<string:category>')
def actor_list(category):
    if category == 'actor':
        cat = '演员大全'
        query = {'type': 'actor'}
    elif category == 'director':
        cat = '导演大全'
        # 注意: 由于scrapy地去重机制,相当多的导演只有演员页或者导演页
        # 此错误已经修复,暂时未经测试
        query = {'type': 'director'}
    else:
        abort(404)
    page = request.args.get(get_parameter(), type=int, default=1)
    # 每页显示几个
    per_page = 20
    start = (page - 1) * per_page
    end = page * per_page

    # 获取演员列表
    actors = db.actors.find(query).sort([('latest_product_year', -1)])[start:end]
    pagination = Pagination(
        css_framework='bootstrap4',
        page=page,
        total=db.actors.count_documents(query),
        per_page=per_page,
        record_name='actors')
    return render_template('actor_list.html',
                           actors=actors,
                           pagination=pagination,
                           category=cat)


@app.route('/actor_detail/<string:name>')
def actor_detail(name):
    actor = db.actors.find_one({'name': name, 'type': 'actor'})
    if not actor:
        msg = '数据库中没有演员"{}"的信息!'.format(name)
        flash(msg)
        return redirect(request.referrer)
    # 获取人物关系
    relations = actor.get('relations')
    new_relations = []
    for relation in relations:
        person = db.actors.find_one({'name': relation[0]})
        if not person:
            continue
        new_relation = (person, relation[1])
        new_relations.append(new_relation)
    # 获取当前作品页码
    page = request.args.get(get_page_parameter(), type=int, default=1)

    # 获取作品列表

    # 每页显示几个
    per_page = 20
    start = (page - 1) * per_page
    end = page * per_page
    movies = db.movies.find({'actor_list': name})[start:end]
    pagination = Pagination(
        css_framework='bootstrap4',
        page=page,
        total=db.movies.count_documents({'actor_list': name}),
        per_page=per_page,
        record_name='movies',
        anchor='movies',
    )
    show_movie = False
    referer_url = request.referrer
    if referer_url:
        referer_name = referer_url.split('/')[-1].split('?')[0]
        request_name = request.url.split('/')[-1].split('?')[0]
        if referer_name == quote(request_name):
            show_movie = True

    return render_template('actor_detail.html',
                           actor=actor,
                           relations=new_relations,
                           movies=movies,
                           pagination=pagination,
                           show_movie=show_movie)


@app.route('/director_detail/<string:name>')
def director_detail(name):
    actor = db.actors.find_one({'name': name, 'type': 'director'})
    if not actor:
        msg = '数据库中没有导演"{}"的信息!'.format(name)
        flash(msg)
        return redirect(request.referrer)
    # 获取人物关系
    relations = actor.get('relations')
    new_relations = []
    for relation in relations:
        person = db.actors.find_one({'name': relation[0]})
        if not person:
            continue
        new_relation = (person, relation[1])
        new_relations.append(new_relation)
    # 获取当前作品页码
    page = request.args.get(get_parameter(), type=int, default=1)
    # 获取作品列表

    # 每页显示几个
    per_page = 20
    start = (page - 1) * per_page
    end = page * per_page
    query = {'info.导演': {'$regex': '.*%s.*' % name}}
    movies = db.movies.find(query)[start:end]
    pagination = Pagination(
        css_framework='bootstrap4',
        page=page,
        total=db.movies.count_documents(query),
        per_page=per_page,
        record_name='movies')

    show_movie = False
    referer_url = request.referrer
    if referer_url:
        referer_name = referer_url.split('/')[-1].split('?')[0]
        request_name = request.url.split('/')[-1].split('?')[0]
        if referer_name == quote(request_name):
            show_movie = True

    return render_template('actor_detail.html',
                           actor=actor,
                           relations=new_relations,
                           movies=movies,
                           pagination=pagination,
                           show_movie=show_movie)


@app.route('/search')
def search():
    type = request.args.get('type')
    category = request.args.get('category')
    search_text = request.args.get('search_text')
    if type == 'movie':
        if category and category != '全部':
            query = {'info.类型': {'$regex': '.*%s.*' % category},
                     'title': {'$regex': '.*%s.*' % search_text.strip()}}
            page = request.args.get(get_parameter(), type=int, default=1)
            cat = '在类型"{}"中搜索电影"{}"的结果'.format(category, search_text)
        else:
            query = {'title': {'$regex': '.*%s.*' % search_text.strip()}}
            page = request.args.get(get_parameter(), type=int, default=1)
            cat = '搜索电影"%s"的结果' % search_text
        # 每页显示几个
        per_page = 20
        start = (page - 1) * per_page
        end = page * per_page

        # 获取作品列表
        movies = db.movies.find(query)[start:end]
        pagination = Pagination(
            css_framework='bootstrap4',
            page=page,
            total=db.movies.count_documents(query),
            per_page=per_page,
            record_name='movies')
        return render_template('movie_list.html',
                               movies=movies,
                               pagination=pagination,
                               category=cat)
    elif type == 'actor':
        query = {'name': {'$regex': '.*%s.*' % search_text.strip()}, 'type': 'actor'}
        page = request.args.get(get_parameter(), type=int, default=1)
        cat = '搜索演员"%s"的结果' % search_text
        # 每页显示几个
        per_page = 20
        start = (page - 1) * per_page
        end = page * per_page

        # 获取作品列表
        actors = db.actors.find(query)[start:end]
        pagination = Pagination(
            css_framework='bootstrap4',
            page=page,
            total=db.actors.count_documents(query),
            per_page=per_page,
            record_name='actors')
        return render_template('actor_list.html',
                               actors=actors,
                               pagination=pagination,
                               category=cat)
    elif type == 'director':
        query = {'name': {'$regex': '.*%s.*' % search_text.strip()}, 'type': 'director'}
        page = request.args.get(get_parameter(), type=int, default=1)
        cat = '搜索导演"%s"的结果' % search_text
        # 每页显示几个
        per_page = 20
        start = (page - 1) * per_page
        end = page * per_page

        # 获取作品列表
        actors = db.actors.find(query)[start:end]
        # 有一些的导演地类型被错误地爬为'actor'，用下面地方法当作workaround
        # 此错误已经修复,但未经过测试,测试完应把下面的三行删除！
        # if not actors.count():
        #     query = {'name': {'$regex': '.*%s.*' % search_text.strip()}, 'type': 'actor'}
        #     actors = db.actors.find(query)[start:end]

        pagination = Pagination(
            css_framework='bootstrap4',
            page=page,
            total=db.actors.count_documents(query),
            per_page=per_page,
            record_name='actors')
        return render_template('actor_list.html',
                               actors=actors,
                               pagination=pagination,
                               category=cat,
                               type=type)


@app.errorhandler(404)
def error_404(e):
    return render_template('error.html',
                           msg='404 Not Found')


@app.errorhandler(500)
def error_404(e):
    return render_template('error.html',
                           msg='500 Internal')


if __name__ == '__main__':
    app.run()
