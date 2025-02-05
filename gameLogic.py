import random
import time
import telebot
from redis.commands.search.query import Query
from telebot.apihelper import delete_message, send_message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import dbMig
from constants import PlayerList, Rolelist, BotUserIds
import threading
from dbMig import *
lock = threading.Lock()

#Lists
gameIds=[]
Voters=[]
chatEvents = {}
# playerIds = []

#Allow and Restrict Chating
allowChatMember = telebot.types.ChatPermissions(can_send_messages=True)
restrictChatMember = telebot.types.ChatPermissions(can_send_messages=False)

def startG(bot,message,gameId):
    addGame(gameId,message.chat.id)
    markup = telebot.types.InlineKeyboardMarkup()
    AddBtn = telebot.types.InlineKeyboardButton('من هستم✋', callback_data='Add')
    FinalStart = InlineKeyboardButton('شروع نهایی👁️‍🗨️', callback_data='FinalStart')
    markup.add(AddBtn)
    markup.add(FinalStart)
    bot.send_message(message.chat.id, f"""به به چه دوستانی قراره دورهم مافیا بازی کنن!😎
    برای شرکت داخل بازی،ابتدا باید ربات رو استارت کرده باشید و سپس روی دکمه من هستم کلیک کنین تا این سناریو جذاب رو بازی کنیم!
    سناریو: پدرخوانده3
    تعداد شهروندان(دکتر،لئون،کین،کنستانتین،ساده): 7
    تعداد مافیا(پدرخوانده،ماتادور،ساول گودمن): 3
    نقش مستقل(شرلوک): 1
    *اگر بازی رو نمی دونید و آَشنایی ندارید از دستور /helpG استفاده کنید تا توضیح بدم.
    لیست بازیکنان:

    """, reply_markup=markup)


def AddPlayer(bot,call,gameId):
    with lock:
        lenP = lenPlayers(gameId,'players')
    if int(lenP) < 11 :
        if call.from_user.id in BotUserIds :
            p=fetchWithPId(gameId,'players',call.from_user.id)
            if not p:
                playerId=str(call.from_user.id)
                playerUser = call.from_user.username
                playerName=call.from_user.first_name
                playerLink = f'<a href="https://t.me/{playerUser}">{playerName}</a>'
                player={'name':playerName,'id':playerId,'user':playerUser,'link':playerLink}
                insertPL(gameId,'players',player)
                links=fetchLinks(gameId,'players')
                text = f"""به به چه دوستانی قراره دورهم مافیا بازی کنن!😎
                برای شرکت تو بازی، روی دکمه من هستم کلیک کنین تا این سناریو جذاب رو بازی کنیم   !
                سناریو: پدرخوانده3
                تعداد شهروندان(دکتر،لئون،کین،کنستانتین،ساده): 7
                تعداد مافیا(پدرخوانده،ماتادور،ساول گودمن): 3
                نقش مستقل(شرلوک): 1
                *اگر بازی رو نمی دونید و آَشنایی ندارید از دستور /helpG استفاده کنید تا توضیح بدم.
                لیست بازیکنان:\n
                {links}
                """

                markup = InlineKeyboardMarkup()
                AddBtn = telebot.types.InlineKeyboardButton('من هستم✋', callback_data='Add')
                FinalStart = telebot.types.InlineKeyboardButton('شروع نهایی👁️‍🗨️', callback_data='FinalStart')
                markup.add(AddBtn)
                markup.add(FinalStart)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=markup, parse_mode='HTML')
            else:
                bot.answer_callback_query(callback_query_id=call.id
                                          ,text='دوست عزیز شما در بازی هستید!منتظر شروع آن باشید'
                                                , show_alert = True)
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                        ,text='دوست عزیز شما ربات را استارت نکرده اید!'
                                        ,show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                , text='شما دیگر نمی توانید اضافه شوید!'
                                , show_alert=True)

def FinalStart(bot,call,gameId):
    UserId=call.from_user.id
    ChatId=call.message.chat.id
    ChatMember=bot.get_chat_member(chat_id=ChatId,user_id=UserId)
    if ChatMember.status in ['administrator', 'creator']:
        with lock:
            lenP = lenPlayers(gameId,'players')
        if int(lenP) == 11:
            bot.answer_callback_query(callback_query_id=call.id
                                        , text='بازی شروع شد!'
                                        , show_alert=True)
            bot.delete_message(ChatId,call.message.message_id)
            Operations(bot,ChatId,gameId)
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                          ,text='تعداد به حد نصاب نرسیده است!'
                                          ,show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                      , text='شما مجوز شروع بازی را ندارید!',
                                      show_alert=True)

def Operations(bot, chatId,gameId):
    playerList=fetchall(gameId,'players')
    randomRole = random.sample(Rolelist, len(playerList))
    for player, role in zip(playerList, randomRole):
        gamePlayer = { 'id': player[0],'name': player[1],
                    'user': player[2],'link': player[3],
                       'side': '', 'role': role , 'votes':0}
        if (gamePlayer['role'] == 'پدرخوانده'
                or gamePlayer['role'] == 'ماتادور'
                or gamePlayer['role'] == 'ساول گودمن'):
            gamePlayer['side'] = 'مافیا'
            insertBinaryTable(gameId,'mafias',gamePlayer['id'])
        elif gamePlayer['role'] == 'شرلوک':
            gamePlayer['side'] = 'شرلوک'
        else:
            gamePlayer['side'] = 'شهروند'
        insertGP(gameId,'games_players',gamePlayer)

    blindFunc(bot,chatId,gameId)

def blindFunc(bot, chatId,gameId):
    pRoleList = fetchall(gameId, 'games_players')
    for P in pRoleList:
        id = P[0]
        if id != "180477776":
            bot.restrict_chat_member(chatId, id, permissions=restrictChatMember)

    for P in pRoleList:
        role = P[4]
        bot.send_message(P[0], f"""نقش شما دوست عزیز🗿: {role}""")
    bot.send_message(chatId, """به همگی دوستان داخل بازی خوش آمد میگم😎
    از اینکه قراره یک بازی لذت بخش با شما رو داشته باشم خشنودم🪶
    دوستان نقش ها داخل پیوی شما توسط من اعلام شده و اکنون روز بلایند(ناآگاهی یا کوری) رو تا 5 ثانیه دیگه شروع می کنیم. اگر صحبت شما تمام شد با نوشتن کلمه اتمام کلام من رو آگاه کنید""")
    # Chat(bot,chatId,pRoleList,gameId)
    bot.send_message(chatId,'شب آغاز شد... شهر به خواب بره...🌙')
    trueFalse(gameId,'games_info','challenge','true')
    Night(bot,chatId,gameId)

