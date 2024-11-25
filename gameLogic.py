import random
import time
import telebot
from requests import delete
from telebot.apihelper import delete_message, send_message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from constants import PlayerList, Rolelist, BotUserIds
import asyncio


playerNames = []
PlayerIds = []
chatId = ''
PRoleList = []
SalakhiList=[]
Old_SalakhiList=[]
DeadList=[]
Old_DeadList=[]
DastbandList=[]
Links = []
mafias=[]
ChallengeRequests=[]
challenger=[]
playerChallenger=[]
Selector=[]
stopTalk = False
stopTask= False
challenge= False
challengeOn=False
blindNight=False
deleteVoteMessage=False
NumOfVote=0
Voter={}
defence=[]

inqueryRequest=2
night=0
day=0

pick = False
GodfatherJacket= False
SualPurchase=False
LeonJacket= False
DoctorSelfSave= False
KeinMeeting=[]
ConstantineBirth=False
LeonBullet=2
def startG(bot,message):
    global chatId
    chatId = message.chat.id
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


def AddPlayer(bot,call):
    if len(PlayerList) < 11:
        if call.from_user.id in BotUserIds:
            playerId=str(call.from_user.id)
            playerUser = call.from_user.username
            PlayerName=call.from_user.first_name
            if playerUser not in PlayerList:
                PlayerList.append({'name':PlayerName,'user':playerUser,'id':playerId},)
            PlayerLink = f'<a href="https://t.me/{playerUser}">{PlayerName}</a>'
            Links.append(PlayerLink)

            text = f"""به به چه دوستانی قراره دورهم مافیا بازی کنن!😎
            برای شرکت تو بازی، روی دکمه من هستم کلیک کنین تا این سناریو جذاب رو بازی کنیم!
            سناریو: پدرخوانده3
            تعداد شهروندان(دکتر،لئون،کین،کنستانتین،ساده): 7
            تعداد مافیا(پدرخوانده،ماتادور،ساول گودمن): 3
            نقش مستقل(شرلوک): 1
            *اگر بازی رو نمی دونید و آَشنایی ندارید از دستور /helpG استفاده کنید تا توضیح بدم.
            لیست بازیکنان:\n
            {Links}
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
                                        ,text='دوست عزیز شما ربات را استارت نکرده اید!'
                                        ,show_alert=True)


def FinalStart(bot,call):
        UserId=call.from_user.id
        ChatId=call.message.chat.id
        ChatMember=bot.get_chat_member(chat_id=ChatId,user_id=UserId)
        if ChatMember.status in ['administrator', 'creator']:
            if len(PlayerList) == 11:
                bot.answer_callback_query(callback_query_id=call.id
                                          , text='بازی شروع شد!'
                                          , show_alert=True)
                bot.delete_message(ChatId,call.message.message_id)
                Operations(bot,PlayerList,ChatId)
            else:
                bot.answer_callback_query(callback_query_id=call.id
                                          ,text='تعداد به حد نصاب نرسیده است!'
                                          ,show_alert=True)
        else:
            bot.answer_callback_query(callback_query_id=call.id
                                      , text='شما مجوز شروع بازی را ندارید!',
                                      show_alert=True)

def StopTalk(message):
    global stopTalk
    stopTalk = True


def Operations(bot,PlayerList, ChatId):
    chatId = ChatId
    randomRole = random.sample(Rolelist, len(PlayerList))
    for Player, Role in zip(PlayerList, randomRole):

        PlayerRole = {'name': Player['name'], 'id': Player['id']
            , 'user': Player['user'], 'side': '', 'role': Role}
        if (PlayerRole['role'] == 'پدرخوانده'
                or PlayerRole['role'] == 'ماتادور' or PlayerRole['role'] == 'ساول گودمن'):
            PlayerRole['side'] = 'مافیا'
        elif PlayerRole['role'] == 'شرلوک':
            PlayerRole['side'] = 'شرلوک'
        else:
            PlayerRole['side'] = 'شهروند'

        PRoleList.append(PlayerRole)
    global mafias
    mafias = [mafia for mafia in PRoleList if mafia['side'] == 'مافیا']
    blindFunc(bot, chatId)


def blindFunc(bot, ChatId):
    Links.clear()
    for P in PRoleList:
        id = P['id']
        PlayerIds.append(id)
    RestrictChatMember = telebot.types.ChatPermissions(can_send_messages=False)
    for id in PlayerIds:
        if id != "180477776":
            bot.restrict_chat_member(ChatId, id, permissions=RestrictChatMember)
    for P in PRoleList:
        role = P['role']
        bot.send_message(P['id'], f"""نقش شما دوست عزیز🗿: {role}""")
    bot.send_message(ChatId, """به همگی دوستان داخل بازی خوش آمد میگم😎
    از اینکه قراره یک بازی لذت بخش با شما رو داشته باشم خشنودم🪶
    دوستان نقش ها داخل پیوی شما توسط من اعلام شده و اکنون روز بلایند(ناآگاهی یا کوری) رو تا 5 ثانیه دیگه شروع می کنیم. اگر صحبت شما تمام شد با نوشتن کلمه اتمام کلام من رو آگاه کنید""")
    Chat(bot,ChatId)
    bot.send_message(ChatId,'شب آغاز شد... شهر به خواب بره...🌙')
    global challenge
    challenge=True
    Night(bot,ChatId)


def Wait(seconds):
    end_time = time.time() + seconds
    while time.time() < end_time:
        if stopTalk:
            break
        if stopTask:
            break
        time.sleep(0.1)

def InquiryRequest(bot,chatId):
    global pick
    global NumOfVote
    global inqueryRequest
    if inqueryRequest>0:
        global Voter
        pick=False
        HalfNumRole = len(PRoleList) // 2
        markup = InlineKeyboardMarkup()
        yesBtn = InlineKeyboardButton('بله', callback_data=f'Yes_forInquiry')
        markup.add(yesBtn)
        message = bot.send_message(chatId, f'🔴آیا استعلام میخواین؟', reply_markup=markup)
        Wait(20)
        if pick == False:
            bot.delete_message(chatId, message.message_id)
        else:
            pass
        if len(Voter) >= HalfNumRole:
            inqueryRequest-=1
            mafia=[mafias for mafias in DeadList if mafias['side']=='مافیا']
            citizen=[citizens for citizens in DeadList if citizens['side']=='شهروند']
            sherlock=[sherlock for sherlock in DeadList if sherlock['side']=='شرلوک']
            bot.send_message(chatId,f'از بازی شما {len(citizen)} شهروند، {len(mafia)} مافیا بیرون رفتند')
            if sherlock:
                bot.send_message(chatId,'و همچنین از بالا خبر رسید شرلوک هم از بازی بیرون رفته!')
            Voter.clear()
            Links.clear()
        else:
            bot.send_message(chatId,'خیلی خب پس استعلام گرفته نمیشه!')
        Voter.clear()
        Links.clear()

    else:
        bot.send_message(chatId,'خب استعلامم که تموم شده...')
def VerifyInquiryRequest(bot,call):
    global Voter
    if call.from_user.id not in Voter:
        Voter.add(call.from_user.id)
        print(Voter)
        playerUser = call.from_user.username
        playerName = call.from_user.first_name
        bot.answer_callback_query(callback_query_id=call.id
                                        , text='رای شما ثبت شد'
                                        , show_alert=True)
        markup = InlineKeyboardMarkup()
        yesBtn = InlineKeyboardButton('بله', callback_data=f'Yes_forInquiry')
        markup.add(yesBtn)
        PlayerLink = f'<a href="https://t.me/{playerUser}">{playerName}</a>'
        Links.append(PlayerLink)
        text=f'''🔴آیا استعلام میخواین؟
        لیست درخواست کنندگان:
        {Links}'''
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=markup, parse_mode='HTML')
    else:
        bot.answer_callback_query(callback_query_id=call.id
                                        , text='شما نمی توانید مجددا درخواست دهید'
                                        , show_alert=True)


def Challenge(P, bot, chatId):
    global playerChallenger
    playerChallenger.append(P)
    player = P
    markup = InlineKeyboardMarkup()
    add_btn = InlineKeyboardButton('من میخوام', callback_data='add_challenge')
    markup.add(add_btn)
    bot.send_message(chatId, f'''کی از {player["name"]} 🟠چالش میخواد؟''', reply_markup=markup)
    Wait(5)


def AddChallenge(bot, call):
    global ChallengeRequests
    userid = str(call.from_user.id)
    p = [P for P in PRoleList if str(P['id']) == userid]
    player=p[0]
    if player:
        ChallengeRequests.append(player)
        markup = InlineKeyboardMarkup()
        add_btn = InlineKeyboardButton('من میخوام', callback_data='add_challenge')
        markup.add(add_btn)
        for CR in ChallengeRequests:
            id = str(CR['id'])
            name_btn = InlineKeyboardButton(CR['name'], callback_data=id)
            markup.add(name_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'''🟠کی از {player["name"]} چالش میخواد؟
                              
لیست کسایی که ازت چالش می‌خوان:                              
''', reply_markup=markup)


def challengePlayer(bot, call, PLayer):
    global challengeOn
    global challenger
    global playerChallenger
    pC = playerChallenger[0]
    if str(call.from_user.id) == str(pC['id']):
        challenger.append(PLayer)
        challengeOn = True
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'چالش انتخاب شد!')
    else:
        bot.answer_callback_query(callback_query_id=call.id, text='درخواست پیدا نشد است', show_alert=True)


def ApplyChallenge(bot, chatId):
    global stopTalk
    global challenger

    if not challenger:
        bot.send_message(chatId, 'هیچ چالشی در حال حاضر وجود ندارد.')
        return

    challengerPlayer = challenger[0]
    allow_chat_member = telebot.types.ChatPermissions(can_send_messages=True)
    restrict_chat_member = telebot.types.ChatPermissions(can_send_messages=False)

    if challengerPlayer['id'] != "180477776":
        bot.restrict_chat_member(chatId, challengerPlayer['id'], permissions=allow_chat_member)

    bot.send_message(chatId, f'نوبت چالشی که به دوست‌مون {challengerPlayer["name"]} دادند. بفرمایید صحبت کنید!')
    stopTalk = False
    Wait(30)

    if challengerPlayer['id'] != "180477776":
        bot.restrict_chat_member(chatId, challengerPlayer['id'], permissions=restrict_chat_member)

    bot.send_message(chatId, f'دوست عزیز زمان چالش شما تمام شد!')
    challenger.remove(challengerPlayer)
    stopTalk = False
    time.sleep(1.5)


def Chat(bot,chatId):
    global stopTalk
    global challengeOn
    startPlay = False
    time.sleep(5)
    endTime = time.time() + 61
    RestrictChatMember = telebot.types.ChatPermissions(can_send_messages=False)
    AllowChatMember = telebot.types.ChatPermissions(can_send_messages=True)
    for P in PRoleList:
        if challenge:
            Challenge(P,bot,chatId)
        if P['id'] != "180477776":
            bot.restrict_chat_member(chatId, P['id'], permissions=AllowChatMember)
        if startPlay == False:
            bot.send_message(chatId, f'خب شروع می کنیم از {P["name"]} بفرمایید صحبت کنید: ')
            startPlay = True
        else:
            bot.send_message(chatId, f'دوست عزیز {P["name"]} بفرمایید صحبت کنید: ')
        stopTalk = False
        Wait(61)
        if P['id'] != "180477776":
            bot.restrict_chat_member(chatId, P['id'], permissions=RestrictChatMember)
        bot.send_message(chatId, f'دوست عزیز زمان صحبت شما تمام شد!')
        stopTalk = False
        ChallengeRequests.clear()
        playerChallenger.clear()
        time.sleep(2)
        if challengeOn:
            ApplyChallenge(bot,chatId)
            challengeOn=False
        challenger.clear()

def Voting(bot,chatId):
    global NumOfVote
    global Voter
    HalfNumRole=len(PRoleList)//2
    for P in PRoleList:
        markup= InlineKeyboardMarkup()
        voteBtn= InlineKeyboardButton('رای میدم',callback_data=f'vote_{P["id"]}')
        markup.add(voteBtn)
        message=bot.send_message(chatId,f'{P["name"]}رای گیری می کنیم برای',reply_markup=markup)
        Wait(10)
        bot.delete_message(chatId,message.message_id)
        if NumOfVote>=HalfNumRole:
            player={'name': P['name'], 'id': P['id']
            , 'user': P['user'], 'side': P['side'], 'role': P['role'],'Votes': NumOfVote}
            defence.append(player)
        NumOfVote = 0
        Voter.clear()
        Links.clear()
    Defence(bot,chatId,HalfNumRole)


def CountingVote(bot,call,P):
    global NumOfVote
    global Voter
    # if call.from_user.id not in Voter:
    Voter.add(call.from_user.id)
    NumOfVote+=1
    if NumOfVote==11 :
        TrueNum=NumOfVote-10
        NumOfVote=TrueNum
    playerUser = call.from_user.username
    playerName = call.from_user.first_name
    bot.answer_callback_query(callback_query_id=call.id
                                   , text='رای شما برای ایشان ثبت شد'
                                   , show_alert=True)

    PlayerLink = f'<a href="https://t.me/{playerUser}">{playerName}</a>'
    Links.append(PlayerLink)
    text = f'''\n {P["name"]}رای گیری می کنیم برای  
    لیست رای دهندگان:
    {Links}'''
    markup = InlineKeyboardMarkup()
    voteBtn = InlineKeyboardButton('رای میدم', callback_data=f'vote_{P["id"]}')
    markup.add(voteBtn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup, parse_mode='HTML')

def Defence(bot,chatId,HalfNumRole):
    Links.clear()
    global stopTalk
    global NumOfVote
    global Voter
    if len(defence)>0:
            RestrictChatMember = telebot.types.ChatPermissions(can_send_messages=False)
            AllowChatMember = telebot.types.ChatPermissions(can_send_messages=True)
            for P in defence:
                if P['id'] != "180477776":
                    bot.restrict_chat_member(chatId, P['id'], permissions=AllowChatMember)
                bot.send_message(chatId,f'خب دوست عزیز {P["name"]} شما اومدید توی دفاعیه! شروع کنید و اگه دفاع تون زودتر تموم میشه از همون کلمه ی اتمام کلام استفاده کنید')
                stopTalk = False
                Wait(75)
                if P['id'] != "180477776":
                    bot.restrict_chat_member(chatId, P['id'], permissions=RestrictChatMember)
                bot.send_message(chatId, f'دوست عزیز زمان دفاع شما تمام شد!')
                stopTalk =False
    Wait(2)
    for P in defence:
        global NumOfVote
        NumOfVote=0
        markup= InlineKeyboardMarkup()
        voteBtn= InlineKeyboardButton('رای میدم',callback_data=f'vote_{P["id"]}')
        markup.add(voteBtn)
        bot.send_message(chatId,f'{P["name"]}رای گیری می کنیم برای ',reply_markup=markup)
        Wait(6)
        if NumOfVote==0:
            defence.remove(P)
        else:
            P['Votes']=NumOfVote
        NumOfVote=0
        Voter.clear()
        Links.clear()
    RemovePlayer(bot,chatId,HalfNumRole)


def RemovePlayer(bot,chatId,HalfNumRole):
    global stopTalk
    global Selector
    if len(defence) == 1:
        defender=defence[0]
        if defender['Votes']>=HalfNumRole:
            DeadList.append(defender)
            Dlist = [player for player in PRoleList if player["id"] == defender["id"]]
            player=Dlist[0]
            PRoleList.remove(player)
            bot.send_message(chatId,f'خب پس طبق نتیجه {defender["name"]}از بازی خارج میشن')
        else:
            bot.send_message(chatId, f'خب پس طبق نتیجه {defender["name"]}از بازی خارج نمیشن')
    elif len(defence)==2:
        defender1=defence[0]
        defender2=defence[1]
        if defender1['Votes']>defender2['Votes']:
            DeadList.append(defender1)
            Dlist = [player for player in PRoleList if player["id"] == defender1["id"]]
            player = Dlist[0]
            PRoleList.remove(player)
            bot.send_message(chatId,f'خب پس طبق نتیجه {defender1["name"]}از بازی خارج میشن')
        elif defender1['Votes']<defender2['Votes']:
            DeadList.append(defender2)
            Dlist = [player for player in PRoleList if player["id"] == defender2["id"]]
            player=Dlist[0]
            PRoleList.remove(player)
            bot.send_message(chatId,f'خب پس طبق نتیجه {defender2["name"]}از بازی خارج میشن')
        elif defender1['Votes']==defender2['Votes']:
            selector=random.choice([defender1['name'],defender2['name']])
            p=[player for player in defence if player["name"] == selector]
            player=p[0]
            Selector.append(player)
            bot.send_message(chatId, 'خب مثل اینکه باید بریم واسه قرعه مرگ')
            bot.send_message(chatId, f'{selector}انتخاب باید انتخاب کنه!')
            markup = InlineKeyboardMarkup()
            callbackData1 = random.choice([f'blue_{player["id"]}', f'red_{player["id"]}'])
            callbackData2 = random.choice([f'blue_{player["id"]}', f'red_{player["id"]}'])
            Cart1 = InlineKeyboardButton('کارت اول💀', callback_data=callbackData1)
            Cart2 = InlineKeyboardButton('کارت دوم💀', callback_data=callbackData2)
            markup.add(Cart1)
            markup.add(Cart2)
            bot.send_message(chatId,
                                 'فرعه مرگ به این شکله اونی که من انتخاب می کنم،به من میگه که بین کارت یک و دو کدوم رو انتخاب می کنه و یکی از این ها کارت آبی هست و اگه آبی رو انتخاب کنه توی بازی میمونه ولی اگه قرمز رو انتخاب کنه، دفاع کننده دوم توی بازی میمونه! حالا انتخاب کن کدوم؟',
                                 reply_markup=markup)
            Wait(300)
            stopTalk=False
    elif len(defence)>=3:
        MaxVotes=0
        for P in defence:
            if P['votes']>MaxVotes:
                MaxVotes=P['votes']
        defender=[P for P in defence if P['votes']==MaxVotes]
        if len(defender)==1:
            defender=defence[0]
            DeadList.append(defender)
            Dlist = [player for player in PRoleList if player["id"] == defender["id"]]
            player=Dlist[0]
            PRoleList.remove(player)
            bot.send_message(chatId, f'خب پس طبق نتیجه {defender["name"]}از بازی خارج میشن')
        elif len(defender)==2:
            defender1=defender[0]
            defender2=defender[1]
            selector=random.choice([defender1['name'], defender2['name']])
            p = [player for player in defence if player["name"] == selector]
            player = p[0]
            Selector.append(player)
            bot.send_message(chatId, 'خب مثل اینکه باید بریم واسه قرعه مرگ')
            bot.send_message(chatId, f'{selector}انتخاب باید انتخاب کنه!')
            markup = InlineKeyboardMarkup()
            callbackData1 = random.choice([f'blue_{player["id"]}', f'red_{player["id"]}'])
            callbackData2 = random.choice([f'blue_{player["id"]}', f'red_{player["id"]}'])
            Cart1 = InlineKeyboardButton('کارت اول', callback_data=callbackData1)
            Cart2 = InlineKeyboardButton('کارت دوم', callback_data=callbackData2)
            markup.add(Cart1)
            markup.add(Cart2)
            bot.send_message(chatId,
                                 'فرعه مرگ به این شکله اونی که من انتخاب می کنم،به من میگه که بین کارت یک و دو کدوم رو انتخاب می کنه و یکی از این ها کارت آبی هست و اگه آبی رو انتخاب کنه توی بازی میمونه ولی اگه قرمز رو انتخاب کنه، دفاع کننده دوم توی بازی میمونه! حالا انتخاب کن کدوم؟',
                                 reply_markup=markup)
            Wait(300)
            stopTalk=False
        elif len(defender)>=3:
            bot.send_message(chatId, f'طبق نتیجه هیچکدوم از بازی خارج نمیشین!')
    defence.clear()


def blueCart(bot,call):
    global stopTalk
    dList=[defender for defender in defence if defender['id']==str(call.from_user.id)]
    defender=dList[0]
    bot.send_message(chatId,f'بهت تبریک میگم! {defender["name"]} نجات پیدا کردی !')
    defence.remove(defender)
    pDeadList=defence[0]
    player = [player for player in PRoleList if player["id"] == pDeadList["id"]]
    PRoleList.remove(player[0])
    DeadList.append(player[0])
    stopTalk = True

def redCart(bot,call):
    global stopTalk
    dList = [defender for defender in defence if defender['id'] == str(call.from_user.id)]
    defender = dList[0]
    bot.send_message(chatId,f'بخت باهات یار نبود متاسانه! {defender["name"]} از بازی اخراجی!')
    DeadList.append(defender)
    p = [player for player in PRoleList if player["id"] == defender["id"]]
    player = p[0]
    PRoleList.remove(player)
    stopTalk=True


def mafiaChat(bot):
    class ChatState:
        active = True

    CHAT_DURATION = 30
    mafiaMessages = {}

    # Notify start
    if blindNight==False:
        for mafia in mafias:
            otherMafia = [f"{member['name']} ({member['role']})" for member in mafias if member["id"] != mafia["id"]]
            message = "\n\nاعضای دیگر مافیا:\n" + "\n".join(otherMafia)
            bot.send_message(mafia["id"], message)
    else:
        pass

    # Instead of managing updates directly, use a message handler
    @bot.message_handler(func=lambda message: ChatState.active)
    def handle_mafia_messages(message):
        # Check if sender is mafia
        if any(int(mafia['id']) == message.from_user.id for mafia in mafias):
            sender_id = message.from_user.id
            sender = next(mafia for mafia in mafias if int(mafia['id']) == sender_id)

            # Store message
            if sender_id not in mafiaMessages:
                mafiaMessages[sender_id] = []
            mafiaMessages[sender_id].append(message.text)

            # Forward to other mafias
            for mafia in mafias:
                other_id = int(mafia['id'])
                if other_id != sender_id:
                    bot.send_message(
                        other_id,
                        f"پیام از {sender['name']}: {message.text}"
                    )

    # Wait for chat duration
    time.sleep(CHAT_DURATION)

    # Deactivate the handler by setting ChatState.active to False
    ChatState.active = False

    # Send end notification
    for mafia in mafias:
            bot.send_message(int(mafia['id']), "🔴زمان چت مافیا به پایان رسید")

    return mafiaMessages


def Night(bot,chatId):
    global pick
    global Old_DeadList
    global Old_SalakhiList
    global blindNight
    Old_DeadList= DeadList.copy()
    Old_SalakhiList= SalakhiList.copy()
    waitTime=10
    if blindNight:
        #sherlock
        sherlock = [player for player in PRoleList if player['role'] == 'شرلوک']
        bot.send_message(chatId, 'شرلوک بیدار شو بیا پیوی مون:)')
        if not sherlock:
            Wait(5)
        else:
            sherlock=sherlock[0]
            sherlockMarkup = InlineKeyboardMarkup()
            yesSherlockBtn= InlineKeyboardButton('آره', callback_data='yes_Sherlock')
            noSherlockBtn= InlineKeyboardButton('نه', callback_data='no_Sherlock')
            sherlockMarkup.add(yesSherlockBtn)
            sherlockMarkup.add(noSherlockBtn)
            message=bot.send_message(sherlock['id'],'شرلوک بیدار شو! آیا امشب میخوای کسی رو سلاخی کنی؟',reply_markup=sherlockMarkup)
            Wait(15)
            if pick==False:
                bot.delete_message(sherlock['id'],message.message_id)

            bot.send_message(sherlock['id'],'شرلوک بخواب راحت باش')

    #Mafia

    godFather = [god for god in mafias if god['role'] == 'پدرخوانده']
    matador = [matador for matador in mafias if matador['role'] == 'ماتادور']
    sualGoodman = [sual for sual in mafias if sual['role'] == 'ساول گودمن']
    simpleMafia=[simple for simple in mafias if simple['role'] == 'مافیا ساده']
    #////////////

    bot.send_message(chatId,'مافیا بیدار شه بیا پیوی بهت مسیج دادم')
    for mafia in mafias:
        bot.send_message(mafia['id'],f'{mafia["role"]} بیدار شو! ده ثانیه زود هرپیامی میخوای بفرست تا یار هات بخونن')
    mafiaChat(bot)

    if blindNight:
        global night
        night=++1
        if not godFather:
            pass
        else:
            pick=False
            godFather = godFather[0]
            godFatherMarkup = InlineKeyboardMarkup()
            salakhiBtn= InlineKeyboardButton('سلاخی می کنم', callback_data='salakhi_godFather')
            shelik=InlineKeyboardButton('شلیک می کنم', callback_data='shelik_godFather')
            godFatherMarkup.add(salakhiBtn)
            godFatherMarkup.add(shelik)
            message=bot.send_message(godFather['id'],'پدرخوانده بازی سلاخی می کنی یا شلیک می کنی؟',reply_markup=godFatherMarkup)
            Wait(waitTime)
            if pick==False:
                bot.delete_message(godFather['id'],message.message_id)
        if not matador:
            pass
        else:
            pick = False
            matador = matador[0]
            if not godFather:
                matadorShelikMarkup = InlineKeyboardMarkup()
                yesMatadorShelik = InlineKeyboardButton('شلیک می کنم', callback_data='yes_shelik_matador')
                noMatadorShelik = InlineKeyboardButton('شلیک نمی کنم', callback_data='no_shelik_matador')
                matadorShelikMarkup.add(yesMatadorShelik)
                matadorShelikMarkup.add(noMatadorShelik)
                message=bot.send_message(matador['id'], 'ماتادور حالا که پدرخوانده نیست تو بگو شلیک می کنی یا نه؟؟',
                                 reply_markup=matadorShelikMarkup)
                Wait(waitTime)
                if pick == False:
                    bot.delete_message(matador['id'], message.message_id)
            pick = False
            matadorMarkup = InlineKeyboardMarkup()
            yesMatadorBtn = InlineKeyboardButton('دستبند میزنم', callback_data='yes_matador')
            noMatadorBtn = InlineKeyboardButton('دستبند نمیزنم', callback_data='no_matador')
            matadorMarkup.add(yesMatadorBtn)
            matadorMarkup.add(noMatadorBtn)
            message=bot.send_message(matador['id'], 'ماتادور، آیا دستبند می زنی؟', reply_markup=matadorMarkup)
            Wait(waitTime)
            if pick==False:
                bot.delete_message(matador['id'],message.message_id)
        if len(mafias)<3 and sualGoodman:
            pick = False
            sualGoodman = sualGoodman[0]
            if not godFather and not matador:
                sualShelikMarkup = InlineKeyboardMarkup()
                yesSualShelik = InlineKeyboardButton('شلیک می کنم', callback_data='yes_shelik_matador')
                noSualShelik = InlineKeyboardButton('شلیک نمی کنم', callback_data='no_shelik_matador')
                sualShelikMarkup.add(yesSualShelik)
                sualShelikMarkup.add(noSualShelik)
                message=bot.send_message(sualGoodman['id'], 'ساول حالا که پدرخوانده نیست تو بگو شلیک می کنی یا نه؟؟',
                                 reply_markup=sualShelikMarkup)
                Wait(waitTime)
                if pick == False:
                    bot.delete_message(sualGoodman['id'], message.message_id)
            pick = False
            sualMarkup = InlineKeyboardMarkup()
            yesSualBtn = InlineKeyboardButton('مذاکره می کنم', callback_data='yes_sual')
            noSualBtn = InlineKeyboardButton('مذاکره نمی کنم', callback_data='no_sual')
            sualMarkup.add(yesSualBtn)
            sualMarkup.add(noSualBtn)
            message=bot.send_message(sualGoodman['id'], 'ساول گودمن، مافیای حیله گر، آیا مذاکره می کنی؟', reply_markup=sualMarkup)
            Wait(waitTime)
            if pick == False:
                bot.delete_message(sualGoodman['id'], message.message_id)
        if simpleMafia and not godFather and not matador and not sualGoodman:
            pick = False
            simpleMafia = simpleMafia[0]
            simpleMafiaMarkup = InlineKeyboardMarkup()
            yesSimpleBtn= InlineKeyboardButton('َشلیک می کنم', callback_data='yes_simpleMafia')
            noSimpleBtn=InlineKeyboardButton('شلیک نمی کنم', callback_data='no_simpleMafia')
            simpleMafiaMarkup.add(yesSimpleBtn)
            simpleMafiaMarkup.add(noSimpleBtn)
            message=bot.send_message(simpleMafia['id'],'مافیا ساده آیا شلیک می کنی؟',reply_markup=simpleMafiaMarkup)
            Wait(waitTime)
            if pick == False:
                bot.delete_message(simpleMafia['id'], message.message_id)
        for mafia in mafias:
            bot.send_message(mafia['id'], f'مافیای جیگر آروم بخواب')

        #Shahrvandan

        #Doctor
        doctor = [doctor for doctor in PRoleList if doctor['role'] == 'دکتر']
        bot.send_message(chatId, 'دکتر بیاد پیوی مریض داریم!')
        if not doctor:
            Wait(5)
        else:
            pick = False
            doctor = doctor[0]
            doctorMarkup = InlineKeyboardMarkup()
            yesDoctorBtn= InlineKeyboardButton('بله', callback_data='yes_doctor')
            noDoctorBtn= InlineKeyboardButton('خیر', callback_data='no_doctor')
            doctorMarkup.add(yesDoctorBtn)
            doctorMarkup.add(noDoctorBtn)
            message=bot.send_message(doctor['id'],'دکتر شهر، آیا کسی رو می خوای نجات بدی؟',reply_markup=doctorMarkup)
            Wait(15)
            if pick == False:
                bot.delete_message(doctor['id'], message.message_id)

        #Leon
        leon = [leon for leon in PRoleList if leon['role'] == 'لئون']
        bot.send_message(chatId, 'لئون حرفه ای مون بیدارشو بیا ببینیم چیکار می کنی!')
        if not leon:
            Wait(5)
        else:
            pick = False
            leon = leon[0]
            leonMarkup = InlineKeyboardMarkup()
            yesleonBtn = InlineKeyboardButton('بله', callback_data='yes_leon')
            noleonBtn = InlineKeyboardButton('خیر', callback_data='no_leon')
            leonMarkup.add(yesleonBtn)
            leonMarkup.add(noleonBtn)
            message = bot.send_message(leon['id'], 'لئون، آیا کسی رو می خوای با تیر بزنی؟', reply_markup=leonMarkup)
            Wait(15)
            if pick == False:
                bot.delete_message(leon['id'], message.message_id)

        #Kein
        kein = [kein for kein in PRoleList if kein['role'] == 'شهروند کین']
        bot.send_message(chatId,'شهروند کین بیدارشو ببینیم استعلام میگیری یا نه!')
        if not kein:
            Wait(6)
        else:
            pick = False
            kein = kein[0]
            if KeinMeeting != None:
                keinMarkup = InlineKeyboardMarkup()
                yesKeinBtn= InlineKeyboardButton('بله', callback_data='yes_kein')
                noKeinBtn= InlineKeyboardButton('خیر', callback_data='no_kein')
                keinMarkup.add(yesKeinBtn)
                keinMarkup.add(noKeinBtn)
                message=bot.send_message(kein['id'],'شهروند کین، آیا کسی رو می خوای استعلام بگیری؟',reply_markup=keinMarkup)
                Wait(15)
                if pick == False:
                    bot.delete_message(kein['id'], message.message_id)
            else:
                bot.send_message(Kein['id'],'خب تو هم که استعلامتو گرفتی دیگه نمیپرسم')
                Wait(7)

        #Constantine
        constantine = [constantine for constantine in PRoleList if constantine['role'] == 'کنستانتین']
        bot.send_message(chatId,'کنستانتین کسی رو میخوای بیاری تو؟پیویم بگو')
        if not constantine:
            Wait(waitTime)
        else:
            constantine = constantine[0]
            if ConstantineBirth == False:
                pick = False
                constantineMarkup = InlineKeyboardMarkup()
                yesConstantineBtn= InlineKeyboardButton('بله', callback_data='yes_constantine')
                noConstantineBtn= InlineKeyboardButton('خیر', callback_data='no_constantine')
                constantineMarkup.add(yesConstantineBtn)
                constantineMarkup.add(noConstantineBtn)
                message=bot.send_message(constantine['id'],'کنستانتین، آیا کسی رو می خوای بیاری داخل ؟',reply_markup=constantineMarkup)
                Wait(15)
                if pick == False:
                    bot.delete_message(constantine['id'], message.message_id)
            else:
                bot.send_message(constantine['id'],'خب تو هم که کارتو کردی بگذریم...')
                Wait(9)

    else:
        blindNight=True
    Day(bot,chatId)

def Day(bot,chatId):
    global day
    global DastbandList
    day=++1
    bot.send_message(chatId,'روز شد! شهر بیدار شه دوستان☀️')
    time.sleep(1)
    DeadPlayers=[DeadP for DeadP in DeadList if DeadP not in Old_DeadList]
    SalakhiPlayers=[SalakhiP for SalakhiP in SalakhiList if SalakhiP not in Old_SalakhiList]
    if len(DeadPlayers) > 0:
        bot.send_message(chatId,'دیشب کشته داشتیم...')
        time.sleep(1)
        for D in DeadPlayers:
            bot.send_message(chatId,f'{D["name"]}کشته دیشب: ')
            PRoleList.remove(D)
            if D['side']=='مافیا':
                mafias.remove(D)
    if len(SalakhiPlayers) > 0:
        if len(DeadPlayers) != 0:
            bot.send_message(chatId,'و سلاخی هم داشتیم دوستان')
        else:
            bot.send_message(chatId, 'ی دیشب سلاخی داشتیم عجب...')
        time.sleep(1)
        for S in SalakhiPlayers:
            bot.send_message(chatId,f'ُسلاخی دیشب: {S["name"]}')

    if len(PRoleList)==len(mafias):
        bot.send_message(chatId, f'دیگه وقتشه اعلام کنم که مافیا بازی رو برد و شهر باخت🔥🔥🔥')
    elif len(mafias)==0:
        bot.send_message(chatId, f'🔥🔥🔥شهر یعنی شماهااا! شهر پیروز شددد')
    DastbandList.clear()
    InquiryRequest(bot,chatId)
    Chat(bot,chatId)
    Voting(bot,chatId)
    Night(bot, chatId)





def Sherlock(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            if P['role'] != 'شرلوک':
                Btn = InlineKeyboardButton(P['name'], callback_data=f'Sherlock_{P["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که سلاخی کنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifySherlockSalakhi(bot,call,Player):
    global pick
    bot.send_message(call.from_user.id,f'''فکر می کنی {Player["name"]} چه نقشی داره؟
لیست نقش ها : {Rolelist}
* باید دقیقا مشابه این ساختار املایی، نقش موردنظرتان را بنویسید''')
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySalakhi(message):
        if message.text == Player['role']:
            s=[sherlock for sherlock in PRoleList if sherlock['role'] == 'شرلوک']
            sherlock=s[0]
            SalakhiList.append(Player)
            PRoleList.remove(Player)
            PRoleList.remove(sherlock)
            ChangedCharacter={'name': sherlock['name'], 'id': sherlock['id'], 'user': sherlock['user'],
                              'side': Player['side'], 'role': Player['role']}
            PRoleList.append(ChangedCharacter)
            if Player['side']=='مافیا':
                mafias.remove(Player)
                mafias.append(ChangedCharacter)

            bot.send_message(call.from_user.id, f'سلاخی درسته و انجام شد.نقش شما از این به بعد: {ChangedCharacter["role"]}')
        else:
            bot.send_message(call.from_user.id,'اشتباه گفتی شرلوک!')


def Salakhi(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            if P['role'] != 'پدرخوانده' and P['role'] != 'ماتادور' and P['role'] != 'ساول گودمن':
                Btn = InlineKeyboardButton(P['name'], callback_data=f'Godfather_salakhi_{P["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که سلاخی کنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')



def VerifyGodfatherSalakhi(bot,call,Player):
    global pick
    bot.send_message(call.from_user.id,f'فکر می کنی {Player["name"]} چه نقشی داره؟')
    @bot.message_handler(func=lambda message: Rolelist )
    def VerifySalakhi(message):
        if message.text == Player['role']:
            SalakhiList.append(Player)
            PRoleList.remove(Player)
            bot.send_message(call.from_user.id, 'سلاخی درسته و انجام شد')
        else:
            bot.send_message(call.from_user.id,'اشتباه گفتی سنیور پدرخوانده!')


def Shelik(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            Btn = InlineKeyboardButton(P['name'], callback_data=f'Godfather_shelik_{P["id"]}')
            markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که بکشی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyGodfatherShelik(bot,call,Player):
    global LeonJacket
    if Player['role'] != 'لئون':
        if Player['role']== 'شرلوک' and night<=2:
            bot.send_message(call.from_user.id,'انجام شد سنیور')
        elif Player['role']=='شرلوک' and night>2:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد سنیور')
        DeadList.append(Player)
        bot.send_message(call.from_user.id, 'انجام شد سنیور')
    else:
        if LeonJacket:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد سنیور')
        else:
            LeonJacket=True
            bot.send_message(call.from_user.id, 'انجام شد سنیور')

def Matador(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            if P['role'] != 'پدرخوانده' and P['role'] != 'ماتادور' and P['role'] != 'ساول گودمن':
                Btn = InlineKeyboardButton(P['name'], callback_data=f'Matador_{P["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای دستبند بزنی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyMatador(bot,call,Player):
    global pick
    if Player not in DastbandList:
        DastbandList.append(Player)
    bot.send_message(call.from_user.id,'اوکی فهمیدم ماتادور')


def ShelikMatador(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            Btn = InlineKeyboardButton(P['name'], callback_data=f'matador_shelik_{P["id"]}')
            markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که بکشی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyMatadorShelik(bot,call,Player):
    global LeonJacket
    if Player['role'] != 'لئون':
        if Player['role']== 'شرلوک' and night<=2:
            bot.send_message(call.from_user.id,'انجام شد ماتادور')
        elif Player['role']=='شرلوک' and night>2:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد ماتادور')
        DeadList.append(Player)
        bot.send_message(call.from_user.id, 'انجام شد ماتادور')
    else:
        if LeonJacket:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد ماتادور')
        else:
            LeonJacket=True
            bot.send_message(call.from_user.id, 'انجام شد ماتادور')


def Sual(bot,call):
    global pick
    pick=True
    if SualPurchase==False:
        if str(call.from_user.id) not in DastbandList:
            markup = InlineKeyboardMarkup()
            for P in PRoleList:
                if P['role'] != 'پدرخوانده' and P['role'] != 'ماتادور' and P['role'] != 'ساول گودمن':
                    Btn = InlineKeyboardButton(P['name'], callback_data=f'Sual_{P["id"]}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای خریداری کنی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')
    else:
        bot.send_message('خب داداش تو که کارتو کردی بخواب!')


def VerifySual(bot,call,Player):
    global pick
    if Player['role']== 'شهروند ساده':
        PRoleList.remove(Player)
        Player['role']='مافیا ساده'
        Player['side']='مافیا'
        PRoleList.append(Player)
        bot.send_message(Player['id'],'نقش تو از بازی خارج شد و الان مافیای ساده هستی! ساول گودمن تو رو خریداری کرد')
        for mafia in mafias:
            bot.send_message(mafia['id'],f' جز تیم مافیا شد.{Player["name"]}خریداری انچام شد! اکنون ')
    else:
        for mafia in mafias:
            bot.send_message(mafia['id'],'متاسفانه خریداری نشسته نشد!')

def ShelikSual(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            Btn = InlineKeyboardButton(P['name'], callback_data=f'sual_shelik_{P["id"]}')
            markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که بکشی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')


def VerifyShelikSual(bot,call,Player):
    global LeonJacket
    if Player['role'] != 'لئون':
        if Player['role']== 'شرلوک' and night<=2:
            bot.send_message(call.from_user.id,'انجام شد ساول')
        elif Player['role']=='شرلوک' and night>2:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد ساول')
        DeadList.append(Player)
        bot.send_message(call.from_user.id, 'انجام شد ساول')
    else:
        if LeonJacket:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد ساول')
        else:
            LeonJacket=True
            bot.send_message(call.from_user.id, 'انجام شد ساول')


def SimpleMafia(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            Btn = InlineKeyboardButton(P['name'], callback_data=f'SimpleMafia_shelik_{P["id"]}')
            markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که بکشی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')



def VerifySimpleMafiaShelik(bot, call, Player):
    global LeonJacket
    if Player['role'] != 'لئون':
        if Player['role']== 'شرلوک' and night<=2:
            bot.send_message(call.from_user.id,'انجام شد مافیاجان')
        elif Player['role']=='شرلوک' and night>2:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد مافیاجان')
        DeadList.append(Player)
        bot.send_message(call.from_user.id, 'انجام شد مافیاجان')
    else:
        if LeonJacket:
            DeadList.append(Player)
            bot.send_message(call.from_user.id, 'انجام شد مافیاجان')
        else:
            LeonJacket=True
            bot.send_message(call.from_user.id, 'انجام شد مافیاجان')


def Doctor(bot,call):
    global pick
    pick=True
    if str(call.from_user.id) not in DastbandList:
        markup = InlineKeyboardMarkup()
        for P in PRoleList:
            global DoctorSelfSave
            if P['id']==str(call.from_user.id) and DoctorSelfSave==True:
                pass
            else:
                Btn = InlineKeyboardButton(P['name'], callback_data=f'doctor_{P["id"]}')
                markup.add(Btn)
        bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای نجات بدی؟', reply_markup=markup)
    else:
        bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')

def VerifyDoctor(bot,call,Player):
    global pick
    if Player['id'] != str(call.from_user.id):
        if Player in DeadList:
            if Player not in SalakhiList:
                DeadList.remove(Player)
                bot.send_message(call.from_user.id, 'خیلی خب دکی جون بخواب')
            else:
                bot.send_message(call.from_user.id,'خیلی خب دکی جون بخواب')
        else:
            bot.send_message(call.from_user.id, 'خیلی خب دکی جون بخواب')
    else:
        global DoctorSelfSave
        if DoctorSelfSave == False:
            DeadList.remove(Player)
            DoctorSelfSave = True
            bot.send_message(call.from_user.id,'خیلی خب دکی جون بخواب')
        else:
            bot.send_message(call.from_user.id, 'دکی تو یبار خودتو نجات دادی!')





def Leon(bot,call):
    global pick
    pick=True
    if LeonBullet>0:
        if str(call.from_user.id) not in DastbandList:
            markup = InlineKeyboardMarkup()
            for P in PRoleList:
                if P['role'] != 'لئون':
                    Btn = InlineKeyboardButton(P['name'], callback_data=f'Leon_{P["id"]}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که تیر بزنی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')
    else:
        bot.send_message(call.from_user.id,'تیرهات تموم شده مرد! دیگه پیر شدی...')


def VerifyLeon(bot,call,Player):
    global pick
    global LeonBullet
    global GodfatherJacket
    if Player['role'] != 'پدرخوانده' and Player['side']!='شهروند':
        if Player['role']== 'شرلوک' and night<=2:
            LeonBullet = LeonBullet - 1
            bot.send_message(call.from_user.id,'شلیکت نشست!')
        elif Player['role']== 'شرلوک' and night>2:
            DeadList.append(Player)
            LeonBullet=LeonBullet-1
            bot.send_message(call.from_user.id,'شلیکت نشست!')
        elif Player['role']!= 'شرلوک':
            DeadList.append(Player)
            LeonBullet = LeonBullet-1
            bot.send_message(call.from_user.id,'شلیکت نشست!')
    elif Player['role'] == 'پدرخوانده':
        if GodfatherJacket:
            DeadList.append(Player)
            LeonBullet = LeonBullet - 1
            bot.send_message(call.from_user.id,'شلیکت نشست!')
        else:
            LeonBullet = LeonBullet-1
            GodfatherJacket = True
            bot.send_message(call.from_user.id,'شلیکت نشست!')
    elif Player['side'] == 'شهروند':
        for P in PRoleList:
            if P['id']==str(call.from_user.id):
                DeadList.append(P)
                bot.send_message(call.from_user.id, 'شلیکت بد نشست!')


def Kein(bot,call):
    global pick
    pick=True
    if len(KeinMeeting)<1:
        if str(call.from_user.id) not in DastbandList:
            markup = InlineKeyboardMarkup()
            for P in PRoleList:
                if P['role'] != 'شهروند کین':
                    Btn = InlineKeyboardButton(P['name'], callback_data=f'Kein_{P["id"]}')
                    markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای که باهاش ملاقات کنی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')
    else:
        p=[player for player in PRoleList if player['id']==str(call.from_user.id)]
        player=p[0]
        DeadList.append(player)
        bot.send_message(call.from_user.id,'خب هم ولاتی چیز همشری جان تو هم که کار خودتو کردی و باید باهم خداحافظی کنیم! بای بای!')


def VerifyKein(bot,call,Player):
    global pick
    if Player['side'] == 'مافیا':
        KeinMeeting.append(Player)
        bot.send_message(call.from_user.id, 'تحقیقاتت انجام شد! اگه درست باشه نتیجه رو روز میگم بهت')
    else:
        bot.send_message(call.from_user.id,'تحقیقاتت انجام شد! اگه درست باشه نتیجه رو روز میگم بهت')


def Constantine(bot,call):
    global pick
    pick=True
    if len(ConstantineBirth)<1:
        if str(call.from_user.id) not in DastbandList:
            markup = InlineKeyboardMarkup()
            for P in DeadList:
                Btn = InlineKeyboardButton(P['name'], callback_data=f'Constantine_{P["id"]}')
                markup.add(Btn)
            bot.send_message(call.from_user.id, 'انتخاب کن کیو میخوای از کسایی مردند نجات بدی؟', reply_markup=markup)
        else:
            bot.send_message(call.from_user.id,'متاسفانه دستبند داری نمی تونی کاری کنی')
    else:
        bot.send_message('خب کنستانتین تو هم که کار خودتو کردی راحت باش')


def VerifyConstantine(bot, call, Player):
    global pick
    global ConstantineBirth
    ConstantineBirth=True
    DeadList.remove(Player)
    PRoleList.append(Player)





