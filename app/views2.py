from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, SignupForm, EditForm, PostForm, SearchForm, RecommandForm
from .models import User, Post, Director, Movie, Movie_gr, Recomd
from oauth import OAuthSignIn
from datetime import datetime
import re
import math
from dbhelper import DBHelper
from os.path import dirname, join
import numpy as np
import pandas.io.sql as psql
import pandas as pd

from bokeh.resources import INLINE
from bokeh.plotting import figure,output_file,show
from bokeh.layouts import row, layout, widgetbox
from bokeh.models import CustomJS,ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc,vplot
from bokeh.embed import components 
from bokeh.resources import CDN

from sqlalchemy import *


t_table = {'0': False, '1': True}

@app.context_processor
def repl_processor():
    def check_at(body):
        url = "fa16-cs411-38.cs.illinois.edu:5000/user/"
        at_list = re.findall(r'@\w*', body, re.M|re.I) 
        for a in at_list:
            # repl = '<a href=\"{{ url_for(\'user\'), nickname="%s" }}\">%s</a>' % (a.split('@')[1], a)
            repl = '<a href=\"/user/%s\">%s</a>' % (a.split('@')[1], a)

            # body = re.sub(a,repl, body)
            body = body.replace(a, repl)
        return body
    return dict(check_at=check_at)



def check_at(body):
    url = "fa16-cs411-38.cs.illinois.edu:5000/user/"
    at_list = re.findall(r'@\w*', body, re.M|re.I) 
    for a in at_list:
        # repl = '<a href=\"{{ url_for(\'user\'), nickname="%s" }}\">%s</a>' % (a.split('@')[1], a)
        repl = '<a href=\"/user/%s\">%s</a>' % (a.split('@')[1], a)

        # body = re.sub(a,repl, body)
        body = body.replace(a, repl)
    return body


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.recom_form = RecommandForm()
    g.ranking = Recomd()

# Only for test
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    user = g.user
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user, private=t_table[form.private.data])

        db.session.add(post)
        db.session.commit()
        flash('Feeling good after post, huh?')
        return redirect(url_for('index'))
    if g.user.is_authenticated:
        posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    else:
        posts = Post.query.filter_by(private=False).order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html',
                           title='Home',
                           user=user,
                           form=form,
                           posts=posts)


