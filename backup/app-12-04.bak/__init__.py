#   This is for Develop


import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from .momentjs import momentjs
# from config import basedir

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY']='what-the-hell-is-going-on'
app.config['OPENID_PROVIDERS']=[
	{'name': 'Yahoo', 'url': 'https://me.yahoo.com/'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/'}]
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dev_local:411track1_dev_local@localhost/microblogdb'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1792280577714988',
        'secret': '4083791c56b72f036ba60f8720dafc9f'
    },
    'twitter': {
        'id': 'O2Gak7Ve6AgzXzUvNAriOMuM1',
        'secret': '0sITuXzqK6PIeptt2tyxxzsVb2OmBSeA2GZJAFWqROERUqGVpy'
    }
}
app.config['POSTS_PER_PAGE'] = 10 

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

# momentjs config
app.jinja_env.globals['momentjs'] = momentjs

# Full text search config
app.config['WHOOSH_BASE'] = os.path.join(basedir, 'search.db')
app.config['MAX_SEARCH_RESULTS'] = 50

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))


#if not app.debug:
#    import logging
#    from logging import FileHandler
#    file_handler = FileHandler("tmp/movien.log", 'a')
#    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#    app.logger.setLevel(logging.INFO)
#    file_handler.setLevel(logging.INFO)
#    app.logger.addHandler(file_handler)
#    app.logger.info('movien startup')

from app import views, models