chatLock = threading.Lock()
def startWait(gameId):
    with chatLock:
        event = threading.Event()
        chatEvents[str(gameId)] = event

def Wait(seconds, gameId):
    try:
        endTime = time.time() + seconds
        while time.time() < endTime:
            # Check if the Event is set every second
            if str(gameId) in chatEvents:
                print(f"Timer stopped for chat {gameId}")
                return
            time.sleep(0.1)
    finally:
        with chatLock:
            if str(gameId) in chatEvents:
                del chatEvents[str(gameId)]

def InquiryRequest(bot,chatId,gameId):
    numOfIRequest=fetchvalue(gameId,'games_info',"inquery_request")
    if numOfIRequest>0:
        trueFalse(gameId, 'games_info', 'pick', 'false')
        len=lenPlayers(gameId,'games_players')
        HalfNum = int(len) // 2
        markup = InlineKeyboardMarkup()
        yesBtn = InlineKeyboardButton('بله', callback_data=f'Yes_forInquiry')
        markup.add(yesBtn)
        message = bot.send_message(chatId, f'🔴آیا استعلام میخواین؟', reply_markup=markup)
        Wait(5,gameId)
        pick=fetchvalue(gameId,'games_info','pick')
        if pick == False:
            bot.delete_message(chatId, message.message_id)
        else:
            len=lenPlayers(gameId,'votes')
            if int(len) >= HalfNum:
                numOfIRequest-=1
                inqueryR(gameId,numOfIRequest)
                mafia=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side','مافیا')
                citizen=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side','شهروند')
                sherlock=fetchWithFK(gameId,'deads','player_id',
                                  'games_players','side','شرلوک')
                lenM=0
                lenC=0
                if mafia and citizen:
                    lenM= len(mafia)
                    lenC = len(citizen)
                if mafia is None:
                    lenC=len(citizen)
                if citizen is None:
                    lenM=len(mafia)

                bot.send_message(chatId,f'از بازی شما {lenC} شهروند، {lenM} مافیا بیرون رفتند')
                if sherlock:
                    bot.send_message(chatId,'و همچنین از بالا خبر رسید شرلوک هم از بازی بیرون رفته!')
            else:
                bot.send_message(chatId,'خیلی خب پس استعلام گرفته نمیشه!')
            resetVotes(gameId,'games_info')
            deleteRows('votes','game_id',gameId,'type','inquery')
            trueFalse(gameId,'games_info','pick','false')

    else:
        bot.send_message(chatId,'خب استعلامم که تموم شده...')
def VerifyInquiryRequest(bot,call,gameId):
    exist=existence(gameId,'games_players','player_id',str(call.from_user.id))
    if exist:
        status=insertVote(gameId,'votes',str(call.from_user.id),'inquery')
        if status:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='رای شما ثبت شد'
                                      , show_alert=True)
            markup = InlineKeyboardMarkup()
            yesBtn = InlineKeyboardButton('بله', callback_data=f'Yes_forInquiry')
            markup.add(yesBtn)
            query = f"""SELECT games_players.link
            FROM `votes`
            JOIN `games_players` ON votes.player_id = games_players.player_id
            WHERE  votes.game_id= %s"""
            links = fetchall(gameId, Query=query)
            text = f'''🔴آیا استعلام میخواین؟

            لیست درخواست کنندگان:
            {links}'''
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=markup, parse_mode='HTML')
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='رای شما قبلا ثبت شده است'
                                      , show_alert=True)


    else:
        bot.answer_callback_query(callback_query_id=call.id
                                        , text='شما نمی توانید درخواست دهید'
                                        , show_alert=True)

def Challenge(p, bot, chatId,gameId):
    insertBinaryTable(gameId,'challenge_turns',p[0])
    markup = InlineKeyboardMarkup()
    add_btn = InlineKeyboardButton('من میخوام', callback_data=f'add_challenge')
    markup.add(add_btn)
    bot.send_message(chatId, f'''کی از {p[1]} 🟠چالش میخواد؟''', reply_markup=markup)
    Wait(5,gameId)

def AddChallenge(bot, call,challenger,gameId):
    exist=existence(gameId,'games_players','player_id',str(call.from_user.id))
    if exist:
        requesterExist=existence(gameId,'challenges','requester_id',str(call.from_user.id))
        if not requesterExist:
            challenge={'requesterId':str(call.from_user.id),'challengerId':challenger}
            insertChllnge(gameId,challenge)
            markup = InlineKeyboardMarkup()
            addBtn = InlineKeyboardButton('من میخوام', callback_data='add_challenge')
            markup.add(addBtn)
            challenges=fetchall(gameId,'challenges',str(challenger))
            for challenge in challenges:
                requester=fetchWithPId(gameId,'games_players',challenge[1])
                name_btn = InlineKeyboardButton(f'{requester[1]}', callback_data=f'challenge_{gameId}_{requester[0]}')
                markup.add(name_btn)
            query = f"""SELECT games_players.link
            FROM `challenges`
            JOIN `games_players` ON challenges.requester_id = games_players.player_id
            WHERE  challenges.game_id= %s"""
            links = fetchall(gameId, Query=query)
            challenger=fetchWithPId(gameId,'games_players',challenger)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'''🟠کی از {challenger[1]} چالش میخواد؟  
                                                            
                                    لیست کسایی که ازت چالش می‌خوان:
                                    {links}                              
                                  ''', reply_markup=markup,parse_mode='HTML')
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='شما قبلا درخواست داده اید'
                                      , show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                        , text='شما نمی توانید درخواست دهید'
                                        , show_alert=True)

def activeChallenge(bot, call,requesterId,gameId):
    activeChllnge(gameId,str(requesterId))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, 'چالش انتخاب شد!')

