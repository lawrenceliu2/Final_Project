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
    if (verified):
        return render_template("home.html", isLoggedIn=verified, isInRoom=inroom, username=session["user"])
    else:
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
                session["room"] = roomname
                if (len(getUsersInRoom(roomname)) == 2):
                    init_game(roomname)
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
@app.route("/profile/<username>")

def profile(username):
    if ("user" in session):
        if (nameAvail(username)):
            return render_template("profile.html", isGuest=True)
        wins = getWins(username)
        games = getGamesPlayed(username)
        rate = getWinrate(username)
        if (rate == -1):
            rate = "No games played."
        else:
            rate = str(rate*100) + "%"
        if (username == session["user"]):
            return render_template("profile.html", user=username, isUser=True, wins = wins, games = games, rate = rate)
        else:
            return render_template("profile.html", user = session["user"], wins = wins, games = games, rate = rate)
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
@app.route("/mkroom", methods=["GET"])

def mkroom():
    rmname = request.args.get("rname")
    if (rmname == ""):
        rmname = "room_" + os.urandom(5).encode("hex")
    if ("user" in session):
        if makeRoom(rmname, session["user"]):
            return redirect("/play/"+rmname)
    return redirect("/rooms")

#------------------------------
@app.route("/leave")

def leave():
    #if ("user" in session):
    #    socket.emit("departure",session["user"],room=session["room"])
    #if (removePlayer(session["room"], session["user"])):
    #if (session["user"]):
    #        if ( session["room"] and (session["room"] in getRooms(True)) and (session["user"] == getCurrentUser(session["room"])) ):
     #           changeTurn(session["room"])
      #          init_game(session["room"])
      #      session.pop("room")
    if "room" in session:
        session.pop("room")
    return redirect(url_for("rooms"))
    #return redirect(url_for("play",roomname=session["room"]))
    #return redirect(url_for("root"))

#------------------------------
@socket.on("disconnect")
def notifDisc():
    if ("user" in session):
        socket.emit("departure",session["user"],room=session["room"])
        if (removePlayer(session["room"], session["user"])):
            if ( session["room"] and (session["room"] in getRooms(True)) and (session["user"] == getCurrentUser(session["room"])) ):
                changeTurn(session["room"])
                init_game(session["room"])
            session.pop("room")

@socket.on("join")#, namespace="/play")
def initUser():
    if ("user" not in session):
        tempname = "Guest_"+os.urandom(5).encode("hex")
        session["user"] = tempname
    emit("init",{"user":session["user"],"room":session["room"],"word":getCurrentWord(session["room"]),"turn":getCurrentUser(session["room"]),"players":getUsersInRoom(session["room"])})
    join_room(session["room"])
    socket.emit("entry",session["user"],room=session["room"],include_self=False)
    
@socket.on("message")
def message(data):
    word = getCurrentWord(session["room"])
    print word
    if (word):
        if word.lower() in data["msg"].lower():
            data["msg"] = data["msg"].replace(word,"****")
            #emit("gotWord");
    socket.emit("chat",data,include_self=False,room=session["room"])
        
#print "received message from client: "+msg

@socket.on("draw")
def draw(data):
    #print "hey got draw event, sending Buf"
    #print session["room"]
    socket.emit("buf",data,include_self=False,room=session["room"])

@socket.on("clear")
def clear():
    socket.emit("clear",room=session["room"])
    
@socket.on("turnreq")
def turnCheck():
    #print getUsersInRoom(session["room"])
    #if getUsersInRoom(session["room"]) <= 1:
        #print "hey"
       # return False
    user = getCurrentUser(session["room"])
    #print user
    if user == session["user"]:
    	return True
    else:
    	return False

@socket.on("turnconf")
def turnConf(data):
    socket.emit("startNewTurn",{"user":getCurrentUser(session["room"]),"word":getCurrentWord(session["room"])})

@socket.on("cycleturn")
def cycleTurn():
    print "turn cycled"
    word = getCurrentWord(session["room"])
    changeTurn(session["room"])
    #clear(None)
    socket.emit("pulseWord",word,room=session["room"])
    socket.emit("startNewTurn",{"user":getCurrentUser(session["room"]),"word":getCurrentWord(session["room"]),"numplayers":len(getUsersInRoom(session["room"]))})

@socket.on("wordconf")
def conf_word():
    return True

@socket.on("timeupdate")
def timeUpdate(data):
    socket.emit("timecheck",data,include_self=False);


#------------------------------
def init_game(roomname):
    socket.emit("startNewTurn",{"user":getCurrentUser(roomname),"word":getCurrentWord(roomname),"numplayers":len(getUsersInRoom(roomname))},room=roomname)
    

if (__name__ == '__main__'):
    app.debug = True
    socket.run(app)
