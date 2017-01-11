import sqlite3, hashlib

#Checks if username and password exist
def UserAuth(username, password):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()
    m = hashlib.sha1(password).hexdigest()
     
    if not nameAvail(username):
        q = "SELECT * FROM users WHERE username = \"%s\";" % (username)
        users.execute(q)
        info = users.fetchall()
        if (info[0][2] == m):
            return True
    return False

#Checks if username is taken
def nameAvail(username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    q = "SELECT * FROM users WHERE username = \"%s\";" % (username)
    users.execute(q)
    info = users.fetchall()
    if (len(info) > 0):
        return False
    return True

def addUser(username, password):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()
    m = hashlib.sha1(password).hexdigest()
 
    if nameAvail(username):
        q = '''INSERT INTO users(username, password, wins, gamesPlayed) VALUES("%s", "%s", "%s", %s)''' % (username, m, 0, 0)
        users.execute(q)
        db.commit()
        return True
    return False

'''def getUsersInRoom (roomname):
    db = sqlite3.connect("data/dbsm.db")
    room = db.cursor()
    m = hashlib.sha1(password).hexdigest()

    q = "SELECT userNum FROM rooms WHERE roomName =='''
