import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from redis import *
import gameLogic
from constants import BotUserIds, PlayerList
from dbMig import getGameId
from gameLogic import *

callList=[]


#delete messages that send to chats
def Delete_message(bot,call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

#return gameId for all handlers
def gId(call=None,chatId=None):
    if call:
        chatId = call.message.chat.id
        gameId = getGameId(chatId)
        if gameId:
            return gameId
        else:
            player=fetchWithPId(0,'games_players',str(call.from_user.id))
            gameId = player[7]
            return gameId
    if chatId:
        gameId=getGameId(chatId)
        return gameId



def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        if message.chat.type == "private":
            userId = message.from_user.id
            if userId not in BotUserIds:
                BotUserIds.append(userId)
            bot.send_message(
                message.chat.id,
                "سلام به ربات ما خوش آمدید.\nاکنون ارسال پیام و پاسخ برای شما باز شد"
            )

    @bot.message_handler(commands=['privacy'])
    def start(message):
        if message.chat.type == "private":
            bot.send_message(
                message.chat.id,
                "و البته اسم قشنگ تون!\nما تنها از آیدی شما برای تگ کردن ها برای  جریان بازی استفاده می کنیم!"
            )

    @bot.message_handler(regexp='شروع مافیا')
    def start_game_handler(message):
        global instance
        if message.chat.type != "private":
            gameId =0
            def Instance():
                with lock:
                    newId = random.randint(10 ** 7, 10 ** 8 - 1)
                    if newId not in gameIds:
                        gameIds.append(newId)
                        return newId
                    else:
                        return instance()
            gameId=Instance()
            deleteTables()
            startG(bot, message,gameId)
        else:
            bot.send_message(message.chat.id,"شما باید از این دستور برای شروع بازی در گروه استفاده کنید")


    @bot.message_handler(regexp='اتمام کلام')
    def stopTalk_handler(message):
        gameId = gId(chatId=message.chat.id)
        trueFalse(gameId, 'games_info', 'stop_talk', 'true')
        startWait(gameId)


    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        def messageOfAccessing(bot, call):
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='شما نمی توانید انتخاب کنید'
                                      , show_alert=True)

        def messageOfSelecting(bot, call):
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='بازیکن انتخاب شد!'
                                      , show_alert=True)

        gameId = gId(call=call)
        if call.data == "Add":
            AddPlayer(bot, call,gameId)
        elif call.data == "FinalStart":
            FinalStart(bot, call,gameId)
        elif call.data == "add_challenge":
            challenger=fetchPlayer(gameId,'challenge_turns')
            if challenger:
                AddChallenge(bot,call,challenger[0][0],gameId)
        elif call.data == "yes_Sherlock":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Sherlock(bot,call,gameId)
        elif call.data == "no_Sherlock":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه شرلوک جان')
        elif call.data == "slaughter_godFather":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GodfatherSlaughter(bot,call,gameId)
        elif call.data == "gunShot_godFather":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "yes_matador":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Matador(bot,call,gameId)
        elif call.data == "no_matador":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه ماتادور زرنگ')
        elif call.data == "yes_Gunshot_matador":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_Gunshot_matador":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'اوکی ماتادور از این پس بگذریم')
        elif call.data == "yes_sual":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Sual(bot,call,gameId)
        elif call.data == "no_sual":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه ساول گودمن جان')
        elif call.data == "yes_Gunshot_sual":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_Gunshot_sual":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'اوکی ساول از این پس بگذریم')
        elif call.data == "yes_simpleMafia":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_simpleMafia":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه مافیای من')
        elif call.data == "yes_doctor":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Doctor(bot,call,gameId)
        elif call.data == "no_doctor":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه دکی جان')
        elif call.data == "yes_leon":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Leon(bot,call,gameId)
        elif call.data == "no_leon":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه لئون حرفه ای')
        elif call.data == "yes_kein":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Kein(bot,call,gameId)
        elif call.data == "no_kein":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه شهروند کین')
        elif call.data == "yes_constantine":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Constantine(bot,call,gameId)
        elif call.data == "no_constantine":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه کنستانتین الهه تولد')
        elif call.data == f'Yes_forInquiry':
            exist=existence(gameId,'games_info','pick',1)
            if exist:
                pass
            else:
                trueFalse(gameId,'games_info','pick','true')
            VerifyInquiryRequest(bot, call,gameId)

        else:
            for game in gameIds:
                operation=None
                gameId=None
                playerId = None
                data= call.data.split('_')
                if len(data) == 3:
                    operation,gameId,playerId=data
                existPlayer = fetchRow(game, 'games_players',
                                       'player_id', str(call.from_user.id))

                if operation == 'challenge':
                    exist=fetchRow(game,'challenges','challenger_id',str(call.from_user.id))
                    if exist:
                        #playerId = requester
                        activeChallenge(bot,call,playerId,gameId)
                    else:
                        messageOfAccessing(bot,call)

                elif operation == 'vote':
                    if existPlayer:
                            CountingVotes(bot,call,playerId,gameId)
                    else:
                        messageOfAccessing(bot,call)

                elif operation == 'hand':
                    if existPlayer:
                        trusted_citizen=fetchPlayer(gameId,'votes',Type='trusted_citizen')
                        if trusted_citizen[0][0] == str(call.from_user.id):
                            insertShakingHands(gameId,playerId)

                elif operation == 'blue':
                    if existPlayer:
                        selector=fetchPlayer(gameId,'votes',Type='death_draw_selector')
                        if selector[0][0] == str(call.from_user.id):
                            blueCart(bot,call,gameId)
                        else:
                            messageOfAccessing(bot, call)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'red':
                    if existPlayer:
                        selector = fetchPlayer(gameId, 'votes', Type='death_draw')
                        if selector[0][0] == str(call.from_user.id):
                            redCart(bot, call, gameId)
                        else:
                            messageOfAccessing(bot, call)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'sherlock':
                    if existPlayer:
                        player=fetchWithPId(gameId,'games_players',playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifySherlockSlaughter(bot,call,player,gameId)
                    else:
                        messageOfAccessing(bot, call)
                elif operation == 'godSluaght':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifyGodfatherSlaughter(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'Shot':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifyGunShot(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'matador':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifyMatador(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'sual':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifySual(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'doctor':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call)
                        Delete_message(bot, call)
                        VerifyDoctor(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'leon':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot, call)
                        Delete_message(bot, call)
                        VerifyGunShot(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'kein':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot, call)
                        Delete_message(bot, call)
                        VerifyKein(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)

                elif operation == 'constantine':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot, call)
                        Delete_message(bot, call)
                        VerifyConstantine(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot, call)




