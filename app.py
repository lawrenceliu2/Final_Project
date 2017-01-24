from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, send, emit
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
@app.route("/play/<roomname>")

def play(roomname):
    if (roomname == ""):
        return redirect(url_for(root))
    session["room"] = roomname
    if not (roomname in getRooms()):
        makeRoom(roomname,"julian")
    #if "user" in session:
        #return render_template("index.html")
    return render_template("index.html")

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
        return redirect("/")
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
@app.route("/instructions")

def instructions():
    return render_template("instructions.html")

#------------------------------
@app.route("/rooms")

def rooms():
    roomlist = getRooms()
    dict = {}
    for x in roomlist:
        dict[str(x[0])] = str(x[1])
    return render_template("rooms.html", tabledict=dict)

@app.route("/leave")

def leave():
    if ("user" in session):
        if removePlayer(session["room"], session["user"]):
            return render_template("rooms.html")
    return redirect("/play/"+session["room"])

#------------------------------
@socket.on("connect")#, namespace="/play")
def initUser():
    if ("user" in session):
        emit("init",{"user":session["user"],"room":session["room"]})
        join_room(session["room"])
        addPlayer(session["room"],session["user"])
    else:
        tempname = "Guest_"+os.urandom(5).encode("hex")
        session["user"] = tempname
        emit("init",{"user":tempname,"room":session["room"]})
        join_room(session["room"])
        addPlayer(session["room"],tempname)
    
    
@socket.on("message")
def message(data):
    socket.emit("chat",data,include_self=False,room=session["room"])
#print "received message from client: "+msg
    
@socket.on("draw")
def draw(data):
    #print "hey got draw event, sending Buf"
    socket.emit("buf",data,include_self=False,room=session["room"])
        
@socket.on("clear")
def clear(data):
    socket.emit("clear",data,include_self=False,room=session["room"])

@socket.on("off")
def off(data):
    socket.emit("closepath",null,room=session["room"])
    
@socket.on("turnreq")
def turnCheck():
    user = getCurrentUser(session["room"])
    print user
    if user == session["user"]:
    	return True
    else:
    	return False
#------------------------------

if (__name__ == '__main__'):
    app.debug = True
    socket.run(app)
