# This config file is used in production mode, which, debug ususlly be false
#
# Use app.config.from_object() to call this config file

# Start flask debug mode
# DEBUG = False 

# Config Flask-Bcrypt extension
# BCRYPT_LEVEL = 13

# Enable Flask-WTF
import os

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'what-the-hell-is-going-on'

    OPENID_PROVIDERS = [
        {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
        {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
        {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
        {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
        {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

    SQLALCHEMY_DATABASE_URI = 'dev:411track1_dev@localhost/microblogdb'