@app.route('/data_pre')
def data_pre():

    # output_file("grap.html")

    movie_path = 'mysql+pymysql://dev_local:411track1_dev_local@localhost/microblogdb'
    db = create_engine(movie_path,encoding="utf-8")
    query = """
    SELECT distinct movie.movie_id,
       year,
       budget,
       profit_rate,
       imdb_score,
       genres as genre
    FROM movie, movie_gr, direct, director
    where movie.movie_id = movie_gr.movie_id 
    and movie.movie_id = direct.movie_id
    and direct.director_id = director.id;
    """
    movies = pd.read_sql_query(query,db)
    movies = movies.reset_index()
    
    movies["color"] = np.where(movies["imdb_score"] >= 7, "orange", "grey")
    movies["size"] = np.where(movies["profit_rate"] >= 1, 20, 10)
    movies["alpha"] = np.where(movies["profit_rate"] >= 1, 0.9, 0.35)
    def add_label(df):
        if df['profit_rate'] >= 1 and df["imdb_score"] >= 7:
            return "Profit Rate >=1 & IMDb Score >= 7"
        elif df['profit_rate'] >= 1 and df["imdb_score"] < 7:
            return "Profit Rate >=1 & IMDb Score < 7"
        elif df['profit_rate'] < 1 and df["imdb_score"] >= 7:
            return "Profit Rate < 1 & IMDb Score >= 7"
        else:
            return "Profit Rate < 1 & IMDb Score < 7"

    movies["label"] = movies.apply(add_label,axis=1)

    # Create Input controls
    min_year = Slider(title="Year released", start=1910, end=2016, value=1970, step=1)
    max_year = Slider(title="End Year released", start=1910, end=2016, value=2014, step=1)
    profit_rate = Slider(title="Minimum Profit Rate from", start=0, end=3, value=0, step=0.1)
    imdb_score = Slider(title="Minimum IMDb Score from", start=1, end=10, value=0, step=1)
    budget = Slider(title="Minimum Budget from", start=200, end=101549977, value=4000, step=1000)
    genre = Select(title="Genre", value="All",options=['All'] + movies['genre'].unique().tolist())
    # director = TextInput(title="Director name contains")
    source = ColumnDataSource(data=dict(imdb_score=movies["imdb_score"], budget=movies["budget"],color=movies["color"], label=movies['label'],size=movies["size"],alpha=movies['alpha'],year=movies['year'],profit_rate=movies['profit_rate']))
    # Create Column Data Source that will be used by the plot
    # source = ColumnDataSource(data=dict(imdb_score=movies["imdb_score"], budget=movies["budget"],color=movies["color"], label=movies['label'],
    #     size=movies["size"],alpha=movies['alpha'],title=movies['movie_title'],year=movies['year'],director=movies['director']))
    movies = ColumnDataSource(movies)
    # source = ColumnDataSource(data=dict(imdb_score=movies["imdb_score"], budget=movies["budget"],color=movies["color"], label=movies['label'],size=movies["size"],alpha=movies['alpha'],year=movies['year']))
      # var director = director.get('value').toLowerCase();
    combined_callback_code = """
  var data = source.get('data');
  var original_data = movies.get('data');
  var imdb_score = imdb_score.get('value');
  console.log("imdb_score: " + imdb_score);
  var budget = budget.get('value');
  console.log("budget: " + budget);
  var min_year = min_year.get('value');
  var max_year = max_year.get('value');
  var genre = genre.get('value');
  var profit_rate = profit_rate.get('value');

  for (var key in original_data) {
      data[key] = [];
      for (var i = 0; i < original_data['budget'].length; ++i) {
          if ((original_data['imdb_score'][i] >= imdb_score) &&
            (original_data['profit_rate'][i] >= profit_rate) &&
              (original_data['budget'][i] >= budget) && (original_data['year'][i] >= min_year) &&
              (original_data['year'][i] <= max_year) &&
              (genre==="All" || original_data['genre'][i] === genre))
            {
              data[key].push(original_data[key][i]);
          }
      }
  }
  target_obj.trigger('change');
  source.trigger('change');
  """
    hover = HoverTool(tooltips=[
        # ("Title", "@title"),
        ("Year", "@year"),
        ("$", "@budget"),
        ("Profit Rate", "@profit_rate"),
        # ('Director',"@director"),
        ('IMDb Score', "@imdb_score")
    ])
    p = figure(plot_height=700, plot_width=800, title="Movies Explorer",
      tools=["crosshair,pan,reset,save,wheel_zoom",hover],
      x_axis_label='IMDb Score',y_axis_label='Budget',
      y_range=(5000,101549977))
    p.circle(x="imdb_score", y="budget", source=source,color='color',size='size',alpha='alpha',legend='label')
    
    general_callback = CustomJS(args=dict(
        source=source, 
        movies=movies, 
        imdb_score=imdb_score,
        profit_rate=profit_rate,
        min_year = min_year,
        max_year = max_year, 
        genre = genre,
        # director=director,
        budget=budget, target_obj=p),code=combined_callback_code)


    min_year.callback = general_callback
    max_year.callback = general_callback
    genre.callback = general_callback
    budget.callback = general_callback
    imdb_score.callback = general_callback
    profit_rate.callback = general_callback
    # director.callback = general_callbacks
    controls = widgetbox(*[imdb_score, budget, profit_rate,min_year, max_year, genre])
    l = layout([[controls,p]])
    # show(l)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(l)
    return render_template('graph.html',script=script, div=div,
      js_resources=js_resources,css_resources=css_resources)



@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        username = User.make_unique_nickname(username)
        user = User(social_id=social_id, nickname=username.replace(' ', '_'), email=email)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        if form.use_openid.data:
            return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        else:
            return password_validation(form.nickname.data, form.password.data)
    return render_template('login.html',
                           title='Sign In',
                           form=form,
						   providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname.replace(' ', '_'), email=resp.email)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