def ApplyChallenge(bot, chatId,player,gameId):
    challenge=fetchRow(gameId,'challenges','status',1)
    if not challenge:
        bot.send_message(chatId, 'هیچ چالشی هم که انگار نداریم.')
    else:
        if challenge[1] != "180477776":
            bot.restrict_chat_member(chatId, challenge[1], permissions=allowChatMember)
        requester=fetchWithPId(gameId,'games_players',challenge[1])
        bot.send_message(chatId, f'نوبت چالشی که به دوست‌مون {requester[1]} دادند. بفرمایید صحبت کنید!')
        trueFalse(gameId,'games_info','stop_talk','false')
        Wait(30,gameId)
        if challenge[1] != "180477776":
            bot.restrict_chat_member(chatId, challenge[1], permissions=restrictChatMember)
        bot.send_message(chatId, f'دوست عزیز زمان چالش شما تمام شد!')
        deleteRows('challenges','game_id',int(gameId))
        trueFalse(gameId, 'games_info', 'stop_talk', 'false')
    deleteRows('challenge_turns', 'challenger_id',
               str(player[0]), 'game_id', int(gameId))
    time.sleep(1.5)


def Chat(bot,chatId,pRoleList,gameId):
    time.sleep(5)
    challenge=bool(existence(gameId,'games_info','challenge',1))
    for P in pRoleList:
        if P[0] != "180477776":
            bot.restrict_chat_member(chatId, P[0], permissions=allowChatMember)
        if challenge:
            Challenge(P,bot,chatId,gameId)
        bot.send_message(chatId, f'دوست عزیز {P[1]} بفرمایید صحبت کنید: ')
        trueFalse(gameId,'games_info','stop_talk','false')
        Wait(50,gameId)
        if P[0] != "180477776":
            bot.restrict_chat_member(chatId, P[0], permissions=restrictChatMember)
        bot.send_message(chatId, f'دوست عزیز زمان صحبت شما تمام شد!')
        trueFalse(gameId,'games_info','stop_talk','false')
        time.sleep(2)
        if challenge:
            ApplyChallenge(bot,chatId,P,gameId)

def mafiaChat(bot,mafias):
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
                bot.send_message(mafia['id'],f"پیام از {sender['name']}: {message.text}")

    time.sleep(chatDuration)
    ChatState.active = False
    for mafia in mafias:
            bot.send_message(mafia['id'], "🔴زمان چت مافیا به پایان رسید")

def TrustDecision(bot,chatId,gameId):
    trustedCitizen=[]
    voters=[]
    names=[]
    players=fetchPlayer(gameId,'games_players')
    bot.send_message(chatId,f'''خیلی خب دوستان عزیز به مرحله کی آس رسیدیم و شما درابتدا می تونید آزادانه سه دقیقه صحبت کنید''')
    for player in players:
        names.append(player['name'])
        bot.restrict_chat_member(chatId, player['id'], permissions=allowChatMember)
    Wait(181, gameId)
    bot.send_message(chatId, f'خیلی خب زمان صحبت تموم شد و الان وقتشه هر سه بیاین داخل پیوی من و بنویسید به کی اعتماد دارید که شهرونده!')
    for player in players:
        bot.send_message(player['id'],'بگو ببینم کی رو تو به عنوان شهروند بهش اعتماد داری؟')
    @bot.message_handler(func=lambda message: names )
    def selectingCitizen(message):
        if message.chat.type == "private" and str(message.chat.id) not in voters:
            for player in players:
                if message.text == player['name']:
                    with lock:
                        player['votes'] = int(player['votes']) + 1
                        voters.append(str(message.chat.id))
                        bot.send_message(message.chat.id, 'نظرت دریافت شد!')
    Wait(15,gameId)
    for player in players:
        if player['votes'] > 1:
            trustedCitizen.append(player)
            trustedCitizen=trustedCitizen[0]
    if trustedCitizen is None:
        trustedCitizen = players[0]
    insertVote(gameId, 'votes',trustedCitizen['id'], 'trusted_citizen')
    bot.send_message(chatId,f'طبق نتیجه، {trustedCitizen['name']}  به عنوان فرد شهروند شما انتخاب شد. از الان تا سی ثانیه وقت داری تا انتخاب کنی با چه کسی دست بدی!')
    markup= InlineKeyboardMarkup()
    for player in players:
        if player['id'] != trustedCitizen['id']:
            voteBtn = InlineKeyboardButton(f'{player['name']}', callback_data=f'hand_{gameId}_{player['id']}')
            markup.add(voteBtn)
    bot.send_message(chatId, f'کدوم یکی از دوستان رو برای دست دادن انتخاب می کنی؟', reply_markup=markup)
    Wait(30, gameId)
    shakingHands=fetchvalue(gameId,'games_info','shaking_hands')
    if shakingHands:
        player=fetchWithPId(gameId,'games_players',shakingHands)
        if player['side'] == 'مافیا':
            bot.send_message('با انتخاب شما، مافیا بازی رو برد و شهر باخت🔥🔥')
            Ending(bot,chatId,gameId)
        else:
            bot.send_message('با انتخاب شما، مافیا بازی رو باخت و شهر برد🔥🔥')
            Ending(bot, chatId, gameId)
    else:
        bot.send_message('بدلیل اینکه شما انتخاب نکردید، مافیا بازی رو برد و شهر باخت🔥🔥')
        Ending(bot, chatId, gameId)


votingTime=12
def Voting(bot,chatId,gameId):
    players=fetchPlayer(gameId,'games_players')
    HalfNum=len(players)//2
    for P in players:
        markup= InlineKeyboardMarkup()
        voteBtn= InlineKeyboardButton('رای میدم',callback_data=f'vote_{gameId}_{P['id']}')
        markup.add(voteBtn)
        message=bot.send_message(chatId,f'{P['name']}رای گیری می کنیم برای',reply_markup=markup)
        Wait(votingTime,gameId)
        bot.delete_message(chatId,message.message_id)
        votes=fetchvalue(gameId,'games_players','votes',P['id'])
        if votes>=HalfNum:
            status=insertVote(gameId,'votes',P['id'],'city')
            if status:
                bot.send_message(chatId,f'به دفاع میره {P['name']} خب پس ...')
        clearVoters(gameId)
    resetVotes(gameId, 'games_players')
    Defence(bot,chatId,HalfNum,gameId)

def clearVoters(gameId):
    global Voters
    for voter in reversed(Voters):
        if voter['gameId'] == str(gameId):
            Voters.remove(voter)



