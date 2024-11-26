import sqlite3

conn= sqlite3.connect('MafiaInfo.db')
c= conn.cursor()

c.execute('''
CREATE TABLE gameInfo (
gameId INTEGER,
chatId text,
stopTalk INTEGER,
stopTask INTEGER,
challenge INTEGER,
challengeOn INTEGER,
blindNight INTEGER,
deleteVoteMessage INTEGER,
inqueryRequest INTEGER,
night INTEGER,
day INTEGER,
pick  INTEGER,
GodfatherJacket INTEGER,
SualPurchase INTEGER,
LeonJacket INTEGER,
DoctorSelfSave INTEGER,
ConstantineBirth INTEGER,
LeonBullet INTEGER,
NumOfVote INTEGER
)''')

conn.commit()
conn.close()