
from os.path import dirname, join
import numpy as np
import pandas.io.sql as psql
from flask import Flask,render_template
import pandas as pd


from bokeh.plotting import figure,output_file,show
from bokeh.layouts import row, layout, widgetbox
from bokeh.models import CustomJS,ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc,vplot
from bokeh.embed import components 
from bokeh.resources import CDN

from sqlalchemy import *

# app = Flask(__name__)
output_file("visualization.html")
# from bokeh.sampledata.movies_data import movie_path

# movie_path = 'mysql+pymysql://dev_local:411track1_dev_local@localhost/microblogdb'
# conn = sql.connect(movie_path)
# conn=MySQLdb.connect(
#	host='fa16-cs411-38.cs.illinois.edu',
#	user='dev',
#	passwd='411track1_dev',
#	db='microblogdb')

# query = open(join(dirname(__file__), 'imdb.sql')).read()
# movies = psql.read_sql(query, conn)

# @app.route('/')
def main():
    movie_path = 'mysql+pymysql://dev_local:411track1_dev_local@localhost/microblogdb'
    db = create_engine(movie_path)
    query = "select * from movies;"


    # """
    # SELECT distinct movie.movie_id,
    #    movie_title,
    #    year,
    #    budget,
    #    profit_rate,
    #    imdb_score,
    #    genres as genre,
    #    name as director
    # FROM movie, movie_gr, direct, director
    # where movie.movie_id = movie_gr.movie_id 
    # and movie.movie_id = direct.movie_id
    # and direct.director_id = director.id;
    # """

    movies = pd.read_sql(query,db)
    # movies = pd.read_sql_query(query,db)
    # f = {'movie_id' : [1,2,3,4,5,6,7,8],
    #      'movie_title': [1,2,3,4,5,6,7,8],
    #     'budget':[1000000,5000000,2300000,40000,800000,600000,350000,90000],
    #     'genre':["Action",'Adventure','Drama','Action','Music','Action','Fantasy','Music'],
    #     'year':[1992,1993,1970,1992,1994,1945,2004,2013],
    #     'imdb_score':[7.2,8.0,6.5,4.5,6.7,9.0,5.6,8.2],
    #     'profit_rate':[.8,.7,1.6,1.5,1.4,.3,1.2,2.1],
    #     'director':['Sam Mendes','Kevin Chang','Lee Ann','Kevin Chang','Yuetong Liu','Rong Du','Leg Zuo','Leg Right']}
    # movies = pd.DataFrame(f)
    # movies = movies.reset_index()
    
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
    min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
    max_year = Slider(title="End Year released", start=1940, end=2014, value=2014, step=1)
    # profit_rate = Slider(title="profit_rate", start=0, end=10, value=0, step=1)
    imdb_score = Slider(title="Minimum IMDb Score from", start=0, end=10, value=0, step=1)
    budget = Slider(title="Minimum Budget from", start=40000, end=5000000, value=40000, step=1000)
    # genre = Select(title="Genre", value="All",
    #               options=open(join(dirname(__file__), 'genres.txt')).read().split())
    genre = Select(title="Genre", value="All",options=open('genres.txt').read().split())
    director = TextInput(title="Director name contains")

    # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data=dict(imdb_score=movies["imdb_score"], budget=movies["budget"],color=movies["color"], label=movies['label'],
        size=movies["size"],alpha=movies['alpha'],title=movies['movie_title'],year=movies['year'],director=movies['director']))
    movies = ColumnDataSource(movies)
    
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
  var director = director.get('value').toLowerCase();

  for (var key in original_data) {
      data[key] = [];
      for (var i = 0; i < original_data['budget'].length; ++i) {
          if ((original_data['imdb_score'][i] >= imdb_score) &&
              (original_data['budget'][i] >= budget) && (original_data['year'][i] >= min_year) &&
              (original_data['year'][i] <= max_year) &&
              (genre==="All" || original_data['genre'][i] === genre) &&
              (original_data['director'][i].toLowerCase().includes(director)))
            {
              data[key].push(original_data[key][i]);
          }
      }
  }
  target_obj.trigger('change');
  source.trigger('change');
  """
    hover = HoverTool(tooltips=[
        ("Title", "@title"),
        ("Year", "@year"),
        ("$", "@budget"),
        ('Director',"@director"),
        ('IMDb Score', "@imdb_score")
    ])
    p = figure(plot_height=400, plot_width=400, title="",tools=["crosshair,pan,reset,save,wheel_zoom",hover],x_axis_label='IMDb Score',y_axis_label='Budget')
    p.circle(x="imdb_score", y="budget", source=source,color='color',size='size',alpha='alpha',legend='label')
    
    general_callback = CustomJS(args=dict(
        source=source, 
        movies=movies, 
        imdb_score=imdb_score,
        min_year = min_year,
        max_year = max_year, 
        genre = genre,
        director=director,
        budget=budget, target_obj=p),code=combined_callback_code)


    min_year.callback = general_callback
    max_year.callback = general_callback
    genre.callback = general_callback
    budget.callback = general_callback
    imdb_score.callback = general_callback
    director.callback = general_callback

    controls = widgetbox(*[imdb_score, budget, min_year, max_year, genre,director])
    l = layout([[controls,p]])
    show(l)

    # script, div = components(l)
    # return render_template('description3.html', script=script, div=div)

if __name__ == '__main__':
    main()
