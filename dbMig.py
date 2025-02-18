import mysql.connector
from contextlib import contextmanager
from constants import connectionDetail,PlayerList
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
        tables=['hand_cuffed','slaughtereds','deads','defences','challenge_turns','challenges','votes','mafias','games_players','players']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM `{table}`")
                print(f"Deleted all rows from `{table}`")  # Optional: for debugging
            except Exception as e:
                print(f"Error deleting from `{table}`: {e}")

def endGame(gameId):
    with dbConnection() as cursor:
        query = f"UPDATE games_info SET status = 0 WHERE game_id = %s"
        cursor.execute(query, (int(gameId),))

def addGame(gameId,chatId,langCode):
    with dbConnection() as cursor:
        cursor.execute(f'''SELECT * FROM games_info WHERE chat_id=%s AND status=1 ''',(str(chatId),))
        existGame=cursor.fetchall()
        if existGame:
            cursor.execute(f'''UPDATE games_info SET status = 0
            WHERE game_id = "{existGame[0][0]}"
            ''')
            return addGame(gameId,chatId,langCode)
        else:
            cursor.execute('''
            INSERT INTO games_info  
            VALUES (%s, %s, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, %s,1,' ')
            ''', (abs(int(gameId)), str(chatId),langCode))
        print("Successfully game added")
def date(gameId,operate):
    with dbConnection() as cursor:
        if operate== "days":
            query=f"UPDATE games_info SET days = days + 1 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))
        elif operate== "nights":
            query=f"UPDATE games_info SET nights = nights + 1 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))
def lenPlayers(gameId,tableNames):
    with dbConnection() as cursor:
        query = f"SELECT COUNT(*) FROM `{tableNames}` WHERE game_id= %s"
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
        cursor.execute(query, (str(chatId),))
        result = cursor.fetchone()
        return result[0]
def trueFalse(gameId,tableName,columnName,operate):
    with dbConnection() as cursor:
        if operate == 'true':
            query = f"UPDATE `{tableName}` SET `{columnName}` = 1 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))
        elif operate == 'false':
            query = f"UPDATE `{tableName}` SET `{columnName}` = 0 WHERE game_id = %s"
            cursor.execute(query, (int(gameId),))

def activeChllnge(gameId,requesterId):
    with dbConnection() as cursor:
        query = f"UPDATE challenges SET status = 1 WHERE game_id = %s AND requester_id = %s"
        cursor.execute(query, (int(gameId),requesterId))
def inqueryR(gameId,value):
    with dbConnection() as cursor:
        query = f"UPDATE games_info SET inquery_request = %s WHERE game_id = %s"
        cursor.execute(query, (int(value),int(gameId),))
def resetVotes(gameId,tableName):
    with dbConnection() as cursor:
        query=f"UPDATE `{tableName}` SET votes = 0 WHERE game_id = %s"
        cursor.execute(query, (int(gameId),))
def leonBullet(gameId):
    with dbConnection() as cursor:
        query=f"UPDATE games_info SET leon_bullet = leon_bullet-1 WHERE game_id = %s"
        cursor.execute(query,(int(gameId),))

def sualPurchese(gameId,playerId,langCode):
    with dbConnection() as cursor:
        if langCode == 'fa':
            query=f"UPDATE `games_players` SET side = %s WHERE game_id = %s AND player_id = %s"
            cursor.execute(query, ('مافیا',int(gameId),str(playerId)),)
            query = f"UPDATE `games_players` SET role = %s WHERE game_id = %s AND player_id = %s"
            cursor.execute(query, ('مافیا ساده', int(gameId), str(playerId)), )
        else:
            query=f"UPDATE `games_players` SET side = %s WHERE game_id = %s AND player_id = %s"
            cursor.execute(query, ('Mafia',int(gameId),str(playerId)),)
            query = f"UPDATE `games_players` SET role = %s WHERE game_id = %s AND player_id = %s"
            cursor.execute(query, ('Simple Mafia', int(gameId), str(playerId)), )
#INSERT FUNCs

