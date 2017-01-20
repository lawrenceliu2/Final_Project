import sqlite3, hashlib, random

#Methods for users table

#Checks if username and password exist
def UserAuth(username, password):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()
    m = hashlib.sha1(password).hexdigest()
     
    if not nameAvail(username):
        q = "SELECT * FROM users WHERE username = \"%s\";" % (username)
        users.execute(q)
        info = users.fetchall()
        if (info[0][1] == m):
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

#Adds a new user to the database if the username is not taken already
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

#Returns how many wins a user has
def getWins (username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    q = "SELECT wins FROM users WHERE username = \"%s\";" % (username)
    users.execute(q)
    return users.fetchall()[0][0]

#Returns how many games the user has played
def getGamesPlayed (username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    q = "SELECT gamesPlayed FROM users WHERE username = \"%s\";" % (username)
    users.execute(q)
    return users.fetchall()[0][0]

#Returns the users winrate as a decimal
#Note that if you have not played any games, this returns -1
def getWinrate (username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    wins = getWins(username)
    gamesPlayed = getGamesPlayed(username)
    if (gamesPlayed < 1):
        return -1
    return float(wins) / gamesPlayed

#Adds a game played to the specified user
def addLoss (username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    gamesPlayed = getGamesPlayed(username)+1
    q = "UPDATE users SET gamesPlayed = %s WHERE username = \"%s\";" % (gamesPlayed, username,)
    users.execute(q)
    db.commit()
    return True

#Adds a game played and a win to the specified user
def addWin (username):
    db = sqlite3.connect("data/dbsm.db")
    users = db.cursor()

    wins = getWins(username) + 1
    addLoss(username)
    q = "UPDATE users SET wins = %s WHERE username = \"%s\";" % (wins, username,)
    users.execute(q)
    db.commit()
    return True


#Methods for words table

#Returns an array of the words in the database
def getWords():
    db = sqlite3.connect("data/dbsm.db")
    words = db.cursor()

    q = "SELECT noun FROM words"
    words.execute(q)
    wordList = words.fetchall()
    realWordList = []
    for word in wordList:
        realWordList.append(str(word[0]))
    return realWordList

#Returns a random word from the current array for the user to draw
def getRandomWord():
    words = getWords()
    which = random.randint(0,len(words)-1)
    return words[which]

#Checks if the word the user guessed is the word being drawn, actual is the word being drawn
#Not sure if this is necessary but whatever
def checkWord(actual, guess):
    return actual.lower() == guess.lower()


'''print addWin("lawrence")
print getWins("lawrence")
print getGamesPlayed("lawrence")
print getWinrate("lawrence")'''

#Methods for rooms table

def getUsersInRoom (roomname):
    db = sqlite3.connect("../data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT userNum FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    numUsers = rooms.fetchall()[0][0]
    i = 1
    a = []
    while (i < numUsers + 1):
        q = "SELECT user%s FROM rooms where roomName = \"%s\";" %(i, roomname)
        rooms.execute(q)
        person = str(rooms.fetchall()[0][0])
        a.append(person)
        i+=1
    return a

print getUsersInRoom("test")
       