def CountingVotes(bot,call,playerId,gameId):
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
        text = f'''\n {player[1]}رای گیری می کنیم برای  
        لیست رای دهندگان:
        {links}'''
        markup = InlineKeyboardMarkup()
        voteBtn = InlineKeyboardButton('رای میدم', callback_data=f'vote_{gameId}_{player[0]}')
        markup.add(voteBtn)
        bot.answer_callback_query(callback_query_id=call.id
                                  , text='رای شما برای ایشان ثبت شد'
                                  , show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup, parse_mode='HTML')
        playerIds.clear()
        links.clear()
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                  , text='شما قبلا یکبار رای داده اید!'
                                  , show_alert=True)


def Defence(bot,chatId,HalfNum,gameId):
    defenders=[]
    list=fetchPlayer(gameId,'votes',Type='city')
    if list:
        for player in list:
            p = {'id': player[0], 'type': player[1], 'gameId': player[2]}
            defenders.append(p)
        if int(len(defenders))>0:
            for P in defenders:
                if P['id'] != "180477776":
                    bot.restrict_chat_member(chatId, P['id'], permissions=allowChatMember)
                playerName = fetchvalue(gameId, 'games_players', 'name', P['id'])
                bot.send_message(chatId,f'خب دوست عزیز {playerName} شما اومدید توی دفاعیه! شروع کنید و اگه دفاع تون زودتر تموم میشه از همون کلمه ی اتمام کلام استفاده کنید')
                trueFalse(gameId,'games_info','stop_talk','false')
                Wait(75,gameId)
                if P['id'] != "180477776":
                    bot.restrict_chat_member(chatId, P['id'], permissions=restrictChatMember)
                bot.send_message(chatId, f'دوست عزیز زمان دفاع شما تمام شد!')
                trueFalse(gameId,'games_info','stop_talk','false')
            Wait(2,gameId)
            for P in defenders:
                markup= InlineKeyboardMarkup()
                voteBtn= InlineKeyboardButton('رای میدم',callback_data=f'vote_{gameId}_{P["id"]}')
                markup.add(voteBtn)
                message=bot.send_message(chatId,f'{playerName}رای گیری می کنیم برای ',reply_markup=markup)
                Wait(50,gameId)
                bot.delete_message(chatId, message.message_id)
                votes=fetchvalue(gameId,'games_players','votes',P['id'])
                if int(votes)>=HalfNum:
                    status=insertVote(gameId,'votes',P['id'],'exit',int(votes))
                    if status:
                        bot.send_message(chatId,f'{playerName} اوه آرا کافی است...')
                clearVoters(gameId,)
            RemovePlayer(bot, chatId, gameId)
    else:
        bot.send_message(chatId,f'خب پس هیچ دفاعی نداریم...')
    resetVotes(gameId, 'games_players')

def remove(bot,gameId,p,chatId=None,nightDead=None):
    player = fetchWithPId(gameId, 'games_players', p['id'], )
    date=fetchvalue(gameId,'games_info','days')
    insertDeadMan(gameId,player,int(date))
    if chatId:
        bot.send_message(chatId, f'خب پس طبق نتیجه {player[1]}از بازی خارج میشن')
    #To follow the rules of the game, we need to keep the players until the beginning of the day and then remove them from the game
    if nightDead is None:
        deleteRows('votes', 'player_id', p['id'])
        if player[3] == 'مافیا':
            deleteRows('mafias', 'game_id', gameId, 'player_id', player[0])
        deleteRows('games_players', 'player_id', player[0])


def RemovePlayer(bot,chatId,gameId):
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
            deathDraw(bot,chatId,player1, player2, gameId)
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
                deathDraw(bot,chatId, player1, player2, gameId)
                trueFalse(gameId,'games_info','stop_talk','false')
                Wait(300,gameId)
                trueFalse(gameId,'games_info','stop_talk','false')
            elif len(mXPlayers)>=3:
                bot.send_message(chatId, f'طبق نتیجه هیچکدوم از بازی خارج نمیشین!')
    deleteRows('votes', 'game_id', gameId)

def deathDraw(bot,chatId,player1,player2,gameId):
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
        bot.send_message(chatId, 'خب مثل اینکه باید بریم واسه قرعه مرگ')
        bot.send_message(chatId, f'{playerName}انتخاب باید انتخاب کنه!')
        markup = InlineKeyboardMarkup()
        callbackData1 = random.choice([f'blue_{gameId}_{player1["id"]}', f'blue_{gameId}_{player2["id"]}'])
        callbackData2 = random.choice([f'blue_{gameId}_{player1["id"]}', f'blue_{gameId}_{player2["id"]}'])
        Cart1 = InlineKeyboardButton('کارت اول💀', callback_data=callbackData1)
        Cart2 = InlineKeyboardButton('کارت دوم💀', callback_data=callbackData2)
        markup.add(Cart1)
        markup.add(Cart2)
        bot.send_message(chatId,
                         'فرعه مرگ به این شکله اونی که من انتخاب می کنم،به من میگه که بین کارت یک و دو کدوم رو انتخاب می کنه و یکی از این ها کارت آبی هست و اگه آبی رو انتخاب کنه توی بازی میمونه ولی اگه قرمز رو انتخاب کنه، دفاع کننده دوم توی بازی میمونه! حالا انتخاب کن کدوم؟',
                         reply_markup=markup)

def blueCart(bot,call,gameId):
    player=fetchWithPId(gameId,'games_player',str(call.from_user.id))
    chatId=fetchvalue(gameId,'games_info','chat_id')
    bot.send_message(chatId,f'بهت تبریک میگم! {player[1]} نجات پیدا کردی !')
    list=fetchPlayer(gameId,'votes',Type='death_draw_player')
    deadMan=None
    for player in list:
        if player[0] != str(call.from_user.id):
            deadMan=player
    remove(bot,gameId,deadMan,chatId)
    deleteRows('votes','game_id',gameId)
    trueFalse(gameId,'games_info','stop_talk','true')

def redCart(bot,call,gameId):
    player=fetchWithPId(gameId,'games_player',str(call.from_user.id))
    chatId = fetchvalue(gameId, 'games_info', 'chat_id')
    bot.send_message(chatId,f'بخت باهات یار نبود متاسانه! {player[1]} از بازی اخراجی!')
    remove(bot, gameId, player,chatId)
    deleteRows('votes', 'game_id', gameId)
    trueFalse(gameId,'games_info','stop_talk','true')


