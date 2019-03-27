from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask import escape
from flask import redirect
from flask import url_for
from tabulate import tabulate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import os

dbdir="sqlite:///" + os.path.abspath(os.getcwd()) +"/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50))
class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True ,nullable=False)
    password=db.Column(db.String(80),unique=True ,nullable=False)
class Lockers(db.Model):
     nLocker=db.Column(db.Integer,primary_key=True) 
     ocupado=db.Column(db.Boolean,nullable=False)
     tiempoOcupado=db.Column(db.Integer,nullable=False)
     ocupante=db.Column(db.String,unique=True ,nullable=False)
    
@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/principal",methods=["GET","POST"])
def principal():
    comprobante=False
    if "username" in session and Lockers.query.filter_by(ocupado=False).first() :
        ocupacion="presione para apartar un casillero"
    elif "username" in session:
            ocupacion="no hay casilleros disponibles"
    else:     
        return  redirect(url_for("login"))   
    if request.method=="POST":
        for i in range(1,60):
            if Lockers.query.get(i).ocupante==session["username"]:
                return render_template("principal.html" ,ocupacion="ya tiene un casillero asignado N:{}".format(i))
                break
            elif  Lockers.query.get(i).ocupado==False:
                Lockers.query.get(i).ocupado=True
                Lockers.query.get(i).ocupante=session["username"]
                Lockers.query.get(i).tiempoOcupado=0
                db.session.commit()
                return render_template("principal.html" ,ocupacion="ya tiene un casillero asignado N:{}".format(i))
                break      
            
        return render_template("principal.html" ,ocupacion="que no hay manito")    
    return render_template("principal.html" ,ocupacion=ocupacion)    
                 
                

@app.route("/principal/Administrador",methods=["GET","POST"])
def administrador():
    
    if request.method=="POST":
        clave=request.form["passwordA"]
        if  "veneca"==clave:
            
            return redirect(url_for("administradors"))
    return render_template("administrador.html")

@app.route("/principal/Administrador/ola",methods=["GET","POST"])
def administradors():
    if request.method=="POST":
         
        if request.form['submit'] == "ver": 
            for i in range(1,60):
                if Lockers.query.get(i).ocupante==request.form["num"] or str(Lockers.query.get(i).nLocker)==request.form["num"]:
                    imprimir1= "______________________________________________________________________________________________________________________________________________________"
                    imprimir2="   ||   locker:"+str(i) + "   ||   ocupado: " + str(Lockers.query.get(i).ocupado) + "   ||   usuario:" + str(Lockers.query.get(i).ocupante) + "   ||   tiempo: " + str(Lockers.query.get(i).tiempoOcupado) + "   ||   "
                    imprimir3="-----------------------------------------------------------------------------------------------------------------------------------------------------"
                     
                    return  render_template("disponibilidad.html",imprimir1=imprimir1,imprimir2=imprimir2,imprimir3=imprimir3)     
            return  render_template("disponibilidad.html",imprimir= "no existe dicho locker o usuario registrado")                        
        if request.form['submit'] == "vaciar":
            for i in range(1,60):
                if Lockers.query.get(i).ocupante==request.form["num"] or str(Lockers.query.get(i).nLocker)==request.form["num"]: 
                    Lockers.query.get(i).ocupado=False 
                    Lockers.query.get(i).ocupante="estudiante {}".format(i)
                    Lockers.query.get(i).tiempoOcupado=0
                    db.session.commit()
            return  render_template("disponibilidad.html",imprimir1="__________________________",imprimir2=" ",imprimir3="-----------------------------" )                     
        elif request.form['submit'] == 'multar': 
            for i in range(1,60):
                if Lockers.query.get(i).tiempoOcupado>12:
                    imprimir1= "______________________________________________________________________________________________________________________________________________________"
                    imprimir2="   ||   locker:"+str(i) + "   ||   ocupado: " + str(Lockers.query.get(i).ocupado) + "   ||   usuario:" + str(Lockers.query.get(i).ocupante) + "   ||   tiempo: " + str(Lockers.query.get(i).tiempoOcupado) + "   ||   "
                    imprimir3="-----------------------------------------------------------------------------------------------------------------------------------------------------"
                     
                    return  render_template("disponibilidad.html",imprimir1=imprimir1,imprimir2=imprimir2,imprimir3=imprimir3)   
    return  render_template("disponibilidad.html",imprimir1="__________________________",imprimir2="   ",imprimir3="-----------------------------" )                               

# @app.route("/insert/default")
# def insert_default():
#     for i in range(1,60):
#      new_post=Lockers(nLocker=i , ocupado=False,tiempoOcupado=0,ocupante="estudiante: {}".format(i))
#      db.session.add(new_post)
#      db.session.commit()
#     return "the deafault post was created"

# @app.route("/signup",methods=["GET","POST"])
# def signup():    
#      if request.method=="POST":
#          hashed_pw=generate_password_hash(request.form["password"],method="sha256")
#          new_user=Users(username=request.form["username"],password=hashed_pw)
#          db.session.add(new_user)
#          db.session.commit()
#          return "You have registered"
#      return render_template("signup.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if "username" in session:    
     session.pop("username", None)
    if request.method=="POST":
        user =Users.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password,request.form["password"] ):
            session["username"]=user.username
             
            return  redirect(url_for("principal"))
     
    return render_template("login.html")
    

@app.route("/home")
def home(): 
 if "username" in session:
     return "you are %s"% escape(session["username"])
 else:    
     return  redirect(url_for("login"))


if __name__=="__main__":
 db.create_all()   
 app.secret_key = 'some secret key'
 app.run(debug=True,port=8000) 
 