import random
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from constants import Rolelist,Rolelist_en,Rolelist_fa, BotUserIds
import threading
from dbMig import *
import gettext

lock = threading.Lock()

#Lists
gameIds=[]
Voters=[]
chatEvents = {}
languages = {
    "en": "locales/en/LC_MESSAGES/messages",
    "fa": "locales/fa/LC_MESSAGES/messages",
}
_=None

#Allow and Restrict Chating
allowChatMember = telebot.types.ChatPermissions(can_send_messages=True)
restrictChatMember = telebot.types.ChatPermissions(can_send_messages=False)

def set_language(langCode):
    if str(langCode) not in languages:
        langCode = "en"
    translation = gettext.translation("messages", localedir="locales", languages=[langCode])
    translation.install()
    return translation.gettext

def getLangCode(gameId):
    langCode=[game for game in gameIds if str(game['id']) == str(gameId)]
    langCode = langCode[0]
    return langCode['langCode']

def nameInput(message: Message, bot: telebot):
    userId = message.from_user.id
    name = message.text.strip()

    if len(name) < 100:
        user = {'name': name, 'id': str(userId)}
        BotUserIds.append(user)
        bot.send_message(message.chat.id, "ثبت‌نام شما با موفقیت انجام شد! اکنون می‌توانید بازی کنید.")
    else:
        bot.send_message(message.chat.id, 'نام شما باید کمتر از 100 کاراکتر باشد! لطفا دوباره یک نام ارسال کنید:')
        bot.register_next_step_handler(message, nameInput, bot)

def startG(bot,message,gameId,langCode):
    addGame(gameId,message.chat.id,langCode)
    _ = set_language(langCode)
    markup = telebot.types.InlineKeyboardMarkup()
    AddBtn = telebot.types.InlineKeyboardButton(_("I'm in✋"), callback_data='Add')
    FinalStart = InlineKeyboardButton(_("Final start👁️‍🗨️"), callback_data='FinalStart')
    markup.add(AddBtn)
    markup.add(FinalStart)
    bot.send_message(message.chat.id, _(f"""Wow! What an awesome group of friends gathering to play Mafia! 😎  

To join the game, first, you need to start the bot and then click on the "I am in" button so we can play this exciting scenario!  

Scenario: The Godfather 3
Number of Citizens** (Doctor, Leon, Kane, Constantine, Regular): 7 
Number of Mafia** (Godfather, Matador, Saul Goodman): 3
Independent Role** (Sherlock): 1

If you don’t know the game or are unfamiliar with it, use the command `/helpG` for an explanation.


    """), reply_markup=markup)


def AddPlayer(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    with lock:
        lenP = lenPlayers(gameId,'players')
    if int(lenP) < 11 :
        exist = [user for user in BotUserIds if user['id'] == str(call.from_user.id)]
        if exist:
            exist=exist[0]
            len=checking(str(call.from_user.id))
            if len == 0:
                playerId=str(call.from_user.id)
                playerUser = call.from_user.username
                playerName = exist['name']
                playerLink = f'<a href="tg://user?id={call.from_user.id}">{playerName}</a>'
                player={'name':playerName,'id':playerId,'user':playerUser,'link':playerLink}
                insertPL(gameId,'players',player)
                chatMember = bot.get_chat_member(call.message.chat.id, call.from_user.id)
                isAdmin=chatMember.status in ["administrator", "creator"]
                if isAdmin:
                    insertBinaryTable(gameId,'admins',playerId)
                links=fetchLinks(gameId,'players')
                text = _("""Wow! What an awesome group of friends gathering to play Mafia! 😎  

To join the game, first, you need to start the bot and then click on the "I am in" button so we can play this exciting scenario!  

Scenario: The Godfather 3
Number of Citizens** (Doctor, Leon, Kane, Constantine, Regular): 7 
Number of Mafia** (Godfather, Matador, Saul Goodman): 3
Independent Role** (Sherlock): 1

If you don’t know the game or are unfamiliar with it, use the command `/helpG` for an explanation.

Player List:
                
        {}""").format(links)


                markup = InlineKeyboardMarkup()
                AddBtn = telebot.types.InlineKeyboardButton(_("I'm in✋"), callback_data='Add')
                FinalStart = telebot.types.InlineKeyboardButton(_("Final start👁️‍🗨️"), callback_data='FinalStart')
                markup.add(AddBtn)
                markup.add(FinalStart)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=markup, parse_mode='HTML')
            else:
                bot.answer_callback_query(callback_query_id=call.id
                                          ,text=_("Dear friend, you'r in the game! Please wait for it to start")
                                                , show_alert = True)
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                        ,text=_("Dear friend, you haven't start the bot")
                                        ,show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                , text=_("You can't join to game!")
                                , show_alert=True)

def FinalStart(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    UserId=call.from_user.id
    ChatId=call.message.chat.id
    ChatMember=bot.get_chat_member(chat_id=ChatId,user_id=UserId)
    if ChatMember.status in ['administrator', 'creator']:
        with lock:
            lenP = lenPlayers(gameId,'players')
        if int(lenP) == 11:
            bot.answer_callback_query(callback_query_id=call.id
                                        , text=_('GAME is started!')
                                        , show_alert=True)
            bot.delete_message(ChatId,call.message.message_id)
            Operations(bot,ChatId,gameId,langCode)
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                          ,text=_("The required number of players has not been reached!")
                                          ,show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                      , text=_("You don't have premission to start the game!"),
                                      show_alert=True)

def Operations(bot, chatId,gameId,langCode):
    _ = set_language(langCode)
    playerList=fetchall(gameId,'players')
    if langCode == 'fa':
        randomRole = random.sample(Rolelist_fa, len(playerList))
    else:
        randomRole = random.sample(Rolelist_en, len(playerList))
    for player, role in zip(playerList, randomRole):
        gamePlayer = { 'id': player[0],'name': player[1],
                    'user': player[2],'link': player[3],
                       'side': '', 'role': role , 'votes':0}
        if (gamePlayer['role'] == _('Godfather')
                or gamePlayer['role'] == _('Matador')
                or gamePlayer['role'] == _('Sual Goodman')):
            gamePlayer['side'] = _('Mafia')
            insertBinaryTable(gameId,'mafias',gamePlayer['id'])
        elif gamePlayer['role'] == _('Sherlock'):
            gamePlayer['side'] = _('Sherlock')
        else:
            gamePlayer['side'] = _('Citizen')
        insertGP(gameId,'games_players',gamePlayer)

    blindFunc(bot,chatId,gameId,langCode)

