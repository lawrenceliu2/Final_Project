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
    verified = ("verified" in session)
    inroom = ("room" in session)
    #if ("verified" in session):
        #return render_template("home.html", isLoggedIn=True)
    return render_template("home.html", isLoggedIn=verified, isInRoom=inroom)

#------------------------------
@app.route("/play/<roomname>")

def play(roomname):
    if (roomname == "" or roomname not in getRooms(True)):
        return redirect(url_for("root"))
    if ("user" in session):
        if (session["user"] in getUsersInRoom(roomname)):
            session["room"] = roomname
        else:
            if addPlayer(roomname, session["user"]):
                print "User Added++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                if (len(getUsersInRoom(roomname)) <= 2):
                    changeTurn(roomname)
                session["room"] = roomname
        return render_template("index.html",roomname=roomname,users=getUsersInRoom(roomname))
    return redirect(url_for("root"))

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
        session["verified"] = True
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
    global isGuest
    if "user" in session:
        session.pop("user")
        session.pop("verified")
    return render_template("login.html", msg="You have been logged out. Log back in here:")

#------------------------------
@app.route("/profile")

def profile():
    if ("verified" in session and "user" in session):
        return render_template("profile.html", user=session["user"])
    return redirect("/login")

#------------------------------
@app.route("/instructions")

def instructions():
    return render_template("instructions.html")

#------------------------------
@app.route("/rooms")

def rooms():
    if (("user" in session) and ("room" in session)):
        print url_for("play",roomname=session["room"])
        return redirect(url_for("play",roomname=session["room"]))
    if ("user" not in session):
        tempname = "Guest_"+os.urandom(5).encode("hex")
        session["user"] = tempname
    roomlist = getRooms(False)
    rooms = []
    for x in roomlist:
        rooms.append({"name":str(x[0]),"size":str(x[1])})
    return render_template("rooms.html", tabledict=rooms)

#------------------------------
@app.route("/mkroom")

def mkroom():
    rmname = "room" + os.urandom(5).encode("hex")
    if ("user" in session):
        print "User in session++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        if makeRoom(rmname, session["user"]):
            print "Room made++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            return redirect("/play/"+rmname)
    return redirect("/rooms")

#------------------------------
@app.route("/leave")

def leave():
    if ("user" in session):
        print "User in session+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        if (removePlayer(session["room"], session["user"])):
            print "REMOVED++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            session.pop("room")
            return redirect(url_for("rooms"))
    #return redirect(url_for("play",roomname=session["room"]))
    return redirect(url_for("root"))

#------------------------------
@socket.on("join")#, namespace="/play")
def initUser():
    if ("user" not in session):
        tempname = "Guest_"+os.urandom(5).encode("hex")
        session["user"] = tempname
    emit("init",{"user":session["user"],"room":session["room"],"word":getCurrentWord(session["room"]),"turn":getCurrentUser(session["room"])})
    join_room(session["room"])
    
@socket.on("message")
def message(data):
    word = getCurrentWord(session["room"])
    print word
    #if word.lower() in data["msg"].lower():
        #if (data["user"] == getCurrentUser(session["room"])): 
            #data["msg"] = data["msg"].replace(word,"****")
        #emit("gotWord");
    socket.emit("chat",data,include_self=False,room=session["room"])
        
#print "received message from client: "+msg

@socket.on("draw")
def draw(data):
    print "hey got draw event, sending Buf"
    print session["room"]
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
    #print user
    if user == session["user"]:
    	return True
    else:
    	return False

@socket.on("turnconf")
def turnConf(data):
    socket.emit("startNewTurn",{"user":session["user"],"word":getCurrentWord(session["room"])})

@socket.on("cycleturn")
def cycleTurn():
    changeTurn(session["room"])

socket.on("wordconf")
def conf_word():
    return True
#------------------------------

if (__name__ == '__main__'):
    app.debug = True
    socket.run(app)
