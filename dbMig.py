import sqlite3
from contextlib import contextmanager

@contextmanager
def dbConnection(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def addInfo(gameId,chatId):
    with dbConnection('MafiaInfo.db') as cursor:
        cursor.execute('''
        INSERT INTO gameInfo VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''',(gameId,chatId,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,2,0))
    print("successfull")

def createDb(gameId):
    with dbConnection(f'{gameId}.db') as cursor:
        tableQueries=[
            '''
                        CREATE TABLE playerList (
                            name text NOT NULL,
                            user text NOT NULL,
                            id text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE links (
                            link text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE PRoleList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE challengeRequests (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE playerChallenger (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE challenger (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE defence (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL,
                            votes INTEGER NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE deadList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL,
                            votes INTEGER
                        )
                        ''',
            '''
                        CREATE TABLE oldDeadList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL,
                            votes INTEGER
                        )
                        ''',
            '''
                        CREATE TABLE selector (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL,
                            votes INTEGER 
                        )
                        ''',
            '''
                        CREATE TABLE salakhiList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE oldSalakhiList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE dastbandList (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
            '''
                        CREATE TABLE KeinMeeting (
                            name text NOT NULL,
                            id text NOT NULL,
                            user text NOT NULL,
                            side text NOT NULL,
                            role text NOT NULL
                        )
                        ''',
        ]
        for query in tableQueries:
            cursor.execute(query)

def listTables():
    with dbConnection('MafiaInfo.db') as cursor:
        cursor.execute('''SELECT * FROM gameInfo''')
        items = cursor.fetchall()
        for item in items:
            print(item)

def lenTables(gameId,tableName):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"SELECT COUNT(*) FROM {tableName}"
        cursor.execute(query)
        len = cursor.fetchone()[0]
        return len
def getGameId(chatId):
    with dbConnection(f'MafiaInfo.db') as cursor:
        query = f"SELECT gameId FROM gameInfo WHERE chatId = ?"
        cursor.execute(query, (chatId))
        result = cursor.fetchall()
        # Process the result
        if result:
            game_ids = [row[0] for row in result]
            print("Game IDs:", game_ids)
            return game_ids[0]


#INSERT FUNCs

def insert(gameId,tableName,player):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"INSERT INTO {tableName} VALUES (?,?,?,?,?)"
        cursor.execute(query, (player['name'],player['id'],player['user'],player['side'],player['role']))

#WV means with Votes of player(because on some tables,we have a dictionary with number of votes)
def insertWV(gameId,tableName,player):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"INSERT INTO {tableName} VALUES (?,?,?,?,?,?)"
        cursor.execute(query, (player['name'],player['id'],player['user'],player['side'],player['role'],player['Votes']))

#PL means for playerList table because this has different with another tables
def insertPL(gameId,tableName,player):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"INSERT INTO {tableName} VALUES (?,?,?,?,?,?)"
        cursor.execute(query, (player['name'],player['id'],player['user'],player['side'],player['role'],player['Votes']))

def addLink(gameId,link):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"INSERT INTO link VALUES (?)"
        cursor.execute(query,(link,))

#FETCH FUNCs

def fetchLinks(gameId):
    with dbConnection(f'{gameId}.db') as cursor:
        query = f"SELECT * FROM link "
        cursor.execute(query)
        links= cursor.fetchall()
        return links















# def createMafiaInfo():
#     with dbConnection(f'MafiaInfo.db') as cursor:
#         cursor.execute('''
#         CREATE TABLE gameInfo (
#         gameId INTEGER,
#         chatId INTEGER,
#         stopTalk INTEGER,
#         stopTask INTEGER,
#         challenge INTEGER,
#         challengeOn INTEGER,
#         blindNight INTEGER,
#         deleteVoteMessage INTEGER,
#         inqueryRequest INTEGER,
#         night INTEGER,
#         day INTEGER,
#         pick  INTEGER,
#         GodfatherJacket INTEGER,
#         SualPurchase INTEGER,
#         LeonJacket INTEGER,
#         DoctorSelfSave INTEGER,
#         ConstantineBirth INTEGER,
#         LeonBullet INTEGER,
#         NumOfVote INTEGER
#         )''')
# createMafiaInfo()