def blindFunc(bot, chatId,gameId,langCode):
    _ = set_language(langCode)
    pRoleList = fetchall(gameId, 'games_players')
    for P in pRoleList:
        id = P[0]
        admins=fetchall(gameId,'admins')
        for admin in admins:
            if admin[0] != id:
                bot.restrict_chat_member(chatId, id, permissions=restrictChatMember)


    for P in pRoleList:
        role = P[4]
        bot.send_message(P[0], f"{_("Your role dear friend is:")} {role}")
    bot.send_message(chatId, _("""Welcome to the game, everyone😎
    I'm delighted to have an enjoyable game with you all🪶
    Your roles have been sent to you privately by me. Now, we will begin the Blind Day in 5 seconds.If you have finished speaking, let me know by typing the word End speech"""))
    Chat(bot,chatId,pRoleList,gameId,langCode)
    bot.send_message(chatId,_("Night has begun... The city falls asleep...🌙"))
    trueFalse(gameId,'games_info','challenge','true')
    Night(bot,chatId,gameId,langCode)

chatLock = threading.Lock()
def startWait(gameId):
    with chatLock:
        event = threading.Event()
        chatEvents[str(gameId)] = event

def Wait(seconds, gameId):
    try:
        endTime = time.time() + seconds
        while time.time() < endTime:
            if str(gameId) in chatEvents:
                print(f"Timer stopped for chat {gameId}")
                return
            time.sleep(0.1)
    finally:
        with chatLock:
            if str(gameId) in chatEvents:
                del chatEvents[str(gameId)]

def InquiryRequest(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    numOfIRequest=fetchvalue(gameId,'games_info',"inquery_request")
    if numOfIRequest>0:
        trueFalse(gameId, 'games_info', 'pick', 'false')
        len=lenPlayers(gameId,'games_players')
        HalfNum = int(len) // 2
        markup = InlineKeyboardMarkup()
        yesBtn = InlineKeyboardButton(_('Yes'), callback_data=f'Yes_forInquiry')
        markup.add(yesBtn)
        message = bot.send_message(chatId, _(f'🔴Do you want to make an inquiry?'), reply_markup=markup)
        Wait(20,gameId)
        pick=fetchvalue(gameId,'games_info','pick')
        if pick == False:
            bot.delete_message(chatId, message.message_id)
        else:
            len=lenPlayers(gameId,'votes')
            if int(len) >= HalfNum:
                numOfIRequest-=1
                inqueryR(gameId,numOfIRequest)
                mafia=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side',_('Mafia'))
                citizen=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side',_('Citizen'))
                sherlock=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side',_('Sherlock'))
                lenM=0
                lenC=0
                if mafia and citizen:
                    lenM= len(mafia)
                    lenC = len(citizen)
                if mafia is None:
                    lenC=len(citizen)
                if citizen is None:
                    lenM=len(mafia)

                bot.send_message(chatId,f'{_("From your game,")} {lenC} {_("Citizen and")} {lenM} {_("Mafia ,went out!")}')
                if sherlock:
                    bot.send_message(chatId,_("And also, Word just came in that Sherlock has left the game!"))
            else:
                bot.send_message(chatId,_("Alright, so no inquiry will be made!"))
            resetVotes(gameId,'games_info')
            deleteRows('votes','game_id',gameId,'type','inquery')
            trueFalse(gameId,'games_info','pick','false')

    else:
        bot.send_message(chatId,_('Well, The inquiries are all finished now...'))
def VerifyInquiryRequest(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    exist=existence(gameId,'games_players','player_id',str(call.from_user.id))
    if exist:
        status=insertVote(gameId,'votes',str(call.from_user.id),'inquery')
        if status:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text=_('Your vote has been registered')
                                      , show_alert=True)
            markup = InlineKeyboardMarkup()
            yesBtn = InlineKeyboardButton(_('Yes'), callback_data=f'Yes_forInquiry')
            markup.add(yesBtn)
            query =f"""SELECT games_players.link
            FROM `votes`
            JOIN `games_players` ON votes.player_id = games_players.player_id
            WHERE  votes.game_id= %s"""
            links = fetchall(gameId, Query=query)
            text = f'''{_("""🔴Do you want to make an inquiry?

            List of requesters:""")}
            {links}'''
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=markup, parse_mode='HTML')
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text=_("Your vote has already been registered")
                                      , show_alert=True)


    else:
        bot.answer_callback_query(callback_query_id=call.id
                                        , text=_("You cannot make a request")
                                        , show_alert=True)

def Challenge(p, bot, chatId,gameId,langCode):
    _ = set_language(langCode)
    insertBinaryTable(gameId,'challenge_turns',p[0])
    markup = InlineKeyboardMarkup()
    add_btn = InlineKeyboardButton(_("I want✋"), callback_data=f'add_challenge')
    markup.add(add_btn)
    bot.send_message(chatId, f'''{_("🟠 Who wants a challenge from")} {p[1]}{_('?')} ''', reply_markup=markup)
    Wait(5,gameId)

def AddChallenge(bot, call,challenger,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    exist=existence(gameId,'games_players','player_id',str(call.from_user.id))
    if exist:
        requesterExist=existence(gameId,'challenges','requester_id',str(call.from_user.id))
        if not requesterExist:
            challenge={'requesterId':str(call.from_user.id),'challengerId':challenger}
            insertChllnge(gameId,challenge)
            markup = InlineKeyboardMarkup()
            addBtn = InlineKeyboardButton(_("I want✋"), callback_data='add_challenge')
            markup.add(addBtn)
            challenges=fetchall(gameId,'challenges',str(challenger))
            for challenge in challenges:
                requester=fetchWithPId(gameId,'games_players',challenge[1])
                name_btn = InlineKeyboardButton(f'{requester[1]}',
                                                callback_data=f'challenge_{gameId}_{requester[0]}')
                markup.add(name_btn)
            query = f"""SELECT games_players.link
            FROM `challenges`
            JOIN `games_players` ON challenges.requester_id = games_players.player_id
            WHERE  challenges.game_id= %s"""
            links = fetchall(gameId, Query=query)
            challenger=fetchWithPId(gameId,'games_players',challenger)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'''{_("🟠 Who wants a challenge from")} {challenger[1]}{_("?")}
                                                            
                                    {_("List of people who are requesting a challenge from you:")}
                                    {links}                              
                                  ''', reply_markup=markup,parse_mode='HTML')
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text=_("You have already made a request")
                                      , show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                        , text=_("You cannot make a request")
                                        , show_alert=True)

def activeChallenge(bot, call,requesterId,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    activeChllnge(gameId,str(requesterId))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, _("The challenge has been selected!"))

