from sqlalchemy import (Table, Column, Integer, Numeric, String)
from sqlalchemy import (MetaData, create_engine, select, ForeignKey, desc)
from app import app

class DBHelper:
    def connect(self, database="imdb2"):
        metadata = MetaData()
        recomd = Table('recomd', metadata,
                 Column('director_id', Integer(),ForeignKey('director.id')),
                 Column('avgrating', Numeric(5,3)),
                 Column('avgbudget', Numeric(5,3)),
                 Column('avgprofit', Numeric(5,3)),
                 Column('general_score', Numeric(5,3)),
                 Column('gt2010', Numeric(5,3)),
                 Column('lt1990', Numeric(5,3)),
                Column('lt2000', Numeric(5,3)),
                Column('lt2010', Numeric(5,3)),
                Column('productivity', Numeric(5,3)),
                Column('gr_comedy', Numeric(5,3)),
                Column('gr_thriller', Numeric(5,3)),
                Column('gr_action', Numeric(5,3)),
                Column('gr_romance', Numeric(5,3)),
                Column('gr_adventure', Numeric(5,3)),
                Column('gr_crime', Numeric(5,3)),
                Column('gr_fantasy', Numeric(5,3)),
                Column('gr_animation', Numeric(5,3)),
                Column('gr_scifi', Numeric(5,3))
               )
        director = Table('director', metadata,
                 Column('id', Integer()),
                 Column('name', String(110)),
                 Column('gender', String(1)),
                 Column('biography', String(55678)),
                 Column('hometown', String(110)),
                Column('birthday', String(20)),
                Column('height', String(15)))

        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        metadata.create_all(engine)
        return engine.connect(),recomd,director
        
    def get_recomd(self,rules):
        conn, recomd, director = self.connect()
        try:
            s1 = select([recomd.c.director_id,
                        (recomd.c.avgrating*rules["rating"]+
                        recomd.c.avgbudget*rules["budget"]+
                        recomd.c.avgprofit*rules["profit"]+
                        recomd.c.general_score*0.01+
                        recomd.c.gt2010*rules["gt2010"]+
                        recomd.c.lt1990*rules["lt1990"]+
                        recomd.c.lt2000*rules["lt2000"]+
                        recomd.c.lt2010*rules["lt2010"]+
                        recomd.c.productivity*rules["prod"]+
                        recomd.c.gr_comedy*rules["comedy"]+
                        recomd.c.gr_thriller*rules["thriller"]+
                        recomd.c.gr_action*rules["action"]+
                        recomd.c.gr_romance*rules["romance"]+
                        recomd.c.gr_adventure*rules["adventure"]+
                        recomd.c.gr_crime*rules["crime"]+
                        recomd.c.gr_fantasy*rules["fantasy"]+
                        recomd.c.gr_animation*rules["animation"]+
                        recomd.c.gr_scifi*rules["scifi"]).label("score")])
            s1 = s1.order_by(desc("score")).limit(4)
            rp = conn.execute(s1)
            results = rp.fetchall()
            recomd_dir_id = [x[0] for x in results]
            col = [director.c.name, director.c.id, recomd.c.avgrating, 
                    recomd.c.avgbudget, recomd.c.avgprofit, 
                    recomd.c.gt2010, recomd.c.lt1990, recomd.c.lt2000, 
                    recomd.c.lt2010, recomd.c.productivity, recomd.c.gr_comedy,
                    recomd.c.gr_thriller, recomd.c.gr_action, recomd.c.gr_romance,
                    recomd.c.gr_adventure, recomd.c.gr_crime, recomd.c.gr_fantasy,
                    recomd.c.gr_animation, recomd.c.gr_scifi]
            s2 = select(col).select_from(director.join(recomd)).where(
                    director.c.id.in_(recomd_dir_id))
            rp = conn.execute(s2)
            results = rp.fetchall()
            foo = {}
            for dir_info in results:
                score = [float(x) for x in dir_info[2:]]
                foo[dir_info[1]] = [dir_info[0]] + score 
            recomd_dir_info = []
            for id in recomd_dir_id:
                recomd_dir_info.append(foo[id])
            return recomd_dir_info      
        finally:
            conn.close()
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
        