def Night(bot,chatId,gameId):
    waitTime=25
    blindNight=fetchvalue(gameId,'games_info','blind_night')
    if int(blindNight) == 1:
        #sherlock
        sherlock = fetchPlayer(gameId,'games_players','شرلوک')
        bot.send_message(chatId, 'شرلوک بیدار شو بیا پیوی مون:)')
        if not sherlock:
            Wait(5,gameId)
        else:
            trueFalse(gameId, 'games_info', 'pick', 'false')
            sherlockMarkup = InlineKeyboardMarkup()
            yesSherlockBtn= InlineKeyboardButton('آره', callback_data='yes_Sherlock')
            noSherlockBtn= InlineKeyboardButton('نه', callback_data='no_Sherlock')
            sherlockMarkup.add(yesSherlockBtn)
            sherlockMarkup.add(noSherlockBtn)
            message=bot.send_message(sherlock['id'],'شرلوک بیدار شو! آیا امشب میخوای کسی رو سلاخی کنی؟',reply_markup=sherlockMarkup)
            Wait(waitTime,gameId)
            pick=fetchvalue(gameId,'games_info','pick')
            if pick==False:
                bot.delete_message(sherlock['id'],message.message_id)

            bot.send_message(sherlock['id'],'شرلوک بخواب راحت باش')

    #Mafia
    mafiaList=fetchPlayer(gameId, 'games_players', side='مافیا')
    godFather = [god for god in mafiaList if god['role'] == 'پدرخوانده']
    matador = [matador for matador in mafiaList if matador['role'] == 'ماتادور']
    sualGoodman = [sual for sual in mafiaList if sual['role'] == 'ساول گودمن']
    simpleMafia=[simple for simple in mafiaList if simple['role'] == 'مافیا ساده']
    #////////////

    bot.send_message(chatId,'مافیا بیدار شه بیا پیوی بهت مسیج دادم')
    if blindNight == 0:
        for mafia in mafiaList:
            god=godFather[0]
            ma=matador[0]
            sual=sualGoodman[0]
            bot.send_message(mafia['id'],f'''نام اعضای مافیا :
            پدرخوانده : {god['name']}
            ماتادور : {ma['name']}
            ساول گودمن : {sual['name']}
            ''')
    for mafia in mafiaList:
        bot.send_message(mafia['id'],f'{mafia["role"]} بیدار شو! ده ثانیه زود هرپیامی میخوای بفرست تا یار هات بخونن')
    # mafiaChat(bot,mafiaList)

    if blindNight == 1:
        date(gameId,"nights")
        if not godFather:
            pass
        else:
            trueFalse(gameId,'games_info','pick','false')
            godFather = godFather[0]
            godFatherMarkup = InlineKeyboardMarkup()
            salakhiBtn= InlineKeyboardButton('سلاخی می کنم', callback_data='slaughter_godFather')
            shelik=InlineKeyboardButton('شلیک می کنم', callback_data='gunShot_godFather')
            godFatherMarkup.add(salakhiBtn)
            godFatherMarkup.add(shelik)
            message=bot.send_message(godFather['id'],'پدرخوانده بازی سلاخی می کنی یا شلیک می کنی؟',reply_markup=godFatherMarkup)
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
                yesMatadorShelik = InlineKeyboardButton('شلیک می کنم', callback_data='yes_Gunshot_matador')
                noMatadorShelik = InlineKeyboardButton('شلیک نمی کنم', callback_data='no_Gunshot_matador')
                matadorShelikMarkup.add(yesMatadorShelik)
                matadorShelikMarkup.add(noMatadorShelik)
                message=bot.send_message(matador['id'], 'ماتادور حالا که پدرخوانده نیست تو بگو شلیک می کنی یا نه؟؟',
                                 reply_markup=matadorShelikMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(matador['id'], message.message_id)
            trueFalse(gameId,'games_info','pick','false')
            matadorMarkup = InlineKeyboardMarkup()
            yesMatadorBtn = InlineKeyboardButton('دستبند میزنم', callback_data='yes_matador')
            noMatadorBtn = InlineKeyboardButton('دستبند نمیزنم', callback_data='no_matador')
            matadorMarkup.add(yesMatadorBtn)
            matadorMarkup.add(noMatadorBtn)
            message=bot.send_message(matador['id'], 'ماتادور، آیا دستبند می زنی؟', reply_markup=matadorMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick==False:
                bot.delete_message(matador['id'],message.message_id)
        if len(mafiaList)<3 and sualGoodman:
            trueFalse(gameId,'games_info','pick','false')
            sualGoodman = sualGoodman[0]
            if not godFather and not matador:
                sualShelikMarkup = InlineKeyboardMarkup()
                yesSualShelik = InlineKeyboardButton('شلیک می کنم', callback_data='yes_Gunshot_sual')
                noSualShelik = InlineKeyboardButton('شلیک نمی کنم', callback_data='no_Gunshot_sual')
                sualShelikMarkup.add(yesSualShelik)
                sualShelikMarkup.add(noSualShelik)
                message=bot.send_message(sualGoodman['id'], 'ساول حالا که پدرخوانده نیست تو بگو شلیک می کنی یا نه؟؟',
                                 reply_markup=sualShelikMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(sualGoodman['id'], message.message_id)

            trueFalse(gameId,'games_info','pick','false')
            sualPurchese = fetchvalue(gameId, 'games_info', 'sual_purchese')
            if str(sualPurchese) == '0':
                sualMarkup = InlineKeyboardMarkup()
                yesSualBtn = InlineKeyboardButton('مذاکره می کنم', callback_data='yes_sual')
                noSualBtn = InlineKeyboardButton('مذاکره نمی کنم', callback_data='no_sual')
                sualMarkup.add(yesSualBtn)
                sualMarkup.add(noSualBtn)
                message=bot.send_message(sualGoodman['id'], 'ساول گودمن، مافیای حیله گر، آیا مذاکره می کنی؟', reply_markup=sualMarkup)
                Wait(waitTime,gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(sualGoodman['id'], message.message_id)
            else:
                bot.send_message('خب داداش تو که کارتو کردی بخواب!')

        if simpleMafia and not godFather and not matador and not sualGoodman:
            trueFalse(gameId,'games_info','pick','false')
            simpleMafia = simpleMafia[0]
            simpleMafiaMarkup = InlineKeyboardMarkup()
            yesSimpleBtn= InlineKeyboardButton('َشلیک می کنم', callback_data='yes_simpleMafia')
            noSimpleBtn=InlineKeyboardButton('شلیک نمی کنم', callback_data='no_simpleMafia')
            simpleMafiaMarkup.add(yesSimpleBtn)
            simpleMafiaMarkup.add(noSimpleBtn)
            message=bot.send_message(simpleMafia['id'],'مافیا ساده آیا شلیک می کنی؟',reply_markup=simpleMafiaMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(simpleMafia['id'], message.message_id)
        for mafia in mafiaList:
            bot.send_message(mafia['id'], f'مافیای جیگر آروم بخواب')

        #Shahrvandan

        #Doctor
        doctor = fetchPlayer(gameId,'games_players','دکتر')
        bot.send_message(chatId, 'دکتر بیاد پیوی مریض داریم!')
        if not doctor:
            Wait(5,gameId)
        else:
            trueFalse(gameId,'games_info','pick','false')
            doctorMarkup = InlineKeyboardMarkup()
            yesDoctorBtn= InlineKeyboardButton('بله', callback_data='yes_doctor')
            noDoctorBtn= InlineKeyboardButton('خیر', callback_data='no_doctor')
            doctorMarkup.add(yesDoctorBtn)
            doctorMarkup.add(noDoctorBtn)
            message=bot.send_message(doctor['id'],'دکتر شهر، آیا کسی رو می خوای نجات بدی؟',reply_markup=doctorMarkup)
            Wait(waitTime,gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(doctor['id'], message.message_id)

        #Leon
        leon = fetchPlayer(gameId,'games_players','لئون')
        bot.send_message(chatId, 'لئون حرفه ای مون بیدارشو بیا ببینیم چیکار می کنی!')
        if not leon:
            Wait(5,gameId)
        else:
            trueFalse(gameId,'games_info','pick','false')
            leonMarkup = InlineKeyboardMarkup()
            yesleonBtn = InlineKeyboardButton('بله', callback_data='yes_leon')
            noleonBtn = InlineKeyboardButton('خیر', callback_data='no_leon')
            leonMarkup.add(yesleonBtn)
            leonMarkup.add(noleonBtn)
            message = bot.send_message(leon['id'], 'لئون، آیا کسی رو می خوای با تیر بزنی؟', reply_markup=leonMarkup)
            Wait( waitTime, gameId)
            pick = fetchvalue(gameId, 'games_info', 'pick')
            if pick == False:
                bot.delete_message(leon['id'], message.message_id)

        #Kein
        kein = fetchPlayer(gameId,'games_players','شهروند کین')
        bot.send_message(chatId,'شهروند کین بیدارشو ببینیم استعلام میگیری یا نه!')
        if not kein:
            Wait( 6, gameId)

        else:
            trueFalse(gameId,'games_info','pick','false')
            keinMeeting = fetchvalue(gameId, 'games_info', 'kein_meeting')
            if str(keinMeeting) == '0':
                keinMarkup = InlineKeyboardMarkup()
                yesKeinBtn= InlineKeyboardButton('بله', callback_data='yes_kein')
                noKeinBtn= InlineKeyboardButton('خیر', callback_data='no_kein')
                keinMarkup.add(yesKeinBtn)
                keinMarkup.add(noKeinBtn)
                message=bot.send_message(kein['id'],'شهروند کین، آیا کسی رو می خوای استعلام بگیری؟',reply_markup=keinMarkup)
                Wait( waitTime, gameId)
                pick = fetchvalue(gameId, 'games_info', 'pick')
                if pick == False:
                    bot.delete_message(kein['id'], message.message_id)
            else:
                remove(bot, gameId, kein)
                bot.send_message(kein['id'],
                                 'خب هم ولاتی چیز همشری جان تو هم که کار خودتو کردی و باید باهم خداحافظی کنیم! بای بای!')

    #Constantine
        lenDeads=lenPlayers(gameId,'deads')
        if int(lenDeads) != '0':
            constantine = fetchPlayer(gameId,'games_players','کنستانتین')
            bot.send_message(chatId,'کنستانتین کسی رو میخوای بیاری تو؟پیویم بگو')
            if not constantine:
                Wait( waitTime, gameId)

            else:
                constantineBirth = fetchvalue(gameId, 'games_info', 'constantine_birth')
                if str(constantineBirth) == '0':
                    trueFalse(gameId,'games_info','pick','false')
                    constantineMarkup = InlineKeyboardMarkup()
                    yesConstantineBtn= InlineKeyboardButton('بله', callback_data='yes_constantine')
                    noConstantineBtn= InlineKeyboardButton('خیر', callback_data='no_constantine')
                    constantineMarkup.add(yesConstantineBtn)
                    constantineMarkup.add(noConstantineBtn)
                    message=bot.send_message(constantine['id'],'کنستانتین، آیا کسی رو می خوای بیاری داخل ؟',reply_markup=constantineMarkup)
                    Wait( 15, gameId)
                    pick = fetchvalue(gameId, 'games_info', 'pick')
                    if pick == False:
                        bot.delete_message(constantine['id'], message.message_id)
                else:
                    bot.send_message(constantine['id'],'خب کنستانتین تو هم که کار خودتو کردی راحت باش')
                    Wait( 9, gameId)
    else:
        trueFalse(gameId,'games_info','blind_night','true')

    Day(bot,chatId,gameId)

def Day(bot,chatId,gameId):
    Date=fetchvalue(gameId,'games_info','days')
    deadPlayers=fetchPlayer(gameId,'deads',date=int(Date))
    if deadPlayers == None:
        deadPlayers=[]
    sluaghterPlayers=fetchPlayer(gameId,'slaughtereds',date=int(Date))
    if sluaghterPlayers == None:
        sluaghterPlayers=[]
    date(gameId,"days")
    bot.send_message(chatId,'روز شد! شهر بیدار شه دوستان☀️')
    time.sleep(1)
    if len(deadPlayers) > 0:
        bot.send_message(chatId,'دیشب کشته داشتیم...')
        time.sleep(1)
        for dead in deadPlayers:
            bot.send_message(chatId,f'کشته دیشب: {dead['name']} ')
            deleteRows('votes', 'player_id', dead['id'])
            if dead['side'] == 'مافیا':
                deleteRows('mafias', 'game_id', gameId, 'player_id', dead['id'])
            deleteRows('games_players', 'player_id', dead['id'])

    if len(sluaghterPlayers) > 0:
        if len(deadPlayers) != 0:
            bot.send_message(chatId,'و سلاخی هم داشتیم دوستان')
        else:
            bot.send_message(chatId, 'ی دیشب سلاخی داشتیم عجب...')
        time.sleep(1)
        for sluaghted in sluaghterPlayers:
            bot.send_message(chatId,f'ُسلاخی دیشب: {sluaghted[1]}')
    players=lenPlayers(gameId,'games_players')
    mafias=lenPlayers(gameId,'mafias')
    if players == mafias:
        bot.send_message(chatId, f'دیگه وقتشه اعلام کنم که مافیا بازی رو برد و شهر باخت🔥🔥🔥')
        Ending(bot,chatId, gameId)
    elif mafias == '0':
        bot.send_message(chatId, f'🔥🔥🔥شهر یعنی شماهااا! شهر پیروز شددد')
        Ending(bot, chatId, gameId)
    elif players == '2' and mafias == '1':
        TrustDecision(bot,chatId, gameId)
    deleteRows('hand_cuffed','game_id',gameId)
    InquiryRequest(bot,chatId,gameId)
    # pRoleList = fetchall(gameId, 'games_players')
    # Chat(bot,chatId,pRoleList,gameId)
    Voting(bot,chatId,gameId)
    Night(bot, chatId,gameId)

def Sherlock(bot,call,gameId):
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['side'] != 'شرلوک':
                Btn = InlineKeyboardButton(player['name'], callback_data=f'sherlock_{gameId}_{player["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که سلاخی کنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifySherlockSlaughter(bot,call,player,gameId):
    bot.send_message(call.from_user.id,f'''فکر می کنی {player[1]} چه نقشی داره؟
لیست نقش ها : {Rolelist}
* باید دقیقا مشابه این ساختار املایی، نقش موردنظرتان را بنویسید''')
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySlaughter(message):
        if message.text == player[4]:
            sherlock=fetchPlayer(gameId,'games_players','شرلوک')
            date=fetchvalue(gameId,'games_info','days')
            insertSlaughtered(gameId,player,date)
            deleteRows('games_players','player_id',str(player[0]))
            deleteRows('games_players','player_id',str(sherlock['id']))
            changedChar={'id': sherlock['id'],'name': sherlock['name'], 'user': sherlock['user'],
                              'side': player[3], 'role': player[4], 'link': sherlock['link'], 'votes': 0,}
            insertGP(gameId,'games_players',changedChar)
            if player[4] == 'مافیا':
                deleteRows('mafias', 'game_id', gameId, 'player_id', player[0])
                insertBinaryTable(gameId,'mafias',player[0])

            bot.send_message(call.from_user.id,
                             f'سلاخی درسته و انجام شد.نقش شما از این به بعد: {changedChar['role']}')
        else:
            bot.send_message(call.from_user.id,'اشتباه گفتی شرلوک!')


def GodfatherSlaughter(bot,call,gameId):
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if (player['role'] != 'پدرخوانده' and player['role'] != 'ماتادور'
                    and player['role'] != 'ساول گودمن'):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'godSluaght_{gameId}_{player["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که سلاخی کنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')



def VerifyGodfatherSlaughter(bot,call,player,gameId):
    mafias = fetchPlayer(gameId, 'mafias')
    bot.send_message(call.from_user.id,f'فکر می کنی {player[1]} چه نقشی داره؟')
    for mafia in mafias:
        if mafia[0] != str(call.from_user.id):
            bot.send_message(mafia[0], f'پدرخوانده درحال سلاخی {player[1]} است')
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySlaughter(message):
        if message.text == player[4]:
            date=fetchvalue(gameId,'games_info','days')
            insertSlaughtered(gameId,player,date)
            deleteRows('games_players','player_id',str(player[0]))
            bot.send_message(call.from_user.id, 'سلاخی درسته و انجام شد')
        else:
            bot.send_message(call.from_user.id,'اشتباه گفتی سنیور پدرخوانده!')


def GunShot(bot,call,gameId):
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['id'] != str(call.from_user.id):
                Btn = InlineKeyboardButton(player['name'], callback_data=f'Shot_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که بکشی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyGunShot(bot,call,player,gameId):
    nights=fetchvalue(gameId,'games_info','nights')
    caller=fetchWithPId(gameId,'games_players',str(call.from_user.id))
    #For using remove function, We need to create playerId dictionary
    playerId={'id':player[0]}
    if caller[4] != 'لئون':
        mafias = fetchPlayer(gameId, 'mafias')
        for mafia in mafias:
            caller = [p for p in mafias if p[0] == str(call.from_user.id)]
            caller = caller[0]
            caller = fetchWithPId(gameId, 'games_players', caller[0])
            if mafia[0] != str(call.from_user.id):
                bot.send_message(mafia[0], f'{caller[1]} به {player[1]} شلیک کرد')
        if player[4] != 'لئون':
            if player[4]== 'شرلوک' and nights<=2:
                bot.send_message(call.from_user.id,'انجام شد!')
            elif player[4]=='شرلوک' and nights>2:
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, 'انجام شد!')
            else:
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, 'انجام شد!')
        else:
            leonJacket = fetchvalue(gameId, 'games_info', 'leon_jecket')
            if str(leonJacket) == '1':
                remove(bot,gameId,playerId,nightDead=1)
                bot.send_message(call.from_user.id, 'انجام شد!')
            else:
                trueFalse(gameId,'games_info','leon_jacket','true')
                bot.send_message(call.from_user.id,'انجام شد!')
    else:
        if player[4] != 'پدرخوانده' and player[3] != 'شهروند':
            if player[4] == 'شرلوک' and nights <= 2:
                leonBullet(gameId)
                bot.send_message(call.from_user.id, 'شلیکت نشست!')
            elif player[4] == 'شرلوک' and nights > 2:
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, 'شلیکت نشست!')
            elif player[4] != 'شرلوک':
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, 'شلیکت نشست!')
        elif player[4] == 'پدرخوانده':
            godfatherJacket = fetchvalue(gameId, 'games_info', 'god_father_jacket')
            if str(godfatherJacket) == '1':
                remove(bot,gameId,playerId,nightDead=1)
                leonBullet(gameId)
                bot.send_message(call.from_user.id, 'شلیکت نشست!')
            else:
                leonBullet(gameId)
                trueFalse(gameId, 'games_info', 'god_father_jacket', 'true')
                bot.send_message(call.from_user.id, 'شلیکت نشست!')
        elif player[3] == 'شهروند':
            leon = fetchWithPId(gameId, 'games_info', str(call.from_user.id))
            playerId = {'id': leon[0]}
            remove(bot,gameId,playerId,nightDead=1)
            bot.send_message(call.from_user.id, 'شلیکت بد نشست!')

def Matador(bot,call,gameId):
    handCuffed=existence(gameId,'hand_cuffed','player_id',str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players=fetchPlayer(gameId,'games_players')
        for player in players:
            if player['role'] != 'پدرخوانده' and player['role'] != 'ماتادور' and player['role'] != 'ساول گودمن':
                Btn = InlineKeyboardButton(player['name'], callback_data=f'matador_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای دستبند بزنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyMatador(bot,call,player,gameId):
    mafias = fetchPlayer(gameId, 'mafias')
    for mafia in mafias:
        caller = [p for p in mafias if p[0] == str(call.from_user.id)]
        caller = caller[0]
        caller=fetchWithPId(gameId,'games_players',caller[0])
        if mafia[0] != str(call.from_user.id):
            bot.send_message(mafia[0], f'{caller[1]} به {player[1]} دستبند زد')
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        insertBinaryTable(gameId,'hand_cuffed',player[0])
    bot.send_message(call.from_user.id,'اوکی فهمیدم ماتادور')


def Sual(bot,call,gameId):
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        players = fetchPlayer(gameId, 'games_players')
        for player in players:
            if player['role'] != 'پدرخوانده' and player['role'] != 'ماتادور' and player['role'] != 'ساول گودمن':
                Btn = InlineKeyboardButton(player['name'], callback_data=f'sual_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای خریداری کنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifySual(bot,player,gameId):
    mafias=fetchPlayer(gameId,'mafias')
    if player[4] == 'شهروند ساده':
        sualPurchese(gameId,player[0])
        bot.send_message(player[0],'نقش تو از بازی خارج شد و الان مافیای ساده هستی! ساول گودمن تو رو خریداری کرد')
        for mafia in mafias:
            bot.send_message(mafia[0],f' جز تیم مافیا شد.{player[1]}خریداری انچام شد! اکنون ')
    else:
        for mafia in mafias:
            bot.send_message(mafia[0],'متاسفانه خریداری نشسته نشد!')

def Doctor(bot,call,gameId):
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
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای نجات بدی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')

def VerifyDoctor(bot,call,player,gameId):
    exist=existence(gameId,'deads','player_id',player[0])
    if exist:
            deleteRows('deads','player_id',player[0])
            player={'id': player[0],'name': player[1], 'user': player[2],
                              'side': player[3], 'role': player[4], 'link': player[5], 'votes': 0,}
            insertGP(gameId,'games_players',player)
            if player['side'] == 'مافیا':
                insertBinaryTable(gameId,'mafias',player['id'])
            bot.send_message(call.from_user.id, 'خیلی خب دکی جون بخواب')
    else:
        bot.send_message(call.from_user.id, 'خیلی خب دکی جون بخواب')

def Leon(bot,call,gameId):
    bullet=fetchvalue(gameId,'games_info','leon_bullet')
    if int(bullet)>0:
        handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
        if handCuffed == False:
            markup = InlineKeyboardMarkup()
            players = fetchPlayer(gameId, 'games_players')
            for player in players:
                if player['role'] != 'لئون':
                    Btn = InlineKeyboardButton(player['name'], callback_data=f'leon_{gameId}_{player['id']}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که تیر بزنی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')
    else:
        bot.send_message(call.from_user.id,'تیرهات تموم شده مرد! دیگه پیر شدی...')


def Kein(bot,call,gameId):
        handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
        if handCuffed == False:
            markup = InlineKeyboardMarkup()
            players = fetchPlayer(gameId, 'games_players')
            for player in players:
                if player['role'] != 'شهروند کین':
                    Btn = InlineKeyboardButton(player['name'], callback_data=f'kein_{gameId}_{player['id']}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که باهاش ملاقات کنی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')



def VerifyKein(bot,call,player,gameId):
    if player[3] == 'مافیا':
        insertBinaryTable(gameId,'kein_meets',player[0])
        trueFalse(gameId,'games_info','kein_meeting','true')
        bot.send_message(call.from_user.id, 'تحقیقاتت انجام شد! اگه درست باشه نتیجه رو روز میگم بهت')
    else:
        bot.send_message(call.from_user.id,'تحقیقاتت انجام شد! اگه درست باشه نتیجه رو روز میگم بهت')


def Constantine(bot,call,gameId):
    trueFalse(gameId, 'games_info', 'pick', 'true')
    handCuffed = existence(gameId, 'hand_cuffed', 'player_id', str(call.from_user.id))
    if handCuffed == False:
        markup = InlineKeyboardMarkup()
        deads = fetchPlayer(gameId, 'deads')
        for player in deads:
            if player['role'] != 'کنستانتین':
                Btn = InlineKeyboardButton(player['name'], callback_data=f'constantine_{gameId}_{player['id']}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای از کسایی مردند نجات بدی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')



def VerifyConstantine( player,gameId):
    trueFalse(gameId,'games_info','constantine_birth','true')
    deleteRows("deads",'player_id',player[0])
    player={'id':player[0],'name':player[1],'user':player[2],
            'side':player[3],'role':player[4],'link':player[5],'votes':0}
    insertGP(gameId,'games_players',player)

def Ending(bot,chatId,gameId):
    endGame(gameId)
    pRoleList = fetchall(gameId, 'games_players')
    for P in pRoleList:
        id = P[0]
        if id != "180477776":
            bot.restrict_chat_member(chatId, id, permissions=allowChatMember)





