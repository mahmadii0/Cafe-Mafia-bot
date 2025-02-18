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

    @bot.message_handler(commands=['helpG'])
    def start(message: Message):
        textFa='''در این سناریو، بازیکنان به سه گروه تقسیم می‌شوند: اکثریت شهروندان، تیم مافیا و یک نقش مستقل. هدف شهروندان، پاکسازی شهر از مافیاهاست، در حالی که مافیاها تلاش می‌کنند تعدادشان با شهروندان برابر شود. نقش مستقل نیز بسته به انتخاب خود، با یکی از دو تیم همکاری می‌کند تا به پیروزی برسد.
بازی در دو فاز شب و روز انجام می‌شود. در شب معارفه، اعضای مافیا یکدیگر را می‌شناسند. در هر روز، بازیکنان فرصت دارند با گفتگو و اتهام‌زنی، مافیاها را شناسایی کرده و با رأی‌گیری از بازی خارج کنند. هر بازیکن می‌تواند در زمان صحبت خود، دیگران را متهم یا از اتهام تبرئه کند، اما اشاره مستقیم یا غیرمستقیم به نقش و توانایی‌های شبانه خود ممنوع است.
در شب، تیم مافیا می‌تواند یکی از توانایی‌های خود را انتخاب کند: شلیک شبانه، استفاده از حس ششم پدرخوانده برای حدس نقش بازیکنان، یا تبدیل یک شهروند ساده به مافیای ساده توسط ساول گودمن. اگر پدرخوانده نقش بازیکنی را به درستی حدس بزند، آن بازیکن حتی با وجود حفاظت دکتر یا داشتن جلیقه، از بازی خارج می‌شود.

نقش‌های کلیدی در این سناریو عبارتند از:
پدرخوانده: رهبر مافیا که از یک شلیک شبانه لئون مصون است و توانایی حس ششم برای حدس نقش‌ها را دارد.
ساول گودمن: مافیایی که می‌تواند یک شهروند ساده را به مافیای ساده تبدیل کند.
ماتادور: هر شب توانایی یکی از بازیکنان را غیرفعال می‌کند.
نوستراداموس: نقش مستقل که در شب معارفه، تعداد مافیاها را در بین سه بازیکن انتخابی خود می‌پرسد و بسته به اطلاعات، تصمیم می‌گیرد با کدام تیم همکاری کند.
دکتر واتسون: هر شب می‌تواند جان یک نفر را نجات دهد و در طول بازی، یک‌بار خود را نجات می‌دهد.
لئون حرفه‌ای: شهروندی که می‌تواند به مافیاها شلیک کند، اما در صورت اشتباه و شلیک به شهروند، خود از بازی خارج می‌شود.
همشهری کین: شهروندی که می‌تواند هویت مافیا را افشا کند.
کنستانتین: توانایی بازگرداندن یک بازیکن اخراجی به بازی را دارد.

در پایان هر روز، بازیکن اخراجی یکی از کارت‌های «حرکت آخر» را به‌صورت تصادفی انتخاب می‌کند که می‌تواند تأثیرات مختلفی بر بازی داشته باشد، مانند «سکوت بره‌ها» که دو بازیکن را برای یک روز ساکت می‌کند، یا «افشای هویت» که نقش بازیکن اخراجی را فاش می‌کند.'''
        textEn = '''In this scenario, players are divided into three groups: the majority are citizens, a mafia team, and an independent role. The citizens aim to eliminate the mafia, while the mafia seeks to match their numbers with the citizens. The independent role can choose to collaborate with either side to secure victory.

The game consists of two phases: night and day.
During the introduction night, the mafia members recognize each other.
Each day, players can discuss, accuse, and vote to eliminate suspected mafia members. However, direct or indirect references to one's own role or abilities are prohibited.
At night, the mafia team can use one of their abilities:

A night kill
The Godfather’s sixth sense, which allows them to guess a player’s role
Saul Goodman’s ability to convert a simple citizen into a simple mafia member
If the Godfather correctly guesses a player's role, that player is eliminated, even if they are protected by the doctor or wearing a vest.

Key Roles in the Scenario:
Godfather: The mafia leader, immune to one night shot from Leon, with the ability to guess roles.
Saul Goodman: A mafia member who can convert a simple citizen into a simple mafia.
Matador: Can disable a player's ability each night.
Nostradamus: An independent role who, during the introduction night, selects three players and learns how many mafias are among them. Based on this information, they decide which team to support.
Dr. Watson: Can save one person’s life each night and has a one-time self-heal.
Leon the Professional: A citizen who can shoot mafia members, but if they mistakenly kill a citizen, they are eliminated.
Citizen Kane: A citizen who can reveal a mafia’s identity.
Constantine: Has the power to revive one eliminated player.

At the end of each day, the eliminated player draws a random "Final Move" card, which can impact the game. For example:
"Silence of the Lambs": Prevents two players from speaking for a day.
"Identity Reveal": Exposes the role of the eliminated player'''
        bot.send_message(message.chat.id,textFa)
        bot.send_message(message.chat.id, textEn)
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




