import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import math
from dbhelper import DBHelper


app = Flask(__name__)
DB = DBHelper()

            
@app.route("/") 
def home():
   return render_template("home.html")
   
@app.route("/recomd")
def recomd():
   hasRating = request.args.get("avgrating")
   genres = request.args.get("genres")
   isAdv = request.args.get("adv")
   hasProd = request.args.get("prod")
   hasBudget = request.args.get("budget")
   hasProfit = request.args.get("profit")
   year = request.args.get("year")
   rules = {}
   
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
   if isAdv is None:
      rules["isAdv"] = False
   else:
      rules["isAdv"] = True
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
   
   passValue = {}
   visible = {}
   visible["genres"] = 0 if genres == "none"  else 1
   visible["rating"] = 0 if hasRating is None else 1
   visible["prod"] = 0 if hasProd is None else 1
   visible["budget"] = 0 if hasBudget is None else 1
   visible["profit"] = 0 if hasProfit is None else 1
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
   passValue["budget"] = [0]*4 if hasBudget is None else [round(math.exp(x[2]*20)) for x in recomds]
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
   
   return render_template("recomd2.html", passValue=passValue)
      
if __name__ == "__main__":
   app.run(port=5000, debug=True)
   
