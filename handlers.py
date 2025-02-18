from gameLogic import *
from telebot.types import Message

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



def register_handlers(bot: telebot):
    @bot.message_handler(commands=['start'])
    def start(message: Message):
        if message.chat.type == "private":
            userId = message.from_user.id
            exist=[user for user in BotUserIds if user['id'] == str(userId)]
            if not exist:
                bot.send_message(message.chat.id, 'لطفا یک نام برای فرآیند بازی مافیا ارسال کنید (این نام دائمی می‌ماند):')
                bot.register_next_step_handler(message, nameInput, bot)
            else:
                bot.send_message(message.chat.id, 'شما مجوز بازی را دارید و نیازی به ثبت نام نیست !')


    @bot.message_handler(commands=['privacy'])
    def start(message):
        if message.chat.type == "private":
            bot.send_message(
                message.chat.id,
                "We only use your ID for tagging for the game stream! \n And of course your beautiful name!"
            )

    @bot.message_handler(regexp=r'شروع مافیا|start mafia')
    def start_game_handler(message):
        global instance
        if message.chat.type != "private":
            langCode=''
            if message.text == 'شروع مافیا':
                langCode='fa'
            else:
                langCode='en'
            gameId =0
            def Instance():
                with lock:
                    newId = random.randint(10 ** 7, 10 ** 8 - 1)
                    exist = [game for game in gameIds if game['id'] == str(newId)]
                    if not exist:
                        game={'id':str(newId),'langCode':langCode}
                        gameIds.append(game)
                        return newId
                    else:
                        return instance()
            gameId=Instance()
            deleteTables()
            startG(bot, message,gameId,langCode)
        else:
            bot.send_message(message.chat.id,"You must use this command to start playing in a group")


    @bot.message_handler(regexp='اتمام کلام|End speech')
    def stopTalk_handler(message):
        gameId = gId(chatId=message.chat.id)
        trueFalse(gameId, 'games_info', 'stop_talk', 'true')
        startWait(gameId)


    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        def messageOfAccessing(bot, call,langCode):
            if langCode == 'fa':
                bot.answer_callback_query(callback_query_id=call.id
                                      , text='شما نمی توانید انتخاب کنید'
                                      , show_alert=True)
            else:
                bot.answer_callback_query(callback_query_id=call.id
                                          , text="You can't choose."
                                          , show_alert=True)

        def messageOfSelecting(bot, call,langCode):
            if langCode == 'fa':
                bot.answer_callback_query(callback_query_id=call.id
                                      , text='بازیکن انتخاب شد!'
                                      , show_alert=True)
            else:
                bot.answer_callback_query(callback_query_id=call.id
                                          , text="The player has been selected!"
                                          , show_alert=True)

        gameId = gId(call=call)
        langCode = getLangCode(gameId)
        _ = set_language(langCode)
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
            bot.send_message(call.from_user.id,_('Ok Sherlock!'))
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
            bot.send_message(call.from_user.id,_('Ok smart Matador'))
        elif call.data == "yes_Gunshot_matador":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_Gunshot_matador":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Matador! I got it!'))
        elif call.data == "yes_sual":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Sual(bot,call,gameId)
        elif call.data == "no_sual":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Sual Goodman'))
        elif call.data == "yes_Gunshot_sual":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_Gunshot_sual":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Sual! lets pass it'))
        elif call.data == "yes_simpleMafia":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            GunShot(bot,call,gameId)
        elif call.data == "no_simpleMafia":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('ok my mafia😎'))
        elif call.data == "yes_doctor":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Doctor(bot,call,gameId)
        elif call.data == "no_doctor":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Doctor!'))
        elif call.data == "yes_leon":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Leon(bot,call,gameId)
        elif call.data == "no_leon":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Leon'))
        elif call.data == "yes_kein":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Kein(bot,call,gameId)
        elif call.data == "no_kein":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Kein'))
        elif call.data == "yes_constantine":
            trueFalse(gameId, 'games_info', 'pick', 'true')
            Delete_message(bot, call)
            Constantine(bot,call,gameId)
        elif call.data == "no_constantine":
            trueFalse(gameId,'games_info','pick','true')
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,_('Ok Constantine, Goddess of birth'))
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
                existPlayer = fetchRow(gameId, 'games_players',
                                       'player_id', str(call.from_user.id))

                if operation == 'challenge':
                    exist=fetchRow(game,'challenges','challenger_id',str(call.from_user.id))
                    if exist:
                        #playerId = requester
                        activeChallenge(bot,call,playerId,gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'vote':
                    if existPlayer:
                            CountingVotes(bot,call,playerId,gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

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
                            messageOfAccessing(bot,call,langCode)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'red':
                    if existPlayer:
                        selector = fetchPlayer(gameId, 'votes', Type='death_draw')
                        if selector[0][0] == str(call.from_user.id):
                            redCart(bot, call, gameId)
                        else:
                            messageOfAccessing(bot,call,langCode)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'sherlock':
                    if existPlayer:
                        player=fetchWithPId(gameId,'games_players',playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifySherlockSlaughter(bot,call,player,gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)
                elif operation == 'godSluaght':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyGodfatherSlaughter(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'Shot':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyGunShot(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'matador':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyMatador(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'sual':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifySual(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'doctor':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyDoctor(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'leon':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyGunShot(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'kein':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyKein(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)

                elif operation == 'constantine':
                    if existPlayer:
                        player = fetchWithPId(gameId, 'games_players', playerId)
                        messageOfSelecting(bot,call,langCode)
                        Delete_message(bot, call)
                        VerifyConstantine(bot, call, player, gameId)
                    else:
                        messageOfAccessing(bot,call,langCode)




