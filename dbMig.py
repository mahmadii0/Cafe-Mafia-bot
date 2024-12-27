import mysql.connector
from contextlib import contextmanager
from constants import connectionDetail
from constants import PlayerList
@contextmanager
def dbConnection():
    conn = None
    cursor = None
    try:
        # Establish the connection
        conn = mysql.connector.connect(
            host=connectionDetail['host'],
            port=connectionDetail['port'],
            user=connectionDetail['user'],
            password=connectionDetail['password'],
            database=connectionDetail['database']
        )
        cursor = conn.cursor()
        conn.autocommit=True
        yield cursor

    except Exception as e:
        print("An error occurred:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print('Connection closed')

def deleteTables():
    with dbConnection() as cursor:
        tables=['players','games_players']
        for table in tables:
            cursor.execute(f"DELETE FROM `{table}`")


def addgame(gameId,chatId):
    with dbConnection() as cursor:
        cursor.execute(f'''SELECT * FROM games_info WHERE chat_id=%s AND status=1 ''',(str(chatId),))
        existGame=cursor.fetchall()
        if existGame:
            cursor.execute(f'''UPDATE games_info SET status = 0
            WHERE game_id = "{existGame[0][0]}"
            ''')
            return addgame(gameId,chatId)
        else:
            cursor.execute('''
            INSERT INTO games_info  
            VALUES (%s, %s, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1)
            ''', (abs(int(gameId)), str(chatId),))
        print("Successfully game added")

def lenPlayers(gameId):
    with dbConnection() as cursor:
        query = f"SELECT COUNT(*) FROM players WHERE game_id= %s"
        cursor.execute(query,(int(gameId),))
        len = cursor.fetchone()[0]
        if len:
            return len
        else:
            len='0'
            return len
def getGameId(chatId):
    with dbConnection() as cursor:
        query = f"SELECT game_id FROM games_info WHERE chat_id = %s AND status = 1"
        #ORDER BY ROWID DESC LIMIT 1
        cursor.execute(query, (chatId,))
        result = cursor.fetchone()
        print(type(result))
        print(result)
        return result[0]
def trueChallenge(gameId):
    with dbConnection() as cursor:
        query = f"UPDATE games_info SET challenge = 1 WHERE game_id = %s"
        cursor.execute(query, (int(gameId),))
def stopTalk(operate,gameId):
    with dbConnection() as cursor:
        #operate is boolean that if it is true, it means function want to change the value of stop_talk in table to true and vice versa
        if operate:
            query = f"UPDATE games_info SET stop_talk = 1 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))
        else:
            query = f"UPDATE games_info SET stop_talk = 0 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))

#INSERT FUNCs

# def insert(gameId,tableName,player):
#     with dbConnection(f'{gameId[0]}.db') as cursor:
#         query = f"INSERT INTO '{tableName}' VALUES (?,?,?,?,?)"
#         cursor.execute(query, (player['name'],player['id'],player['user'],player['side'],player['role']))
#
# #WV means with Votes of player(because on some tables,we have a dictionary with number of votes)
# def insertWV(gameId,tableName,player):
#     with dbConnection(f'{gameId[0]}.db') as cursor:
#         query = f"INSERT INTO '{tableName}' VALUES (?,?,?,?,?,?)"
#         cursor.execute(query, (player['name'],player['id'],player['user'],player['side'],player['role'],player['Votes']))
#
#PL means for playerList table because this has different with another tables
def insertPL(gameId, tableName, player):
    with dbConnection() as cursor:
        query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s)"
        for player in PlayerList:
            cursor.execute(query, (player['id'], player['name'], player['user'], player['link'], int(gameId)))
        # query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s)"
        # cursor.execute(query, (player['id'], player['name'], player['user'], player['link'], int(gameId)))

def insertGP(gameId, tableName, player):
    with dbConnection() as cursor:
        query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (player['id'], player['name'], player['user'],player['side'],player['role'], player['link'],player['votes'], int(gameId)))

def insertMafia(gameId, player):
    with dbConnection() as cursor:
        query= f"INSERT INTO mafias VALUES (%s, %s)"
        cursor.execute(query, (player['id'], int(gameId)))


# #FETCH FUNCs

def fetchall(gameId,tableName):
    with dbConnection() as cursor:
        query = f"SELECT * FROM `{tableName}` WHERE game_id = %s "
        cursor.execute(query,(int(gameId),))
        list= cursor.fetchall()
        print(type(list))
        return list
def createDic(*args):
    list=[]
    for arg in args:
        dict={'id':arg[0],'name':arg[1],'user':arg[2],'side':arg[3],
              'role':arg[4],'link':arg[5],'votes':arg[6],'gameId':arg[7]}
        list.append(dict)
    return list
def fetchPlayer(gameId,tableName,role=None,side=None):
    with dbConnection() as cursor:
        if role is None and side is None:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s"
            cursor.execute(query,(int(gameId),))
            list= cursor.fetchall()
            return list
        elif role is not None:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND role = %s"
            cursor.execute(query,(int(gameId),role))
            player= cursor.fetchone()
            list=createDic(player)
            return list[0]
        elif side is not None:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND side = %s"
            cursor.execute(query,(int(gameId),side))
            players= cursor.fetchall()
            list=createDic(players)
            return list
        elif role and side:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND role = %s AND side = %s"
            cursor.execute(query,(int(gameId),role,side))
            player= cursor.fetchone()
            list=createDic(player)
            return list[0]

def fetchvalue(gameId,tableName,columnName):
    with dbConnection() as cursor:
        query = f"SELECT `{columnName}` FROM `{tableName}` WHERE game_id = %s"
        cursor.execute(query,(int(gameId),))
        value=cursor.fetchone()
        return value
def fetchWithPId(gameId,tableName,playerId):
    with dbConnection() as cursor:
        query=f"SELECT * FROM `{tableName}` WHERE game_id= %s AND player_id= %s"
        cursor.execute(query,(int(gameId),str(playerId),))
        item= cursor.fetchone()
        return item
        # for item in list:
        #     if playerId == item[1]:
        #         return item
        #     else:
        #         pass


def fetchLinks(gameId):
    with dbConnection() as cursor:
        query = f"SELECT link FROM players WHERE game_id = %s"
        cursor.execute(query,(int(gameId),))
        links= cursor.fetchall()
        return links

# #Delete and Drop
#
# def clearTable(dbName,tableName):
#     with dbConnection(f'{dbName}.db') as cursor:
#         cursor.execute(f"DELETE FROM '{tableName}' ")
#
#
#
#
#
# # listTables()
# def delete(dbName,tableName):
#     with dbConnection(f'{dbName}.db') as cursor:
#         cursor.execute(f"DELETE FROM '{tableName}' ")