def ApplyChallenge(bot, chatId,player,gameId,langCode):
    _ = set_language(langCode)
    challenge=fetchRow(gameId,'challenges','status',1)
    if not challenge:
        bot.send_message(chatId, _("It seems like we don't have any challenges after all"))
    else:
        admins = fetchall(gameId, 'admins')
        for admin in admins:
            if admin[0] != challenge[1]:
                bot.restrict_chat_member(chatId, challenge[1], permissions=allowChatMember)
        requester=fetchWithPId(gameId,'games_players',challenge[1])
        bot.send_message(chatId, f'{_("it is turn to challenge which given to")}  {requester[1]}')
        trueFalse(gameId,'games_info','stop_talk','false')
        Wait(30,gameId)
        admins = fetchall(gameId, 'admins')
        for admin in admins:
            if admin[0] != challenge[1]:
                bot.restrict_chat_member(chatId, challenge[1], permissions=restrictChatMember)
        bot.send_message(chatId, _(f'Dear friend, your challenge time is over!'))
        deleteRows('challenges','game_id',int(gameId))
        trueFalse(gameId, 'games_info', 'stop_talk', 'false')
    deleteRows('challenge_turns', 'challenger_id',
               str(player[0]), 'game_id', int(gameId))
    time.sleep(1.5)


def Chat(bot,chatId,pRoleList,gameId,langCode):
    _ = set_language(langCode)
    time.sleep(5)
    challenge=bool(existence(gameId,'games_info','challenge',1))
    for P in pRoleList:
        id = P[0]
        admins = fetchall(gameId, 'admins')
        for admin in admins:
            if admin[0] != id:
                bot.restrict_chat_member(chatId, P[0], permissions=allowChatMember)
        if challenge:
            Challenge(P,bot,chatId,gameId,langCode)
        bot.send_message(chatId, f'{_("Dear friend")} {P[1]}, {_("Please speak:")}')
        trueFalse(gameId,'games_info','stop_talk','false')
        Wait(50,gameId)
        admins = fetchall(gameId, 'admins')
        for admin in admins:
            if admin[0] != id:
                bot.restrict_chat_member(chatId, id, permissions=restrictChatMember)
        bot.send_message(chatId, _(f'Dear friend, your chatting time is over!'))
        trueFalse(gameId,'games_info','stop_talk','false')
        time.sleep(2)
        if challenge:
            ApplyChallenge(bot,chatId,P,gameId,langCode)

def mafiaChat(bot,mafias,langCode):
    _ = set_language(langCode)
    class ChatState:
        active = True

    chatDuration = 70
    mafiaMessages = {}
    @bot.message_handler(func=lambda message: ChatState.active)
    def handleMafiaMessages(message):
        sender=[]
        for mafia in mafias:
            if mafia['id'] == str(message.from_user.id):
                sender.append(mafia)
                sender=sender[0]
            if mafia['id'] not in mafiaMessages:
                mafiaMessages[mafia['id']] = []
                mafiaMessages[mafia['id']].append(message.text)

        for mafia in mafias:
            if mafia['id'] != sender['id']:
                bot.send_message(mafia['id'],f"{_("Message from")} {sender['name']}: {message.text}")

    time.sleep(chatDuration)
    ChatState.active = False
    for mafia in mafias:
            bot.send_message(mafia['id'], _("🔴The Mafia chat's time is up"))

