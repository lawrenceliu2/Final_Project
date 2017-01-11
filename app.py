from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
import utils.db_manager
import hashlib, random, os

app = Flask(__name__)
app.secret_key = os.urandom(32)
socket = SocketIO(app)

## #------------------------------
## @app.route("/")

## def root():
##     if "user" in session:
##         return render_template("index.html")
##     return render_template("login.html")

## #------------------------------
## @app.route("/login", methods=['GET', 'POST'])

## def login():
##     user = request.form["user"]
##     pwd = request.form["pass"]
##     if (user == "") or (pwd == ""):
##         return render_template("login.html", msg="Please enter your username and password.")
##     if db_manager.UserAuth(user, pwd):
##         session["user"] = user
##         return redirect("/")
##     return render_template("login.html", msg="Username or password incorrect.")

## #------------------------------
## @app.route("/register", methods=['GET', 'POST'])

## def reg():
##     return render_template("register.html")

## #------------------------------
## @app.route("/regauth", methods=['GET', 'POST'])

## def regauth():
##     user = request.form["user"]
##     pwd = request.form["pass"]
##     confirm = request.form["confirm"]
##     if (user == "") or (pwd == ""):
##         return render_template("register.html", msg="Please enter a username and password.")
##     if (pwd != confirm):
##         return render_template("register.html", msg="Failed to confirm password.  Try again:")
##     if addUser(user, pwd):
##         return render_template("login.html", msg="Account created!  Login here:")
##     return render_template("register.html", msg="Username already taken.  Try again:")

## #------------------------------
## @app.route("/logout")

## def logout():
##     if "user" in session:
##         session.pop("user")
##     return render_template("login.html", msg="You have been logged out.  Log back in here:")

#------------------------------
@socket.on("message")
def message(msg):
    print "received message from client: "+msg
    
@socket.on("draw")
def draw(data):
    #print "hey got draw event, sending Buf"
    socket.emit("buf",data,include_self=False)

#------------------------------

if (__name__ == '__main__'):
    app.debug = True
    socket.run(app)