def password_validation(nickname, password):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None or user.password != password:
        flash('Invalid login. Please try again')
        return redirect(url_for('login'))
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # if form.password.data == form.repassword.data:
        if True:
            user = User(nickname=form.nickname.data.replace(' ', '_'), email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            db.session.add(user.follow(user))
            db.session.commit()
            remember_me = False
            login_user(user, remember = remember_me)
            return render_template('signupsuccess.html',
                           title='Sign Up Success')
    return render_template('signup.html',
                           title='Sign Up',
                           form=form)


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@app.route('/user/<nickname>/<content_type>')
@app.route('/user/<nickname>/<content_type>/<int:page>')
@login_required
def user(nickname, page=1, content_type="post_self"):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    if content_type == "post_liked":
        content = user.liked.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
        content_page = "post"
    elif content_type == "follow":
        content = user.followed.paginate(page, app.config['POSTS_PER_PAGE'], False)
        content_page = "user"
    elif content_type == "follower":
        content = user.followers.paginate(page, app.config['POSTS_PER_PAGE'], False)
        content_page = "user"
    if content_type == "post_self":
        if g.user == user:
            content = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
        else:
            content = user.posts.filter_by(private=False).order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
        content_page = "post"

        
    return render_template('user.html',
                           content_page=content_page,
                           user=user,
                           content=content,
                           content_type=content_type)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Can\'t follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    # return redirect(url_for('user', nickname=nickname))
    return redirect(request.referrer)


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Can\'t unfollow ' + nickname + '.')
        return direct('user', nickname=nickname)
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    # return redirect(url_for('user', nickname=nickname))
    return redirect(request.referrer)


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>', methods=['GET', 'POST'])
@app.route('/search_results/<query>/<int:page>', methods=['GET', 'POST'])
@app.route('/search_results/<int:page>', methods=['GET', 'POST'])
@login_required
def search_results(query, page=1):
        #posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    user_results = User.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS'], like=True).all()
    post_results = Post.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS'], like=True).all()
    director_results = Director.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS'], like=True).paginate(page, app.config['POSTS_PER_PAGE'], False)

    movie_results = Movie.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS'], like=True)
    form = PostForm()
    return render_template('search_results.html',
                           query=query,
                           form=form,
                           user_results=user_results,
                           post_results=post_results,
                           director_results=director_results,
                           movie_results=movie_results)


@app.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get(int(post_id))
    db.session.delete(post)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/like/<post_id>')
@login_required
def like(post_id):
    post = Post.query.get(int(post_id))
    if post is None:
        flash('Post not found',)
        return redirect(url_for('index'))
    l = g.user.like(post)
    if l is None:
        flash('Can\'t like post ')
        return redirect(request.referrer)
    db.session.add(l)
    db.session.commit()
    flash('You liked a post')
    return redirect(request.referrer)


@app.route('/dislike/<post_id>')
@login_required
def dislike(post_id):
    post = Post.query.get(int(post_id))
    if post is None:
        flash('Post not found')
        return redirect(url_for('index'))
    l = g.user.dislike(post)
    if l is None:
        flash('Can\'t dislike post')
        return redirect(request.referrer)
    db.session.add(l)
    db.session.commit()
    flash('You disliked a post')
    return redirect(request.referrer)


@app.route('/repost/<post_id>', methods=['GET', 'POST'])
@login_required
def repost(post_id):
    user = g.user
    form = PostForm()
    post = Post.query.get(int(post_id))
    if post is None:
        flash('Post not found')
        return redirect(url_for('index'))
    new_body = '//@%s:%s' % (post.author.nickname, post.body)
    # new_post = Post(body=check_at(new_body), timestamp=datetime.utcnow(), author=g.user)
    # db.session.add(new_post)
    # db.session.commit()
    # flash('You disliked a post')
    # return redirect(request.referrer)

    if form.validate_on_submit():
        #check_at(form.post.data)
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user, private=form.private.data)
        db.session.add(post)
        db.session.commit()
        flash('Feeling good after post, huh?')
        return redirect(url_for('index'))
    form.post.data = new_body
    posts = g.user.followed_posts().paginate(1, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html',
                           title='Home',
                           user=user,
                           form=form,
                           posts=posts)

@app.route('/director_page/<int:id>')
@login_required
def director_page(id):
    director = Director.query.filter_by(id=id).first()
    if director == None:
        flash('Director %s not found' % name)
        return redirect(url_for('index'))

    return render_template('director.html', director=director)