def insertPL(gameId, tableName, player):
    with dbConnection() as cursor:
        # query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s)"
        # for player in PlayerList:
        #     cursor.execute(query, (player['id'], player['name'], player['user'], player['link'], int(gameId)))
        query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (player['id'], player['name'], player['user'], player['link'], int(gameId)))
def insertGP(gameId, tableName, player):
    with dbConnection() as cursor:
        query = f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (player['id'], player['name'], player['user'],player['side'],player['role'], player['link'],player['votes'], int(gameId)))

def insertBinaryTable(gameId,tableName,playerId):
    with dbConnection() as cursor:
        query= f"INSERT INTO `{tableName}` VALUES (%s, %s)"
        cursor.execute(query, (playerId,int(gameId)))
def insertChllnge(gameId,challenge):
    with dbConnection() as cursor:
        query= f"INSERT INTO challenges (requester_id, challenger_id, status, game_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (challenge['requesterId'],challenge['challengerId'],0,int(gameId)))

def insertVote(gameId,tableName,playerId,type,numOfVotes=None):
    with dbConnection() as cursor:
        if type == 'inquery' or type == 'city' or type == 'death_draw_selector' or type == 'death_draw_player':
            exist=existence(gameId,tableName,'player_id',playerId)
            if not exist:
                query= f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, 0)"
                cursor.execute(query, (playerId,type,int(gameId)))
                return True
            else:
                return False
        elif type == 'exit':
            exist=existence(gameId,tableName,'player_id',playerId)
            if exist:
                query= f"INSERT INTO `{tableName}` VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (playerId,type,int(gameId),numOfVotes))
                return True
            else:
                return False
        elif type == 'addVote':
                query = f"UPDATE `{tableName}` SET votes = votes + 1 WHERE player_id= %s AND game_id = %s"
                cursor.execute(query, (playerId,int(gameId),))

def insertDeadMan(gameId,player,date):
    with dbConnection() as cursor:
        query= f"INSERT INTO deads VALUES (%s, %s, %s ,%s ,%s ,%s ,%s ,%s)"
        cursor.execute(query, (player[0],player[1],player[2],player[3],player[4],player[5],date, int(gameId)))

def insertSlaughtered(gameId,player,date):
    with dbConnection() as cursor:
        query=f"INSERT INTO `slaughtereds` VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (player[0],player[1],player[3],player[4],int(date), int(gameId),))

def insertShakingHands(gameId,playerId):
    with dbConnection() as cursor:
        query = f"UPDATE games_info SET shaking_hands = %s WHERE game_id = %s"
        cursor.execute(query,(str(playerId),int(gameId),))
#FETCH FUNCs

def fetchall(gameId,tableName=None,challengerId=None,Query=None):
    with dbConnection() as cursor:
        if challengerId:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND challenger_id = %s"
            cursor.execute(query, (int(gameId),challengerId))
            list = cursor.fetchall()
            return list
        elif Query:
            query=Query
            cursor.execute(query,(int(gameId),))
            list=cursor.fetchall()
            return list
        else:
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s "
            cursor.execute(query,(int(gameId),))
            list= cursor.fetchall()
            print(type(list))
            return list
def createDic(*args):
    list=[]
    for arg in args:
        for i in arg:
            dict={'id':i[0],'name':i[1],'user':i[2],'side':i[3],
                'role':i[4],'link':i[5],'votes':i[6],'gameId':i[7]}
            list.append(dict)
    return list
