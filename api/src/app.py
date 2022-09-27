"""
app.py

Aru Bhoop. Algorithms by Lijie Guo.
Clemson University. 7.27.2021.

Rewritten by Shahan (Mehtab Iqbal)
Clemson University.

Server for running the recommender algorithms. See
`models.py` for information about the input and
outputs.
"""

import os
from flask import Flask, Response, abort, json, render_template, request
from flask_cors import CORS, cross_origin

from compute.community import get_discrete_continuous_coupled
from compute.rssa import RSSACompute
from db_connectors.db import db, initialize_db
from db_connectors.movie_db import MovieDB
from db_connectors.survey_db import InvalidSurveyException, SurveyDB
from models import Rating
from utils.json_utils import RssaJsonEncoder
from operator import attrgetter

app = Flask(__name__)
CORS(app)
app.json_encoder = RssaJsonEncoder
survey_db = None
movie_db = None

with open('config.json') as f:
    settings = json.load(f)
MOVIE_DB = 'sqlite:///' + os.path.abspath(settings['movidb'])
SURVEY_DB = 'sqlite:///' + os.path.abspath(settings['userdb'])
SURVEY_ID = settings['survey_id']
SQLALCHEMY_BINDS = {
    'movies': MOVIE_DB
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SURVEY_DB
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'encoding': 'utf-8'}

survey_db = SurveyDB(initialize_db(app))
movie_db = MovieDB(db)

rssa = RSSACompute()


@app.route('/')
def show_readme():
    return render_template('README.html')