@app.route("/recomd", methods=['GET', 'POST'])
def recomd():
    DB = DBHelper()

    hasRating = g.recom_form.avgrating.data
    print(hasRating)
    genres = g.recom_form.genres.data
    hasProd = g.recom_form.prod.data
    hasBudget = g.recom_form.budget.data
    hasProfit = g.recom_form.profit.data
    year = g.recom_form.year.data
    rules = {}

    show_list = [genres, hasRating, hasProd, hasBudget, hasProfit, year] 

    if hasRating is None:
        rules["rating"] = 0.0
    else:
        rules["rating"] = 1.0
    rules["comedy"] = 0.0
    rules["thriller"] = 0.0
    rules["action"] = 0.0
    rules["romance"] = 0.0
    rules["adventure"] = 0.0
    rules["crime"] = 0.0
    rules["fantasy"] = 0.0
    rules["animation"] = 0.0
    rules["scifi"] = 0.0   
    if genres == "comedy":
        rules["comedy"] = 1.0
    elif genres == "thriller":
        rules["thriller"] = 1.0
    elif genres == "action":
        rules["action"] = 1.0
    elif genres == "romance":
        rules["romance"] = 1.0   
    elif genres == "adventure":
        rules["adventure"] = 1.0  
    elif genres == "crime":
        rules["crime"] = 1.0
    elif genres == "fantasy":
        rules["fantasy"] = 1.0      
    elif genres == "animation":
        rules["animation"] = 1.0      
    elif genres == "scifi":
        rules["scifi"] = 1.0

    rules["prod"] = 0.0
    rules["budget"] = 0.0
    rules["profit"] = 0.0
    rules["lt1990"] = 0.0
    rules["lt2000"] = 0.0
    rules["lt2010"] = 0.0
    rules["gt2010"] = 0.0   
    if hasProd == "selected":
        rules["prod"] = 1.0
    if hasBudget == "selected":
        rules["budget"] = 1.0
    if hasProfit == "selected":
        rules["profit"] = 1.0
    if year == "lt1990":
        rules["lt1990"] = 1.0
    elif year == "lt2000":
        rules["lt2000"] = 1.0
    elif year == "lt2010":
        rules["lt2010"] = 1.0
    elif year == "gt2010":
        rules["gt2010"] = 1.0
    recomds = DB.get_recomd(rules)

    directors = []
    for recomd in recomds:
        directors.append(Director.query.filter_by(name=recomd[0]).first())

    passValue = {}
    visible = {}
    visible["genres"] = 0 if genres == "none"  else 1
    visible["rating"] = 1 if hasRating else 0
    print("visibal:", visible["rating"])
    visible["prod"] = 1 if hasProd else 0
    visible["budget"] = 1 if hasBudget else 0
    visible["profit"] = 1 if hasProfit else 0
    visible["year"] = 0 if year == "none" else 1
    passValue["visible"] = visible
    name_value = [x[0] for x in recomds]
    passValue["name"] = name_value
    genres_idx = {"comedy":9,"thriller":10,"action":11,"romance":12,
                 "adventure":13,"crime":14,"fantasy":15,
                 "animation":16,"scifi":17}
    genres_cheng = {"comedy":12.5,"thriller":8,"action":8,"romance":8,
                 "adventure":8,"crime":6,"fantasy":5.5,
                 "animation":3.5,"scifi":5.5}
    genres_value = [0]*4 if genres == "none" else \
                [round(x[genres_idx[genres]]*genres_cheng[genres]) for x in recomds]
    passValue["genres_type"] = "" if genres == "none" else genres
    passValue["genres"] = genres_value
    passValue["rating"] = [0]*4 if hasRating is None else [x[1]*10/1.5 for x in recomds]
    passValue["prod"] = [0]*4 if hasProd is None else [round(x[8]*15) for x in recomds]
    passValue["budget"] = [0]*4 if hasBudget is None else [round(math.exp(x[2]*20))/1000000 for x in recomds]
    passValue["profit"] = [0]*4 if hasProfit is None else [x[3]*1.8 for x in recomds]
    year_idx = {"gt2010":4,"lt1990":5,"lt2000":6,"lt2010":7}
    year_value = [0]*4 if year == "none" else [x[year_idx[year]] for x in recomds]
    if year == " ":
        year_range = "none"
    elif year == "lt1990":
        year_range = "early than 1990"
    elif year == "lt2000":
        year_range = "between 1990 and 2000"
    elif year == "lt2010":
        year_range = "between 2000 and 2010"
    else:
        year_range = "after 2010"
    passValue["year_range"] = year_range
    passValue["year"] = year_value

    return render_template("recommandation.html", passValue=passValue, directors=directors, show_list=show_list)




@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
