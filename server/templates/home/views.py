from flask import render_template, request, jsonify, Blueprint
import sqlite3 as sql
from pymemcache.client import base

home_blueprint = Blueprint('home', __name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@home_blueprint.route('/')
@home_blueprint.route('/home')
def index():
    return render_template("index.html")


@home_blueprint.route('/get_teams', methods=['GET'])
def get_teams():
    con = sql.connect('ranking.db')
    con.row_factory = dict_factory

    cur = con.cursor()
    cur.execute("select teams.id as id, teams.name as name, beginner_score.score as bscore, middle_score.time as mtime \
        from teams \
        join beginner_score on beginner_score.id = teams.id \
        join middle_score on middle_score.id = teams.id")

    teams = cur.fetchall()

    return jsonify(teams)


@home_blueprint.route('/start_recording', methods=['POST'])
def start_recording():
    if request.method == 'POST':
        req = request.json
        print("Start recording {}".format(req['current_team']))

        cache = base.Client(('localhost', 11211))
        cache.set('current_team', req['current_team'])
        cache.set('is_watching', 1)

        return jsonify(team=cache.get('current_team').decode("utf-8"))


@home_blueprint.route('/stop_recording', methods=['POST'])
def stop_recording():
    if request.method == 'POST':
        req = request.json
        print("Stop recording")

        cache = base.Client(('localhost', 11211))
        cache.set('is_watching', 0)

        return jsonify(is_watching=cache.get('is_watching').decode("utf-8"))
