
import pymongo

client = pymongo.MongoClient()
db = client.movie_x
movies = db.movies.find({})
for movie in movies:
    year = movie.get('year', 0)
    actors = db.actors.find({'name': {'$in': movie.get('major_actor_list')}})
    for actor in actors:
        if actor.get('year', -1) < year:
            db.actors.update_one({
                '_id': actor['_id']
            }, {
                '$set': {
                    'year': year
                }
            }, upsert=False)