import meeple
import datetime
import urllib2
from flask import request
from meeple.tools import build_search,build_game

from meeple.meeple_exceptions import GameNotFound
from sqlalchemy.exc import IntegrityError

search_q = "dominion"
bgg_results = build_search(search_q)
for result in bgg_results:
    print result
    game = build_game(result['id'])