import sqlite3, hashlib, random

'''PROFILE STUFF
getWins ("username")
getGamesPlayed ("username")
getWinrate ("username") [as a decimal, returns -1 if you have no games played]


addLoss("username")
addWin("username")
^^^^^^^^^^^^^^^^^^ use these
'''


'''WORD STUFF
getWords()

getRandomWord() [Use this as main method of getting a random word to draw, might need to keep track of ones already used to prevent repeats]

checkWord ("actual word", "the user's guess")
'''


'''ROOM STUFF
Sequence of creating a room:
makeRoom ("roomname", "username")
addPlayer ("roomname", "username")


removePlayer ("roomname", "username")
changeTurn ("roomname") 


Getting stuff:
getRooms()
getCurrentWord ("roomname")
getCurrentUser ("roomname")
getUsersInRoom ("roomname")
'''


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



##################Methods for words table


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



##################Methods for rooms table


#Returns an array of the users currently playing
def getUsersInRoom (roomname):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT userNum FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    numUsers = rooms.fetchall()[0][0]
    i = 1
    a = []
    while (i < numUsers + 1):
        q = "SELECT user%s FROM rooms WHERE roomName = \"%s\";" %(i, roomname)
        rooms.execute(q)
        person = str(rooms.fetchall()[0][0])
        a.append(person)
        i+=1
    return a

#Returns the user who is currently drawing
def getCurrentUser (roomname):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT currentTurn FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    q = rooms.fetchall()[0][0]
    return q

def changeTurn (roomname):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    users = getUsersInRoom(roomname)
    currentUser = getCurrentUser(roomname)
    nextUser = 0
    for num in range(0, len(users) - 1):
        if users[num] == currentUser:
            if num == len(users) - 1:
                nextUser = 0
            else:
                nextUser = num + 1
    currentUser = users[nextUser]
    newCurrentWord(roomname, getRandomWord())
    return newCurrentUser(roomname, currentUser)

#Returns the room's current word being drawn
def getCurrentWord (roomname):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT currWord FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    q = rooms.fetchall()[0][0]
    return q

#Updates the current word to the new one provided
def newCurrentWord (roomname, newWord):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()
    
    q = "UPDATE rooms SET currWord = \"%s\" WHERE roomName = \"%s\";" % (newWord, roomname,)
    rooms.execute(q)
    db.commit()
    return True

#Updates the current drawer to the new one provided
def newCurrentUser (roomname, username):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "UPDATE rooms SET currentTurn = \"%s\" WHERE roomName = \"%s\";" % (username, roomname,)
    rooms.execute(q)
    db.commit()
    return True

#Create a room based on name and creator's username
def makeRoom (roomname, username):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT roomName FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    if rooms.fetchall() == []:
        q = "INSERT INTO rooms(roomName, userNum, currentTurn, user1) VALUES (\"%s\", 1, \"%s\", \"%s\");" % (roomname, username, username,)
        rooms.execute(q)
        db.commit()
        word = getRandomWord()
        newCurrentWord(roomname, word)
        return True
    return False #room with that name already exists

#Add the player to the room; return false if there is no space
def addPlayer (roomname, username):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    stuff = getRooms(False)
    for room in stuff:
        if username in room:
            return False
    q = "SELECT userNum FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    numUsers = rooms.fetchall()[0][0]
    numUsers += 1
    if (numUsers < 6):
        q = "UPDATE rooms SET user%s = \"%s\" WHERE roomName = \"%s\";" % (numUsers, username, roomname,)
        rooms.execute(q)
        q = "UPDATE rooms SET userNum = %s WHERE roomName = \"%s\";" % (numUsers, roomname,)
        rooms.execute(q)
        db.commit()
        return True
    return False # MESSAGE: FAILED TO JOIN ROOM

#Removes the specified player from the room
def removePlayer (roomname, username):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    users = getUsersInRoom(roomname)
    remove = 0
    current = getCurrentUser(roomname)
    if str(current) == username:
        changeTurn(roomname)
    q = "SELECT userNum FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    numUsers = rooms.fetchall()[0][0]
    numUsers -= 1
    if numUsers == 0:
        removeRoom(roomname)
        return True
    for num in range(0,numUsers+1):
        if username == str(users[num]):
            remove = num + 1
            print remove
    if remove == 0:
        return False
    q = "UPDATE rooms SET userNum = %s WHERE roomName = \"%s\";" % (numUsers, roomname)
    rooms.execute(q)
    q = "UPDATE rooms SET user%s = \"\" WHERE roomName = \"%s\";" %(remove, roomname)
    rooms.execute(q)
    if remove == len(users):
        db.commit()
    while remove < len(users):
        q = "SELECT user%s FROM rooms WHERE roomName = \"%s\";" %  (remove + 1, roomname)
        rooms.execute(q)
        placeholder = rooms.fetchall()[0][0]
        q = "UPDATE rooms SET user%s = \"%s\" WHERE roomName = \"%s\";" % (remove, placeholder, roomname)
        rooms.execute(q)
        q = "UPDATE rooms SET user%s = \"\" WHERE roomName = \"%s\";" % (remove + 1, roomname)
        rooms.execute(q)
        remove += 1
        db.commit()
    return True

#Returns a list of open rooms
#Returns only names if <names> is True

def getRooms(names):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "SELECT * FROM rooms;"
    rooms.execute(q)
    roomList = rooms.fetchall()
    realRoomList = []
    for room in roomList:
        if names:
            realRoomList.append(room[0])
        else:
            realRoomList.append(room)
    return realRoomList

#Removes the room specified
def removeRoom(roomname):
    db = sqlite3.connect("data/dbsm.db")
    rooms = db.cursor()

    q = "DELETE FROM rooms WHERE roomName = \"%s\";" % (roomname)
    rooms.execute(q)
    db.commit()
    return True

print changeTurn("test")