def fetchPlayer(gameId,tableName,role=None,side=None,Type=None,date=None):
    with (dbConnection() as cursor):
        if (role is None and side is None
            and Type is None and date is None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s"
            cursor.execute(query,(int(gameId),))
            players= cursor.fetchall()
            if tableName != 'mafias':
                players=createDic(players)
            return players
        elif (role is not None and side is None
            and Type is None and date is None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND role = %s"
            cursor.execute(query,(int(gameId),role))
            player= cursor.fetchone()
            player={'id':player[0],'name':player[1],'user':player[2],'side':player[3],
                'role':player[4],'link':player[5],'votes':player[6],'gameId':player[7]}
            return player
        elif (role is None and side is not None
            and Type is None and date is None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND side = %s"
            cursor.execute(query,(int(gameId),side))
            players= cursor.fetchall()
            players=createDic(players)
            return players
        elif (role is not None and side is not None
            and Type is None and date is None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND role = %s AND side = %s"
            cursor.execute(query,(int(gameId),role,side))
            player= cursor.fetchone()
            players=createDic(player)
            return players[0]
        elif (role is None and side is None
            and Type is not None and date is None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND type = %s"
            cursor.execute(query,(int(gameId),Type))
            players= cursor.fetchall()
            print(type(players))
            return players
        elif (role is None and side is None
            and Type is None and date is not None):
            query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND date_of_death = %s"
            print(gameId)
            print(date)
            cursor.execute(query,(int(gameId),int(date),))
            players= cursor.fetchall()
            print(type(players))
            return players

def fetchvalue(gameId,tableName,columnName,playerId=None):
    with dbConnection() as cursor:
        if not playerId:
            query = f"SELECT `{columnName}` FROM `{tableName}` WHERE game_id = %s"
            cursor.execute(query,(int(gameId),))
            value=cursor.fetchone()
            value=value[0]
            return value
        else:
            query = f"SELECT `{columnName}` FROM `{tableName}` WHERE game_id = %s AND player_id= %s"
            cursor.execute(query,(int(gameId),playerId))
            value=cursor.fetchone()
            value=value[0]
            return value
def fetchRow(gameId,tableName,columnName,value):
    with dbConnection() as cursor:
        query = f"SELECT * FROM `{tableName}` WHERE game_id = %s AND `{columnName}` = %s"
        cursor.execute(query,(int(gameId),value))
        row= cursor.fetchall()
        return row
def fetchWithPId(gameId,tableName,playerId):
    with dbConnection() as cursor:
        #I used this approach because changing gameId to a None object would require changing all its usages!
        if gameId != 0:
            query=f"SELECT * FROM `{tableName}` WHERE game_id= %s AND player_id= %s"
            cursor.execute(query,(int(gameId),str(playerId),))
            item= cursor.fetchone()
            return item
        else:
            query=f"SELECT * FROM `{tableName}` WHERE player_id= %s"
            cursor.execute(query,(str(playerId),))
            item= cursor.fetchone()
            return item
def fetchWithFK(gameId,tableName,FK,FTableName,condition,value):
    with dbConnection() as cursor:
        query=f"""SELECT {tableName}.{FK}
        FROM `{tableName}`
        JOIN `{FTableName}` ON {tableName}.{FK} = {FTableName}.{FK}
        WHERE {FTableName}.{condition} = %s AND {FTableName}.game_id= %s"""
        cursor.execute(query,(value,int(gameId),))
        players=cursor.fetchall()
        list=createDic(players)
        return list

#EXIST FUNC

def existence(gameId,tableName,columnName,value):
    with dbConnection() as cursor:
        query= f"SELECT EXISTS (SELECT 1 FROM `{tableName}` WHERE game_id = %s AND `{columnName}` = %s)"
        cursor.execute(query,(int(gameId),value))
        result = cursor.fetchone()[0]
        return result

def fetchLinks(gameId,tableName,playerIds=None):
    with dbConnection() as cursor:
        if playerIds:
            links=[]
            for playerId in playerIds:
                query = f"SELECT link FROM `{tableName}` WHERE player_id = %s AND game_id = %s"
                cursor.execute(query,(playerId,int(gameId),))
                link= cursor.fetchone()
                links.append(link[0])
            return links
        else:
            query = f"SELECT link FROM `{tableName}` WHERE game_id = %s"
            cursor.execute(query,(int(gameId),))
            links= cursor.fetchall()
            return links

# #Delete and Drop
#
def deleteRows(tableName,columnName1,value1,columnName2=None,value2=None):
    with dbConnection() as cursor:
        if columnName2 and value2:
            query=f"DELETE FROM `{tableName}` WHERE {columnName1} = %s AND `{columnName2}` = %s"
            cursor.execute(query,(value1,value2,))
        else:
            query=f"DELETE FROM `{tableName}` WHERE {columnName1} = %s"
            cursor.execute(query,(value1,))




