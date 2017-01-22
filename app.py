from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
#import utils.db_manager
from utils.db_manager import *
import hashlib, random, os

app = Flask(__name__)
app.secret_key = os.urandom(32)
socket = SocketIO(app)

#------------------------------
@app.route("/")

def root():
    if "user" in session:
        return render_template("home.html", isLoggedIn=True)
    return render_template("home.html", isLoggedIn=False)

#------------------------------
@app.route("/play")

def play():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return render_template("index.html", user="Guest")

#------------------------------
@app.route("/login")

def login():
    return render_template("login.html")

#-----------------------------
@app.route("/loginauth", methods=['GET', 'POST'])

def loginauth():
    user = request.form["user"]
    pwd = request.form["pwd"]
    if (user == "") or (pwd == ""):
        return render_template("login.html", msg="Please enter your username and password.")
    if (nameAvail(user)):
        return render_template("login.html", msg="Username does not exist.")
    if UserAuth(user, pwd):
        session["user"] = user
        return redirect("/profile")
    return render_template("login.html", msg="Username or password incorrect.")

#------------------------------
@app.route("/register", methods=['GET', 'POST'])

def reg():
    return render_template("register.html")

#------------------------------
@app.route("/regauth", methods=['GET', 'POST'])

def regauth():
    user = request.form["user"]
    pwd = request.form["pwd"]
    confirm = request.form["confirm"]
    if (user == "") or (pwd == ""):
        return render_template("register.html", msg="Please enter a username and password.")
    if (len(pwd) > 16) or (len(pwd) < 4):
        return render_template("register.html", msg="Password must be between 4 and 16 characters long.  Try again:")
    if (pwd != confirm):
        return render_template("register.html", msg="Failed to confirm password.  Try again:")
    if addUser(user, pwd):
        return render_template("login.html", msg="Account created!  Login here:")
    return render_template("register.html", msg="Username already taken.  Try again:")

#------------------------------
@app.route("/logout")

def logout():
    if "user" in session:
        session.pop("user")
    return render_template("login.html", msg="You have been logged out.  Log back in here:")

#------------------------------
@app.route("/profile")

def profile():
    if "user" in session:
        return render_template("profile.html", user=session["user"])
    return redirect("/login")

#------------------------------
@socket.on("message")
def message(data):
    socket.emit("chat",data,include_self=False)
    #print "received message from client: "+msg
    
@socket.on("draw")
def draw(data):
    #print "hey got draw event, sending Buf"
    socket.emit("buf",data,include_self=False)

@socket.on("clear")
def clear(data):
    socket.emit("clear",data,include_self=False)
#------------------------------

if (__name__ == '__main__'):
    app.debug = True
    socket.run(app)