def TrustDecision(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    trustedCitizen=[]
    voters=[]
    names=[]
    players=fetchPlayer(gameId,'games_players')
    bot.send_message(chatId,_(f'''Alright, dear friends, we have reached the 'Trust Decision' stage (Key Ace),
     and initially,you can freely talk for three minutes'''))
    for player in players:
        names.append(player['name'])
        bot.restrict_chat_member(chatId, player['id'], permissions=allowChatMember)
    Wait(181, gameId)
    bot.send_message(chatId, _(f"Alright, the talking time is over, and now it's time for all three of you to come into my private messages (PV) and write who you trust as the citizen!"))
    for player in players:
        bot.send_message(player['id'],_("Tell me, who do you trust as the citizen?"))
    @bot.message_handler(func=lambda message: names )
    def selectingCitizen(message):
        if message.chat.type == "private" and str(message.chat.id) not in voters:
            for player in players:
                if message.text == player['name']:
                    with lock:
                        player['votes'] = int(player['votes']) + 1
                        voters.append(str(message.chat.id))
                        bot.send_message(message.chat.id, _("Your opinion has been received!"))
    Wait(15,gameId)
    for player in players:
        if player['votes'] > 1:
            trustedCitizen.append(player)
            trustedCitizen=trustedCitizen[0]
    if trustedCitizen is None:
        trustedCitizen = players[0]
    insertVote(gameId, 'votes',trustedCitizen['id'], 'trusted_citizen')
    bot.send_message(chatId,f"""{_("According to the result,")} {trustedCitizen['name']} {_("""have been chosen as the citizen.
    From now on, you have 30 seconds to decide who to shake hands with!""")}""")
    markup= InlineKeyboardMarkup()
    for player in players:
        if player['id'] != trustedCitizen['id']:
            voteBtn = InlineKeyboardButton(f'{player['name']}', callback_data=f'hand_{gameId}_{player['id']}')
            markup.add(voteBtn)
    bot.send_message(chatId,_(f"Which one of your friends are you choosing to shake hands with?"),
                     reply_markup=markup)
    Wait(30, gameId)
    shakingHands=fetchvalue(gameId,'games_info','shaking_hands')
    if shakingHands:
        player=fetchWithPId(gameId,'games_players',shakingHands)
        if player['side'] == _('Mafia'):
            bot.send_message(_("With your choice, the Mafia won the game, and the town lost! 🔥🔥"))
            Ending(bot,chatId,gameId)
        else:
            bot.send_message(_("With your choice, the Mafia lost the game, and the town won! 🔥🔥"))
            Ending(bot, chatId, gameId)
    else:
        bot.send_message(_("Because you didn't make a choice, the Mafia won the game, and the town lost! 🔥🔥"))
        Ending(bot, chatId, gameId)


votingTime=12
def Voting(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    players=fetchPlayer(gameId,'games_players')
    HalfNum=len(players)//2
    for P in players:
        markup= InlineKeyboardMarkup()
        voteBtn= InlineKeyboardButton(_("I vote"),callback_data=f'vote_{gameId}_{P['id']}')
        markup.add(voteBtn)
        message=bot.send_message(chatId,f"{_("🟠 We vote for")} {P['name']}",reply_markup=markup)
        Wait(votingTime,gameId)
        bot.delete_message(chatId,message.message_id)
        votes=fetchvalue(gameId,'games_players','votes',P['id'])
        if votes>=HalfNum:
            status=insertVote(gameId,'votes',P['id'],'city')
            if status:
                bot.send_message(chatId,f'{_("So")} {P['name']} {_("goes to the defense")}')
        clearVoters(gameId)
    resetVotes(gameId, 'games_players')
    Defence(bot,chatId,HalfNum,gameId,langCode)

def clearVoters(gameId):
    global Voters
    for voter in reversed(Voters):
        if voter['gameId'] == str(gameId):
            Voters.remove(voter)



def CountingVotes(bot,call,playerId,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    global Voters
    voter=[voter for voter in Voters if str(call.from_user.id) == voter['playerId']]

    if len(voter) == 0:
        voter = {'playerId': str(call.from_user.id), 'gameId': str(gameId)}
        player=fetchWithPId(gameId,'games_players',playerId)
        playerIds=set()
        with lock:
            Voters.append(voter)
            insertVote(gameId,'games_players',playerId,'addVote')
            for voter in Voters:
                if voter['gameId'] == gameId:
                    playerIds.add(voter['playerId'])

        links = fetchLinks(gameId, 'games_players',playerIds)
        text = f'''\n {_("🟠 We vote for")} {player[1]} 
        {_("List of voters:")}
        {links}'''
        markup = InlineKeyboardMarkup()
        voteBtn = InlineKeyboardButton(_("I vote"), callback_data=f'vote_{gameId}_{player[0]}')
        markup.add(voteBtn)
        bot.answer_callback_query(callback_query_id=call.id
                                  , text=_("Your vote was registered for him/her!")
                                  , show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup, parse_mode='HTML')
        playerIds.clear()
        links.clear()
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                  , text=_("You have already voted once!")
                                  , show_alert=True)


def Defence(bot,chatId,HalfNum,gameId,langCode):
    _ = set_language(langCode)
    defenders=[]
    list=fetchPlayer(gameId,'votes',Type='city')
    if list:
        for player in list:
            p = {'id': player[0], 'type': player[1], 'gameId': player[2]}
            defenders.append(p)
        if int(len(defenders))>0:
            for P in defenders:
                admins = fetchall(gameId, 'admins')
                for admin in admins:
                    if admin[0] != P['id']:
                        bot.restrict_chat_member(chatId, P['id'], permissions=allowChatMember)
                playerName = fetchvalue(gameId, 'games_players', 'name', P['id'])
                bot.send_message(chatId,f"""{_("Alright, dear")} {playerName}{_(""", it's your turn for the defense! Go ahead and start.
                If you finish your defense early, use the phrase 'end of statement' to conclude""")}""")
                trueFalse(gameId,'games_info','stop_talk','false')
                Wait(75,gameId)
                admins = fetchall(gameId, 'admins')
                for admin in admins:
                    if admin[0] != P['id']:
                        bot.restrict_chat_member(chatId, P['id'], permissions=restrictChatMember)
                bot.send_message(chatId, _("Dear friend, your defense time is over!"))
                trueFalse(gameId,'games_info','stop_talk','false')
            Wait(2,gameId)
            for P in defenders:
                markup= InlineKeyboardMarkup()
                voteBtn= InlineKeyboardButton(_("I vote"),callback_data=f'vote_{gameId}_{P["id"]}')
                markup.add(voteBtn)
                message=bot.send_message(chatId,f' {_("We vote for")} {playerName} ',reply_markup=markup)
                Wait(50,gameId)
                bot.delete_message(chatId, message.message_id)
                votes=fetchvalue(gameId,'games_players','votes',P['id'])
                if int(votes)>=HalfNum:
                    status=insertVote(gameId,'votes',P['id'],'exit',int(votes))
                    if status:
                        bot.send_message(chatId,f'{playerName} {_("Oops!, Enough Votes...")}')
                clearVoters(gameId,)
            RemovePlayer(bot, chatId, gameId,langCode)
    else:
        bot.send_message(chatId,_(f"Well, we have no defense..."))
    resetVotes(gameId, 'games_players')

def remove(bot,gameId,p,chatId=None,nightDead=None):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    player = fetchWithPId(gameId, 'games_players', p['id'], )
    date=fetchvalue(gameId,'games_info','days')
    insertDeadMan(gameId,player,int(date))
    if chatId:
        bot.send_message(chatId, f"{_("Well, according to result,")} {player[1]} {_("is out of the game")}")
    #To follow the rules of the game, we need to keep the players until the beginning of the day and then remove them from the game
    if nightDead is None:
        deleteRows('votes', 'player_id', p['id'])
        if player[3] == _('Mafia'):
            deleteRows('mafias', 'game_id', gameId, 'player_id', player[0])
        deleteRows('games_players', 'player_id', player[0])


def RemovePlayer(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    players=[]
    list=fetchPlayer(gameId,'votes',Type='exit')
    if list:
        for player in list:
            p = {'id': player[0], 'type': player[1], 'gameId': player[2], 'numOfVotes' : player[3]}
            players.append(p)

        if len(players) == 1:
            player=players[0]
            remove(bot,gameId, player,chatId)

        elif len(players) == 2:
            player1=players[0]
            player2=players[1]
            deathDraw(bot,chatId,player1, player2, gameId,langCode)
            trueFalse(gameId,'games_info','stop_talk','false')
            Wait(300,gameId)
            trueFalse(gameId,'games_info','stop_talk','false')

        elif len(players)>=3:
            maxVotes=0
            mXPlayers=[]
            with lock:
                for player in players:
                    if player['numOfVotes']>maxVotes:
                        maxVotes=player['numOfVotes']
                list=fetchRow(gameId,'votes','num_of_votes',maxVotes)
                for player in list:
                    p = {'id': player[0], 'type': player[1], 'gameId': player[2], 'numOfVotes': player[3]}
                    mXPlayers.append(p)
            if len(mXPlayers)==1:
                mXPlayers=mXPlayers[0]
                remove(bot,gameId,mXPlayers,chatId)

            elif len(mXPlayers)==2:
                player1=mXPlayers[0]
                player2=mXPlayers[1]
                deathDraw(bot,chatId, player1, player2, gameId,langCode)
                trueFalse(gameId,'games_info','stop_talk','false')
                Wait(300,gameId)
                trueFalse(gameId,'games_info','stop_talk','false')
            elif len(mXPlayers)>=3:
                bot.send_message(chatId, _(f"According to the result, They will not be out of the game!"))
    deleteRows('votes', 'game_id', gameId)

def deathDraw(bot,chatId,player1,player2,gameId,langCode):
    _ = set_language(langCode)
    if player1['numOfVotes'] > player2['numOfVotes']:
        remove(bot,gameId= gameId, p=player1)
    elif player1['numOfVotes'] < player2['numOfVotes']:
        remove(bot, gameId=gameId, p=player2)
    elif player1['numOfVotes'] == player2['numOfVotes']:
        selector = random.choice([player1['id'], player2['id']])
        insertVote(gameId, 'votes', selector, 'death_draw_selector')
        insertVote(gameId,'votes',player1,'death_draw_player')
        insertVote(gameId, 'votes', player2, 'death_draw_player')
        playerName = fetchvalue(gameId, 'games_players', 'name', selector['id'])
        bot.send_message(chatId, _("Well, it's like we have to go for the lottery of death (Death draw)"))
        bot.send_message(chatId, f'{playerName}{_(" must choose!")}')
        markup = InlineKeyboardMarkup()
        callbackData1 = random.choice([f'blue_{gameId}_{player1["id"]}', f'blue_{gameId}_{player2["id"]}'])
        callbackData2 = random.choice([f'blue_{gameId}_{player1["id"]}', f'blue_{gameId}_{player2["id"]}'])
        Cart1 = InlineKeyboardButton(_('First Card💀'), callback_data=callbackData1)
        Cart2 = InlineKeyboardButton(_('Second Card💀'), callback_data=callbackData2)
        markup.add(Cart1)
        markup.add(Cart2)
        bot.send_message(chatId,
                         _("""The Death draw is like this, the one I choose, tells me which card he chooses between card one
                         and two, and one of these cards is blue, and if he chooses blue, he stays in the game, but if he chooses
                          red, the second defender stays in the game! Now, which one should you choose?"""),
                         reply_markup=markup)

def blueCart(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    player=fetchWithPId(gameId,'games_player',str(call.from_user.id))
    chatId=fetchvalue(gameId,'games_info','chat_id')
    bot.send_message(chatId,f"{_("I congratulate")} {player[1]}{_("! You are saved!")}")
    list=fetchPlayer(gameId,'votes',Type='death_draw_player')
    deadMan=None
    for player in list:
        if player[0] != str(call.from_user.id):
            deadMan=player
    remove(bot,gameId,deadMan,chatId)
    deleteRows('votes','game_id',gameId)
    trueFalse(gameId,'games_info','stop_talk','true')

def redCart(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    player=fetchWithPId(gameId,'games_player',str(call.from_user.id))
    chatId = fetchvalue(gameId, 'games_info', 'chat_id')
    bot.send_message(chatId,f"{_("Luck was not kind to you")} {player[1]} {_(",You kicked out of the game!")}")
    remove(bot, gameId, player,chatId)
    deleteRows('votes', 'game_id', gameId)
    trueFalse(gameId,'games_info','stop_talk','true')


def Night(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    waitTime=25
    blindNight=fetchvalue(gameId,'games_info','blind_night')
    if int(blindNight) == 1:
        #sherlock
        sherlock = fetchPlayer(gameId,'games_players',_('Sherlock'))
        bot.send_message(chatId,_("Sherlock, wake up, come to my PV :)"))
        if not sherlock:
            Wait(5,gameId)
        else:
            trueFalse(gameId, 'games_info', 'pick', 'false')
            sherlockMarkup = InlineKeyboardMarkup()
            yesSherlockBtn= InlineKeyboardButton(_('Yes'), callback_data='yes_Sherlock')
            noSherlockBtn= InlineKeyboardButton(_('No'), callback_data='no_Sherlock')
            sherlockMarkup.add(yesSherlockBtn)
            sherlockMarkup.add(noSherlockBtn)
            message=bot.send_message(sherlock['id'],_("Sherlock wake up! Do you want to slaughter someone tonight?")
                                     ,reply_markup=sherlockMarkup)
            Wait(waitTime,gameId)
            pick=fetchvalue(gameId,'games_info','pick')
            if pick==False:
                bot.delete_message(sherlock['id'],message.message_id)

            bot.send_message(sherlock['id'],_("Sherlock, sleep, relax..."))

    #Mafia
    mafiaList=fetchPlayer(gameId, 'games_players', side=_('Mafia'))
    godFather = [god for god in mafiaList if god['role'] == _('Godfather')]
    matador = [matador for matador in mafiaList if matador['role'] == _('Matador')]
    sualGoodman = [sual for sual in mafiaList if sual['role'] == _('Sual Goodman')]
    simpleMafia=[simple for simple in mafiaList if simple['role'] == _('Simple Mafia')]


    bot.send_message(chatId,_("Mafia, wake up, I gave you a message"))
    if blindNight == 0:
        for mafia in mafiaList:
            god=godFather[0]
            ma=matador[0]
            sual=sualGoodman[0]
            bot.send_message(mafia['id'],f'''{_("Names of mafia members:")}
            {_("Godfather")} : {god['name']}
            {_("Matador")} : {ma['name']}
            {_("Sual Goodman")} : {sual['name']}
            ''')
    for mafia in mafiaList:
        bot.send_message(mafia['id'],_(f"""{mafia["role"]} {_("""Wake up! Send any message you want forty seconds early
        So that your friend will read it""")}"""))
    mafiaChat(bot,mafiaList,langCode)

    if blindNight == 1:
        date(gameId,"nights")
        if not godFather:
            pass
        else:
            trueFalse(gameId,'games_info','pick','false')
            godFather = godFather[0]
            godFatherMarkup = InlineKeyboardMarkup()
            salakhiBtn= InlineKeyboardButton(_("I slaughter"), callback_data='slaughter_godFather')
            shelik=InlineKeyboardButton(_("I shoot"), callback_data='gunShot_godFather')
            godFatherMarkup.add(salakhiBtn)
            godFatherMarkup.add(shelik)
            message=bot.send_message(godFather['id'],_("godfather, do you play slaughter or shoot?")
                                     ,reply_markup=godFatherMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick==False:
                bot.delete_message(godFather['id'],message.message_id)
        if not matador:
            pass
        else:
            trueFalse(gameId,'games_info','pick','false')
            matador = matador[0]
            if not godFather:
                matadorShelikMarkup = InlineKeyboardMarkup()
                yesMatadorShelik = InlineKeyboardButton(_('I shoot'), callback_data='yes_Gunshot_matador')
                noMatadorShelik = InlineKeyboardButton(_("I don't shoot"), callback_data='no_Gunshot_matador')
                matadorShelikMarkup.add(yesMatadorShelik)
                matadorShelikMarkup.add(noMatadorShelik)
                message=bot.send_message(matador['id'], _("Matador, now that the godfather is not there, tell me, will you shoot or not??"),
                                 reply_markup=matadorShelikMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(matador['id'], message.message_id)
            trueFalse(gameId,'games_info','pick','false')
            matadorMarkup = InlineKeyboardMarkup()
            yesMatadorBtn = InlineKeyboardButton(_("I handcuff"), callback_data='yes_matador')
            noMatadorBtn = InlineKeyboardButton(_("I don't handcuff"), callback_data='no_matador')
            matadorMarkup.add(yesMatadorBtn)
            matadorMarkup.add(noMatadorBtn)
            message=bot.send_message(matador['id'], _("Matador, are you handcuffing anyone?"),
                                     reply_markup=matadorMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick==False:
                bot.delete_message(matador['id'],message.message_id)
        if len(mafiaList)<3 and sualGoodman:
            trueFalse(gameId,'games_info','pick','false')
            sualGoodman = sualGoodman[0]
            if not godFather and not matador:
                sualShelikMarkup = InlineKeyboardMarkup()
                yesSualShelik = InlineKeyboardButton(_("I shoot"), callback_data='yes_Gunshot_sual')
                noSualShelik = InlineKeyboardButton(_("I don't shoot"), callback_data='no_Gunshot_sual')
                sualShelikMarkup.add(yesSualShelik)
                sualShelikMarkup.add(noSualShelik)
                message=bot.send_message(sualGoodman['id'],_("Saul, now that the godfather is not there, tell me, will you shoot or not??"),
                                 reply_markup=sualShelikMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(sualGoodman['id'], message.message_id)

            trueFalse(gameId,'games_info','pick','false')
            sualPurchese = fetchvalue(gameId, 'games_info', 'sual_purchese')
            if str(sualPurchese) == '0':
                sualMarkup = InlineKeyboardMarkup()
                yesSualBtn = InlineKeyboardButton(_("I negotiate"), callback_data='yes_sual')
                noSualBtn = InlineKeyboardButton(_("I don't negotiate"), callback_data='no_sual')
                sualMarkup.add(yesSualBtn)
                sualMarkup.add(noSualBtn)
                message=bot.send_message(sualGoodman['id'],_("Saul Goodman, Cunning Mafia, Do You Negotiate?"),
                                         reply_markup=sualMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(sualGoodman['id'], message.message_id)
            else:
                bot.send_message(_("Well brother, you have done your work, go to sleep!"))

        if simpleMafia and not godFather and not matador and not sualGoodman:
            trueFalse(gameId,'games_info','pick','false')
            simpleMafia = simpleMafia[0]
            simpleMafiaMarkup = InlineKeyboardMarkup()
            yesSimpleBtn= InlineKeyboardButton(_("I shoot"), callback_data='yes_simpleMafia')
            noSimpleBtn=InlineKeyboardButton(_("I don't shoot"), callback_data='no_simpleMafia')
            simpleMafiaMarkup.add(yesSimpleBtn)
            simpleMafiaMarkup.add(noSimpleBtn)
            message=bot.send_message(simpleMafia['id'],_("simple mafia, do you shoot?"),
                                     reply_markup=simpleMafiaMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(simpleMafia['id'], message.message_id)
        for mafia in mafiaList:
            bot.send_message(mafia['id'], _(f"Sleep well mafia!"))

        #Shahrvandan

        #Doctor
        doctor = fetchPlayer(gameId,'games_players',_('Doctor'))
        bot.send_message(chatId, _("Come to the doctor, we have a sick patient!"))
        if not doctor:
            Wait(5,gameId)
        else:
            trueFalse(gameId,'games_info','pick','false')
            doctorMarkup = InlineKeyboardMarkup()
            yesDoctorBtn= InlineKeyboardButton(_('Yes'), callback_data='yes_doctor')
            noDoctorBtn= InlineKeyboardButton(_('No'), callback_data='no_doctor')
            doctorMarkup.add(yesDoctorBtn)
            doctorMarkup.add(noDoctorBtn)
            message=bot.send_message(doctor['id'],_("Dr of city, do you want to save someone?"),
                                     reply_markup=doctorMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(doctor['id'], message.message_id)

        #Leon
        leon = fetchPlayer(gameId,'games_players',_('Leon'))
        bot.send_message(chatId, _("Professional Leon, wake up, let's see what you are doing!"))
        if not leon:
            Wait(5,gameId)
        else:
            trueFalse(gameId,'games_info','pick','false')
            leonMarkup = InlineKeyboardMarkup()
            yesleonBtn = InlineKeyboardButton(_('Yes'), callback_data='yes_leon')
            noleonBtn = InlineKeyboardButton(_('No'), callback_data='no_leon')
            leonMarkup.add(yesleonBtn)
            leonMarkup.add(noleonBtn)
            message = bot.send_message(leon['id'], _("Leon, do you want to shoot someone?"),
                                       reply_markup=leonMarkup)
            Wait( waitTime, gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(leon['id'], message.message_id)

        #Kein
        kein = fetchPlayer(gameId,'games_players',_('Kein'))
        bot.send_message(chatId,_("Citizen Kein, wake up and tell me you are asking?!"))
        if not kein:
            Wait( 6, gameId)

        else:
            trueFalse(gameId,'games_info','pick','false')
            keinMeeting = fetchvalue(gameId, 'games_info', 'kein_meeting')
            if str(keinMeeting) == '0':
                keinMarkup = InlineKeyboardMarkup()
                yesKeinBtn= InlineKeyboardButton(_('Yes'), callback_data='yes_kein')
                noKeinBtn= InlineKeyboardButton(_('No'), callback_data='no_kein')
                keinMarkup.add(yesKeinBtn)
                keinMarkup.add(noKeinBtn)
                message=bot.send_message(kein['id'],_("Citizen Kein, do you want to question someone?"),
                                         reply_markup=keinMarkup)
                Wait( waitTime, gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(kein['id'], message.message_id)
            else:
                remove(bot, gameId, kein)
                bot.send_message(kein['id'],
                                 _("Well, you've done your own thing and we have to say goodbye! Bye bye!"))

    #Constantine
        lenDeads=lenPlayers(gameId,'deads')
        if int(lenDeads) != '0':
            constantine = fetchPlayer(gameId,'games_players',_('Constantine'))
            bot.send_message(chatId, 'کنستانتین کسی رو میخوای بیاری تو؟پیویم بگو')
            if not constantine:
                Wait( waitTime, gameId)

            else:
                constantineBirth = fetchvalue(gameId, 'games_info', 'constantine_birth')
                if str(constantineBirth) == '0':
                    trueFalse(gameId,'games_info','pick','false')
                    constantineMarkup = InlineKeyboardMarkup()
                    yesConstantineBtn= InlineKeyboardButton(_('Yes'), callback_data='yes_constantine')
                    noConstantineBtn= InlineKeyboardButton(_('No'), callback_data='no_constantine')
                    constantineMarkup.add(yesConstantineBtn)
                    constantineMarkup.add(noConstantineBtn)
                    message=bot.send_message(constantine['id'],_("Constantine, do you want to bring someone in?"),
                                             reply_markup=constantineMarkup)
                    Wait( 15, gameId)
                    pick = fetchvalue(gameId, 'games_info', 'pick')
                    if pick == False:
                        bot.delete_message(constantine['id'], message.message_id)
                else:
                    bot.send_message(constantine['id'],_("Well, Constantine, you have done your job, take it easy"))
                    Wait( 9, gameId)
    else:
        trueFalse(gameId,'games_info','blind_night','true')

    Day(bot,chatId,gameId,langCode)

def Day(bot,chatId,gameId,langCode):
    _ = set_language(langCode)
    Date=fetchvalue(gameId,'games_info','days')
    deadPlayers=fetchPlayer(gameId,'deads',date=int(Date))
    if deadPlayers == None:
        deadPlayers=[]
    sluaghterPlayers=fetchPlayer(gameId,'slaughtereds',date=int(Date))
    if sluaghterPlayers == None:
        sluaghterPlayers=[]
    date(gameId,"days")
    bot.send_message(chatId,_("It's day! Wake up city friends☀️"))
    time.sleep(1)
    if len(deadPlayers) > 0:
        bot.send_message(chatId,_("We had a death last night..."))
        time.sleep(1)
        for dead in deadPlayers:
            bot.send_message(chatId,f'{_("killed last night:")} {dead['name']} ')
            deleteRows('votes', 'player_id', dead['id'])
            if dead['side'] == _('Mafia'):
                deleteRows('mafias', 'game_id', gameId, 'player_id', dead['id'])
            deleteRows('games_players', 'player_id', dead['id'])

    if len(sluaghterPlayers) > 0:
        if len(deadPlayers) != 0:
            bot.send_message(chatId,_("And we had a slaughter, friends"))
        else:
            bot.send_message(chatId,_('We had a slaughter last night'))
        time.sleep(1)
        for sluaghted in sluaghterPlayers:
            bot.send_message(chatId,f'{_('Slaughter last night:')} {sluaghted[1]}')
    players=lenPlayers(gameId,'games_players')
    mafias=lenPlayers(gameId,'mafias')
    if players == mafias:
        bot.send_message(chatId, _(f"It's time to announce that the mafia WON the game and the city lost🔥🔥🔥"))
        Ending(bot,chatId, gameId)
    elif mafias == '0':
        bot.send_message(chatId, _(f"The city means you... WON🔥🔥🔥"))
        Ending(bot, chatId, gameId)
    elif players == '2' and mafias == '1':
        TrustDecision(bot,chatId, gameId,langCode)
    deleteRows('hand_cuffed','game_id',gameId)
    InquiryRequest(bot,chatId,gameId,langCode)
    pRoleList = fetchall(gameId, 'games_players')
    Chat(bot,chatId,pRoleList,gameId,langCode)
    Voting(bot,chatId,gameId,langCode)
    Night(bot, chatId,gameId,langCode)

def Sherlock(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['side'] != _('Sherlock'):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'sherlock_{gameId}_{player["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to slaughter?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))


def VerifySherlockSlaughter(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    if langCode == 'fa':
        bot.send_message(call.from_user.id, f'''فکر می کنی {player[1]} چه نقشی داره؟
        لیست نقش ها : {Rolelist_fa}
        * باید دقیقا مشابه این ساختار املایی، نقش موردنظرتان را بنویسید''')
    else:
        bot.send_message(call.from_user.id, f'''What role do you think {player[1]} has?
        List of roles : {Rolelist_en}
        * You must write your desired role exactly like this spelling structure''')
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySlaughter(message):
        if message.text == player[4]:
            sherlock=fetchPlayer(gameId,'games_players',_('Sherlock'))
            date=fetchvalue(gameId,'games_info','days')
            insertSlaughtered(gameId,player,date)
            deleteRows('games_players','player_id',str(player[0]))
            deleteRows('games_players','player_id',str(sherlock['id']))
            changedChar={'id': sherlock['id'],'name': sherlock['name'], 'user': sherlock['user'],
                              'side': player[3], 'role': player[4], 'link': sherlock['link'], 'votes': 0,}
            insertGP(gameId,'games_players',changedChar)
            if player[4] == _('Mafia'):
                deleteRows('mafias', 'game_id', gameId, 'player_id', player[0])
                insertBinaryTable(gameId,'mafias',player[0])

            bot.send_message(call.from_user.id,
                             f"{_("Slaughter is correct and done. Your role from now on:")} {changedChar['role']}")
        else:
            bot.send_message(call.from_user.id,_("You said wrong, Sherlock!"))


def GodfatherSlaughter(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if (player['role'] != _('Godfather') and player['role'] != _('Matador')
                    and player['role'] != _('Sual Goodman')):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'godSluaght_{gameId}_{player["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to slaughter?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))



def VerifyGodfatherSlaughter(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    mafias = fetchPlayer(gameId, 'mafias')
    bot.send_message(call.from_user.id,_('What role do you think {} has?').format(player[1]))
    for mafia in mafias:
        if mafia[0] != str(call.from_user.id):
            bot.send_message(mafia[0], f"{_("The godfather is slaughtering")} {player[1]}")
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySlaughter(message):
        if message.text == player[4]:
            date=fetchvalue(gameId,'games_info','days')
            insertSlaughtered(gameId,player,date)
            deleteRows('games_players','player_id',str(player[0]))
            bot.send_message(call.from_user.id, _("Slaughter is correct and done!"))
        else:
            bot.send_message(call.from_user.id,_("You said wrong, Senior Godfather!"))


def GunShot(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['id'] != str(call.from_user.id):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'Shot_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to kill?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))


def VerifyGunShot(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    nights=fetchvalue(gameId,'games_info','nights')
    caller=fetchWithPId(gameId,'games_players',str(call.from_user.id))
    #For using remove function, We need to create playerId dictionary
    playerId={'id':player[0]}
    if caller[4] != _('Leon'):
        mafias = fetchPlayer(gameId, 'mafias')
        for mafia in mafias:
            caller = [p for p in mafias if p[0] == str(call.from_user.id)]
            caller = caller[0]
            caller = fetchWithPId(gameId, 'games_players', caller[0])
            if mafia[0] != str(call.from_user.id):
                bot.send_message(mafia[0], _('{} Shoot to {} ').format(caller[1],player[1]))
        if player[4] != _('Leon'):
            if player[4]== _('Sherlock') and nights<=2:
                bot.send_message(call.from_user.id,_("Done"))
            elif player[4]==_('Sherlock') and nights>2:
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, _("Done"))
            else:
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, _("Done"))
        else:
            leonJacket = fetchvalue(gameId, 'games_info', 'leon_jecket')
            if str(leonJacket) == '1':
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, _("Done"))
            else:
                trueFalse(gameId,'games_info','leon_jacket','true')
                bot.send_message(call.from_user.id,_("Done"))
    else:
        if player[4] != _('Godfather') and player[3] != _('Citizen'):
            if player[4] == _('Sherlock') and nights <= 2:
                leonBullet(gameId)
                bot.send_message(call.from_user.id, _("Your shot is done!"))
            elif player[4] == _('Sherlock') and nights > 2:
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, _("Your shot is done!"))
            elif player[4] != _('Sherlock'):
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, _("Your shot is done!"))
        elif player[4] == _('Godfather'):
            godfatherJacket = fetchvalue(gameId, 'games_info', 'god_father_jacket')
            if str(godfatherJacket) == '1':
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, _("Your shot is done!"))
            else:
                leonBullet(gameId)
                trueFalse(gameId, 'games_info', 'god_father_jacket', 'true')
                bot.send_message(call.from_user.id, _("Your shot is done!"))
        elif player[3] == _('Citizen'):
            leon = fetchWithPId(gameId, 'games_info', str(call.from_user.id))
            playerId = {'id': leon[0]}
            remove(bot,gameId,playerId,nightDead=1)
            bot.send_message(call.from_user.id, _("Your shot is done!"))

def Matador(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['role'] != _('Godfather') and player['role'] != _('Matador') and player['role'] != _("Sual Goodman"):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'matador_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to handcuff?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))


def VerifyMatador(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    mafias = fetchPlayer(gameId, 'mafias')
    for mafia in mafias:
        caller = [p for p in mafias if p[0] == str(call.from_user.id)]
        caller = caller[0]
        caller=fetchWithPId(gameId,'games_players',caller[0])
        if mafia[0] != str(call.from_user.id):
            bot.send_message(mafia[0], _('{} handcuffed to {} ').format(caller[1],player[1]))
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        insertBinaryTable(gameId,'hand_cuffed',player[0])
    bot.send_message(call.from_user.id,_("Ok, I understand, Matador"))


def Sual(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players = fetchPlayer(gameId, 'games_players')
        for player in players:
            if player['role'] != _('Godfather') and player['role'] != _('Matador') and player['role'] != _('Sual Goodman'):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'sual_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to buy?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))


def VerifySual(bot,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    mafias=fetchPlayer(gameId,'mafias')
    if player[4] == _('Simple Citizen'):
        sualPurchese(gameId,player[0],langCode)
        bot.send_message(player[0],_("Your role is out of the game and now you are a simple mafia! Saul Goodman bought you"))
        for mafia in mafias:
            bot.send_message(mafia[0],f"{_("The purchase was made! Now,")} {player[1]} {_("became a member of the mafia team")}")
    else:
        for mafia in mafias:
            bot.send_message(mafia[0],_('Unfortunately, the purchase did not sit!'))

def Doctor(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['id'] == str(call.from_user.id):
                doctorSelfSave=fetchvalue(gameId,'games_players','doctor_self_save')
                if str(doctorSelfSave) == '1':
                    pass
                else:
                    Btn = InlineKeyboardButton(player['name'], callback_data=f'doctor_{gameId}_{player['id']}')
                    markup.add(Btn)
            else:
                Btn = InlineKeyboardButton(player['name'], callback_data=f'doctor_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to save?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))

def VerifyDoctor(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    exist=existence(gameId,'deads','player_id',player[0])
    if exist:
            deleteRows('deads','player_id',player[0])
            player={'id': player[0],'name': player[1], 'user': player[2],
                              'side': player[3], 'role': player[4], 'link': player[5], 'votes': 0,}
            insertGP(gameId,'games_players',player)
            if player['side'] == _('Mafia'):
                insertBinaryTable(gameId,'mafias',player['id'])
            bot.send_message(call.from_user.id, _("Alright Doctor! Go to sleep"))
    else:
        bot.send_message(call.from_user.id, _("Alright Doctor! Go to sleep"))

def Leon(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    bullet=fetchvalue(gameId,'games_info','leon_bullet')
    if int(bullet)>0:
        handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
        if handCuffed == False:
            markup = InlineKeyboardMarkup()
            players = fetchPlayer(gameId, 'games_players')
            for player in players:
                if player['role'] != _('Leon'):
                    Btn = InlineKeyboardButton(player['name'], callback_data=f'leon_{gameId}_{player['id']}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, _('Choose who you want to shoot?'), reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))
    else:
        bot.send_message(call.from_user.id,_("You're out of bullets, man! You are getting old..."))


def Kein(bot,call,gameId):
    langCode = getLangCode(gameId)
    _ = set_language(langCode)
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players = fetchPlayer(gameId, 'games_players')
        for player in players:
            if player['role'] != _('Kein'):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'kein_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to meet?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))



def VerifyKein(bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    if player[3] == _('Mafia'):
        insertBinaryTable(gameId,'kein_meets',player[0])
        trueFalse(gameId,'games_info','kein_meeting','true')
        bot.send_message(call.from_user.id, _("Your research is done! If it is true, I will tell you the result today."))
    else:
        bot.send_message(call.from_user.id,_("Your research is done! If it is correct, I will tell you the result today"))


def Constantine(bot,call,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    trueFalse(gameId, 'games_info', 'pick', 'true')
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        deads = fetchPlayer(gameId, 'deads')
        for player in deads:
            if player['role'] != _('Constantine'):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'constantine_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, _("Choose who you want to save from the dead?"), reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,_("Unfortunately, you can't do anything with a handcuff"))



def VerifyConstantine( bot,call,player,gameId):
    langCode=getLangCode(gameId)
    _ = set_language(langCode)
    trueFalse(gameId,'games_info','constantine_birth','true')
    deleteRows("deads",'player_id',player[0])
    player={'id':player[0],'name':player[1],'user':player[2],
            'side':player[3],'role':player[4],'link':player[5],'votes':0}
    insertGP(gameId,'games_players',player)
    bot.send_message(call.from_user.id,_("Ok i got it Constantine!"))

def Ending(bot,chatId,gameId):
    endGame(gameId)
    pRoleList = fetchall(gameId, 'games_players')
    for P in pRoleList:
        id = P[0]
        admins = fetchall(gameId, 'admins')
        for admin in admins:
            if admin[0] != id:
                bot.restrict_chat_member(chatId, id, permissions=allowChatMember)





