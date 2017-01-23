from app import app, db
from flask_login import UserMixin
from hashlib import md5
from sqlalchemy import PrimaryKeyConstraint


import sys
if sys.version_info >= (3,0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemyplus as whooshalchemy


# Relations

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


likes = db.Table('likes', 
                 db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                 db.Column('liker_id', db.Integer, db.ForeignKey('user.id'))
)


actin = db.Table('actin',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'))
)


direct = db.Table('direct',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')),
    db.Column('director_id', db.Integer, db.ForeignKey('director.id'))
)


# Schemas

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __searchable__ = ['nickname']
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(32), index=False, unique=False)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'))

    # Relations
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
#    liked = db.relationship('Post',
#                            secondary=likes,
#                            primaryjoin=(likes.c.liker_id == id),
#                            secondaryjoin=(likes.c.post_id == Post.c.id),
#                            backref=db.backref('likers', lazy='dynamic'), lazy='dynamic')
    liked = db.relationship('Post', 
                            secondary=likes, 
                            primaryjoin=(likes.c.liker_id == id),
                            backref=db.backref('likers', lazy='dynamic'),
                            lazy='dynamic')

    verified = db.relationship('Director', backref='social_account')

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_verified(self):
        return len(self.verified) > 0

    def get_id(self):
        try:
            return unicode(self.id)    # python 2
        except NameError:
            return str(self.id)    #python 3


    def avatar(self, size):
        if self.email is None:
            mail = ''
        else:
            mail = self.email
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(mail.encode('utf-8')).hexdigest(), size)


    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self


    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self


    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id, Post.private==False).order_by(Post.timestamp.desc())


    def like(self, post):
        if not self.is_liking(post):
            self.liked.append(post)
            return self


    def dislike(self, post):
        if self.is_liking(post):
            self.liked.remove(post)
            return self


    def is_liking(self, post):
        return self.liked.filter(likes.c.post_id == post.id).count() > 0
        #return self.liked.filter(likes.c.post_id == post.id) 


    def __repr__(self):
		return '<User %r>' % (self.nickname)




class Post(db.Model):
    __tablename__ = 'post'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    private = db.Column(db.Boolean, default=False) 


#    def liker_count(self):
#        return len(self.likers)


    def __repr__(self):
        return '<Post %r>' % (self.body)




class Actor(db.Model):
    __tablename__ = 'actor'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(110), nullable = False)
    gender = db.Column(db.String(1))

    # Relations
    acted = db.relationship('Movie',
                            secondary=actin,
                            primaryjoin=(actin.c.actor_id == id),
                            backref=db.backref('actors', lazy='dynamic'),
                            lazy='dynamic')


class Director(db.Model):
    __tablename__ = 'director'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(110), nullable = False)
    gender = db.Column(db.String(1))
    biography = db.Column(db.String(55678))
    hometown = db.Column(db.String(110))
    birthday = db.Column(db.String(20))
    height = db.Column(db.String(15))

    # Relations
    directed = db.relationship('Movie',
                               secondary=direct,
                               primaryjoin=(direct.c.director_id == id),
                               backref=db.backref('directors', lazy='dynamic'),
                               lazy='dynamic')


    def movie_by_year(self):
        return self.directed.order_by(Movie.year.desc())

    def movie_by_rating(self):
        return self.directed.order_by(Movie.imdb_score.desc())

class Movie(db.Model):
    __tablename__ = 'movie'
    __searchable__ = ['movie_title']

    movie_id = db.Column(db.Integer, primary_key = True)
    movie_title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    budget = db.Column(db.Float)
    profit_rate = db.Column(db.Float)
    imdb_score = db.Column(db.Float)
    movie_imdb_link = db.Column(db.String(60))


class Movie_gr(db.Model):
    __tablename__ = 'movie_gr'
    __searchable__ = ['genres']
    __table_args__ = (
        PrimaryKeyConstraint('movie_id', 'genres'),
    )

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'))
    genres = db.Column(db.String(15))


class Recomd(db.Model):
    __tablename__ = 'recomd'

    director_id = db.Column(db.Integer,db.ForeignKey('director.id'), primary_key = True)
    avgrating = db.Column(db.Float)
    avgbudget = db.Column(db.Float)
    avgprofit = db.Column(db.Float)
    general_score = db.Column(db.Float)
    gt2010 = db.Column(db.Float)
    lt1990 = db.Column(db.Float)
    lt2000 = db.Column(db.Float)
    lt2010 = db.Column(db.Float)
    productivity = db.Column(db.Float)
    gr_comedy = db.Column(db.Float)
    gr_thriller = db.Column(db.Float)
    gr_action = db.Column(db.Float)
    gr_romance = db.Column(db.Float)
    gr_adventure = db.Column(db.Float)
    gr_crime = db.Column(db.Float)
    gr_fantasy = db.Column(db.Float)
    gr_animation = db.Column(db.Float)
    gr_scifi = db.Column(db.Float)

    # Relation
    director = db.relationship('Director', backref='ranking')

    def general_ranking(self):
        return self.query.order_by(Recomd.general_score.desc())


if enable_search:
    whooshalchemy.whoosh_index(app, Post)
    whooshalchemy.whoosh_index(app, User)
    whooshalchemy.whoosh_index(app, Actor)
    whooshalchemy.whoosh_index(app, Director)
    whooshalchemy.whoosh_index(app, Movie)

    # Question:
    whooshalchemy.whoosh_index(app, Movie_gr)
