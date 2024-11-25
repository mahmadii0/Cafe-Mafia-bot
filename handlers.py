import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import gameLogic
from constants import BotUserIds, PlayerList
from gameLogic import *

callList=[]

def Delete_message(bot,call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
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
        startG(bot, message)


    @bot.message_handler(regexp='اتمام کلام')
    def stopTalk_handler(message):
        StopTalk(message)

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        if call.data == "Add":
            AddPlayer(bot, call)
        elif call.data == "FinalStart":
            FinalStart(bot, call)
        elif call.data == "add_challenge":
            AddChallenge(bot,call)
        elif call.data == "yes_Sherlock":
            Delete_message(bot, call)
            Sherlock(bot,call)
        elif call.data == "no_Sherlock":
            gameLogic.pick=True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه شرلوک جان')
        elif call.data == "salakhi_godFather":
            Delete_message(bot, call)
            Salakhi(bot,call)
        elif call.data == "shelik_godFather":
            Delete_message(bot, call)
            Shelik(bot,call)
        elif call.data == "yes_matador":
            Delete_message(bot, call)
            Matador(bot,call)
        elif call.data == "no_matador":
            gameLogic.pick=True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه ماتادور زرنگ')
        elif call.data == "yes_shelik_matador":
            Delete_message(bot, call)
            ShelikMatador(bot,call)
        elif call.data == "no_shelik_matador":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'اوکی ماتادور از این پس بگذریم')
        elif call.data == "yes_sual":
            Delete_message(bot, call)
            bot.send_message(chatId,' جالب مافیا درحال خریداری است... تازه بازی جذاب داره میشه')
            Sual(bot,call)
        elif call.data == "no_sual":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه ساول گودمن جان')
        elif call.data == "yes_shelik_sual":
            Delete_message(bot, call)
            ShelikSual(bot,call)
        elif call.data == "no_shelik_sual":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'اوکی ساول از این پس بگذریم')
        elif call.data == "yes_simpleMafia":
            Delete_message(bot, call)
            SimpleMafia(bot,call)
        elif call.data == "no_simpleMafia":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه مافیای من')
        elif call.data == "yes_doctor":
            Delete_message(bot, call)
            Doctor(bot,call)
        elif call.data == "no_doctor":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه دکی جان')
        elif call.data == "yes_leon":
            Delete_message(bot, call)
            Leon(bot,call)
        elif call.data == "no_leon":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه لئون حرفه ای')
        elif call.data == "yes_kein":
            Delete_message(bot, call)
            Kein(bot,call)
        elif call.data == "no_kein":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه شهروند کین')
        elif call.data == "yes_constantine":
            Delete_message(bot, call)
            Constantine(bot,call)
        elif call.data == "no_constantine":
            gameLogic.pick = True
            Delete_message(bot, call)
            bot.send_message(call.from_user.id,'باشه کنستانتین الهه تولد')
        elif call.data == f'Yes_forInquiry':
            VerifyInquiryRequest(bot, call)

        for Player in PRoleList:
            if call.data == Player['id']:
                challengePlayer(bot,call, Player)
            elif call.data == f'Sherlock_{Player["id"]}':
                Delete_message(bot, call)
                VerifySherlockSalakhi(bot,call,Player)
            elif call.data == f'Godfather_salakhi_{Player["id"]}':
                Delete_message(bot, call)
                VerifyGodfatherSalakhi(bot, call, Player)
            elif call.data == f'Godfather_shelik_{Player["id"]}':
                Delete_message(bot, call)
                VerifyGodfatherShelik(bot, call, Player)
            elif call.data == f'Matador_{Player["id"]}':
                Delete_message(bot, call)
                VerifyMatador(bot, call, Player)
            elif call.data == f'matador_shelik_{Player["id"]}':
                Delete_message(bot, call)
                VerifyMatadorShelik(bot, call, Player)
            elif call.data == f'Sual_{Player["id"]}':
                Delete_message(bot, call)
                VerifySual(bot, call, Player)
            elif call.data == f'sual_shelik_{Player["id"]}':
                Delete_message(bot, call)
                VerifyShelikSual(bot, call, Player)
            elif call.data == f'SimpleMafia_shelik_{Player["id"]}':
                Delete_message(bot, call)
                VerifySimpleMafiaShelik(bot, call, Player)
            elif call.data == f'doctor_{Player["id"]}':
                    Delete_message(bot, call)
                    VerifyDoctor(bot, call, Player)
            elif call.data == f'Leon_{Player["id"]}':
                Delete_message(bot, call)
                VerifyLeon(bot, call, Player)
            elif call.data == f'Kein_{Player["id"]}':
                Delete_message(bot, call)
                VerifyKein(bot, call, Player)
            elif call.data == f'Constantine_{Player["id"]}':
                Delete_message(bot, call)
                VerifyConstantine(bot, call, Player)
            elif call.data == f'vote_{Player["id"]}':
                CountingVote(bot,call,Player)

            elif call.data == f'blue_{Player["id"]}':
                if str(call.from_user.id) == Player['id']:
                #     pList = [player for player in defence if player['id'] == str(call.from_user.id)]
                #     p = pList[0]
                # if call.from_user.id == int(p['id']):
                    Delete_message(bot, call)
                    blueCart(bot, call)
                else:
                    bot.answer_callback_query(callback_query_id=call.id
                                              , text='شما نمی توانید انتخاب کنید'
                                              , show_alert=True)
            elif call.data == f'red_{Player["id"]}':
                if str(call.from_user.id) == Player['id']:
                    Delete_message(bot, call)
                    redCart(bot, call)
                else:
                    bot.answer_callback_query(callback_query_id=call.id
                                              , text='شما نمی توانید انتخاب کنید'
                                              , show_alert=True)