@app.route('/disc_cont_coupled', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_discrete_cont_coupled():
    data = get_discrete_continuous_coupled()

    dictdata = {movie['item_id']: movie for movie in data}
    moviedata = movie_db.get_movie_from_list(movieids=list(dictdata.keys()))
    for movie in moviedata:
        dictdata[movie['movie_id']]['poster'] = movie['poster']
        dictdata[movie['movie_id']]['title'] = movie['title']
        dictdata[movie['movie_id']]['description'] = movie['description']

    data = list(dictdata.values())
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/movies', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_movies_two():
    lim = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    movies = movie_db.get_movies(lim, page)
    print(movies)

    return Response(json.dumps(movies), mimetype='application/json')


@app.route('/movies', methods=['POST'])
@cross_origin(supports_credentials=True)
def get_movies_for_user():
    req = json.loads(request.data)
    try:
        userid = req['userid']
        surveypageid = req['pageid']
        lim = req['limit']
        gallerypage = req['page']
        moviesubset = 'rssa'
        if 'subset' in req:
            moviesubset = req['subset']
        seen = survey_db.movies_seen(userid)
        movies: list
        loadedpages = seen.keys()
        if 0 in loadedpages or gallerypage not in loadedpages:
            print('Sending request to movie database.')
            seenflat = []
            for seenpage in seen.values():
                seenflat.extend(seenpage)
            movies = movie_db.get_movies(
                lim, gallerypage, seenflat, moviesubset)
            survey_db.update_movies_seen(movies[:lim], userid, surveypageid,
                                        gallerypage)
            survey_db.update_movies_seen(movies[lim:], userid, surveypageid,
                                        gallerypage+1)

        else:
            print('This page was already generated, don\'t need to rebuild.')
            movies = movie_db.get_movie_from_list(
                [seenitem.item_id for seenitem in seen[gallerypage]])
    except KeyError:
        print(req)
        abort(400)

    return Response(json.dumps(movies), mimetype='application/json')

@app.route('/recommendations', methods=['POST'])
@cross_origin(supports_credentials=True)
def predict_preferences():
    req = json.loads(request.data)

    try:
        userid = req['userid']
        ratings = req['ratings']
        ratings = [Rating(**rating) for rating in ratings]

        item_count = req['count']
        moviesubset = 'rssa'
        if 'subset' in req:
            moviesubset = req['subset']

        condition = survey_db.get_condition_for_user(userid)
        left, right = rssa.get_condition_prediction(ratings, userid,
                                                    condition.id-1, item_count)
        leftitems = movie_db.get_movie_from_list(
            movieids=left, api=moviesubset)
        rightitems = movie_db.get_movie_from_list(
            movieids=right, api=moviesubset)


        prediction = {
            # topN
            'left': {
                'tag': 'control',
                'label': 'Movies You May Like',
                'byline': 'Among the movies in your system, we predict that \
                    you will like these 11 movies the best. We have also included a few other recommendation that you may try.',
                'items': leftitems
            },
            # Condition specific messaging
            'right': {
                'tag': condition.cond_tag,
                'label': condition.cond_act,
                'byline': condition.cond_exp,
                'items': rightitems
            }
        }
    except KeyError:
        abort(400)

    return dict(recommendations=prediction)


# FIXME to get condition specific recommendations
@app.route('/recommendation', methods=['POST'])
@cross_origin(supports_credentials=True)
def predict_preference():
    req = json.loads(request.data)

    try:
        condition = req['condition']
        ratings = req['ratings']
        ratings = [Rating(**rating) for rating in ratings]

        item_count = req['count']
        moviesubset = 'rssa'
        if 'subset' in req:
            moviesubset = req['subset']

        left, right = rssa.get_condition_prediction(ratings, 0,
                                                    condition, item_count)
        leftitems = movie_db.get_movie_from_list(
            movieids=left, api=moviesubset)
        rightitems = movie_db.get_movie_from_list(
            movieids=right, api=moviesubset)

        prediction = {
            # topN
            'left': {
                'tag': 'control',
                'label': 'Movies You May Like',
                'byline': 'Among the movies in your system, we predict that \
                    you will like these 7 movies the best.',
                'items': leftitems
            },
            # Condition specific messaging
            'right': {
                'tag': condition.cond_tag,
                'label': condition.cond_act,
                'byline': condition.cond_exp,
                'items': rightitems
            }
        }
    except KeyError:
        abort(400)

    return dict(recommendations=prediction)


@app.route('/ersrecommendations', methods=['POST'])
@cross_origin(supports_credentials=True)
def predict_emotional():
    req = json.loads(request.data)

    try:
        userid = req['userid']
        ratings = req['ratings']
        ratings = [Rating(**rating) for rating in ratings]

        item_count = req['count']
        moviesubset = 'ers'
        if 'subset' in req:
            moviesubset = req['subset']

        left, right = rssa.get_condition_prediction(ratings, userid,
                                                    0, item_count)
        items = movie_db.get_movie_from_list(
            movieids=left+right, api=moviesubset)

    except KeyError:
        abort(400)

    return dict(recommendations=items)


""" TODO
    Wrap this into a restful User resource
    POST -> create a new user at the beginning of the survey
    PUT  -> Update entries as a user progresses through the survey
"""


@app.route('/new_user', methods=['POST'])
@cross_origin()
def create_new_user():

    req = json.loads(request.data)

    try:
        welcome_time = req['welcomeTime']
        consent_start_time = req['consentStartTime']
        consent_end_time = req['consentEndTime']
        user_type = req['userType']
        platform_info = req['platformInfo']
        user_id = survey_db.create_user(welcome_time, consent_start_time,
                                        consent_end_time, user_type, platform_info)
    except KeyError:
        abort(400)

    return dict({'Success': True, 'user_id': str(user_id)})


@app.route('/add_survey_response', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_survey():

    req = json.loads(request.data)

    try:
        page_id = req['pageid']
        user_id = req['userid']
        page_starttime = req['starttime']
        page_endtime = req['endtime']

        response_params = req['response']

        user_id = survey_db.add_survey_reponse(user_id=user_id,
                                            survey_pageid=page_id, starttime=page_starttime,
                                            endtime=page_endtime, response_params=response_params)
    except KeyError as e:
        print(e)
        abort(400)

    return dict({'Success': True, 'user_id': str(user_id)})



if __name__ == '__main__':
    app.run(port=settings['port'],
            debug=settings['debug'])
