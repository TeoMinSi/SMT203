import os
import sys
from threading import Thread
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,InlineQueryHandler, BaseFilter, CallbackQueryHandler
import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
import telegram
import re
from flask import Flask
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

# postgres://tdeadiijdpunlj:1121cfc300b659c7dd0e29058e741fc11159621f9dae412261b0c990848ba3e2@ec2-184-72-236-3.compute-1.amazonaws.com:5432/d9h6dl82nd2t0f
#sean token
#api_token = "1037359019:AAGurnQOCnm5Rhvgc9aqne1OYj_zK1zCbRk" 
#minsi token
api_token = '815123050:AAGYmp4G3WQRs2DkGBlyCfedF7yIJXKGH9A'

app = Flask(__name__)
introtext = 'Hi there SMUgger!!! I can estimate how full study spots are, just answer some questions for me!\nFeel free to /restart anytime should you want to start over!'
whattime = 'At which timing do you want me to estimate? Enter in HH:MM in 24hours format.'
whichschooltext = 'Which building do you want to study at?'
whichleveltext = 'Which floor are you on?'
holdonahbrosis = 'Hold on ah Bro/Sis let me compute in my brain first'
occupancy_output_level2 = "Here are the results!!!\nThe current occupancy of SIS Level 2 study areas are as follows:\nOutside GSR 2-1: 6/8 (75%)\nLong corridor outside SRs: 45/50 (90%)"
looksfulltext = 'Oh no! Looks like SIS Level 2 might be full currently. Would you like me to suggest elsewhere in SIS?\nIf you would like me to stop, send /stop'
alternativesuggestiontext = 'Ok! I will let you know of another place in SIS.'
alternativeanswertext = 'Here are the results!!!\nHere are the top 3 most empty study areas in SIS:\nOutside GSR3-1: 9/24 (38%)\nLong corridor outside SRs: 20/50 (40%)\nProject Way: 45/70 (64%)'
forecast_output = "Here are the results!!!\nThe predicted occupancy rates of SIS Level 2 on Thursday at 15:00 are as follows:\nOutside GSR 2-1: 5/8 (63%)\nLong corridor outside SRs: 36/50 (72%)"
end = "Happy studying!\nIf you need my help again, feel free to /start me!"
askday = "Which day do you want to forecast?"
asktime = "What time of the day do you want to forecast? Enter in HH:MM in 24hours format"

updater = Updater(api_token, use_context=True)
dp = updater.dispatcher
forecast = False
suggest = False
school = ''
level = ''
fday  = ''
ftime = ''

location_keyboard = [["Connexion"], ['KGC'], ['LKS Library'],['SIS'], ['SOA'], ['SOB'],['SOE/SOSS'],['SOL']]
type_keyboard = [['Show current crowd level', "Forecast crowds"]]
level_keyboard = [['Level 5'], ['Level 4'], ['Level 3'], ['Level 2'], ["Level B1"]]
suggest_keyboard = [["Find me alternatives!"], ["/stop"]]
day_keyboard = [["Mon", "Tue", "Wed", "Thur", "Fri"]]

@app.route("/query_test/", methods=["GET"])
def reply():
    name = request.json["name"]
    print(name)
    if name:
        test = db.session.query(maindb).filter(maindb.c.mac_address=="8b20d37d47b52b298444971325218e759b516057").first()
        print(test[3])
        return (jsonify({"result": test[3]}), 201)
    else:
        return (jsonify({"result": "it works"}), 200)

def begin():

    global forecast
    global suggest
    global school
    global level

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def reset(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    def start(update, context):
        global forecast 
        global school
        global suggest
        global level
        global ftime
        global fday
        forecast = False
        suggest = False
        school = ''
        level = ''
        ftime = ""
        fday = ""
        update.message.reply_text(introtext)
        update.message.reply_text("What would you like me to do?", reply_markup=ReplyKeyboardMarkup(type_keyboard, resize_keyboard=True, one_time_keyboard=True))

    def restart(update, context):
        global forecast 
        global school
        global suggest
        global level 
        global ftime
        global fday
        forecast = False
        suggest = False
        school = ''
        level = ''
        ftime = ""
        fday = ""
        update.message.reply_text(introtext)
        update.message.reply_text("What would you like me to do?", reply_markup=ReplyKeyboardMarkup(type_keyboard, resize_keyboard=True, one_time_keyboard=True))

    def stop(update, context):
        update.message.reply_text(end)

    class ForecastTrue(BaseFilter):
        def filter(self, message):
            return message.text is not None and message.text == "Forecast crowds"
    forecasttrue = ForecastTrue()

    class ForecastFalse(BaseFilter):
        def filter(self, message):
            return message.text is not None and message.text == "Show current crowd level"
    forecastfalse = ForecastFalse()

    class checkType(BaseFilter):
        def filter(self, message):
            return message.text is not None and (message.text == "Show current crowd level" or message.text == "Forecast crowds")
    checkf = checkType()

    def setType(update, context):
        global forecast
        if update.message.text == "Forecast crowds":
            forecast = True
            update.message.reply_text("You have set forecast to True")
        elif update.message.text == "Show current crowd level":
            forecast = False
            update.message.reply_text("You have set forecast to False")

    def askLocation(update, context):
        if forecast:
            global ftime
            ftime = update.message.text
        update.message.reply_text(whichschooltext, reply_markup=ReplyKeyboardMarkup(location_keyboard, one_time_keyboard=True))

    class SchoolFilter(BaseFilter):
        def filter(self, message):
            l = ["Connexion", 'KGC', 'LKS Library', 'SIS', 'SOA', 'SOB','SOE/SOSS','SOL']
            return message.text is not None and message.text in l
    schoolf = SchoolFilter()

    def askLevel(update, context):
        global school
        school = update.message.text
        update.message.reply_text(whichleveltext, reply_markup=ReplyKeyboardMarkup(level_keyboard, resize_keyboard=True, one_time_keyboard=True))

    class LevelFilter(BaseFilter):
        def filter(self, message):
            return message.text is not None and message.text in ['Level 5', 'Level 4', 'Level 3', 'Level 2', "Level B1"]
    levelf = LevelFilter()

    def crowdlevel(update, context):
        update.message.reply_text(holdonahbrosis)
        global level
        level = update.message.text
        # add in query to database
        if forecast:
            update.message.reply_text(forecast_output)
            update.message.reply_text(end)
        else:
            update.message.reply_text(occupancy_output_level2)
            update.message.reply_text(looksfulltext, reply_markup=ReplyKeyboardMarkup(suggest_keyboard, one_time_keyboard=True))

    class Suggest_Filter(BaseFilter):
        def filter(self, message):
            return message.text is not None and message.text == "Find me alternatives!"
    suggestf = Suggest_Filter()

    def suggestion(update, context):
        update.message.reply_text(alternativesuggestiontext)
        update.message.reply_text(alternativeanswertext)
        update.message.reply_text(end)
    
    def whichDay(update, context):
        global forecast
        forecast = True
        update.message.reply_text(askday, reply_markup=ReplyKeyboardMarkup(day_keyboard, resize_keyboard=True, one_time_keyboard=True))
    
    class DayFilter(BaseFilter):
        def filter(self, message):
            return message.text is not None and message.text in ["Mon", "Tue", "Wed", "Thur", "Fri"]
    dayf = DayFilter()

    def whatTime(update, context):
        global fday
        fday = update.message.text
        update.message.reply_text(asktime, reply_markup=ReplyKeyboardRemove())

    class TimeFilter(BaseFilter):
        def filter(self, message):
            pattern = re.compile("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
            return message.text is not None and bool(re.search(pattern, message.text))
    timef = TimeFilter()

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler('r', reset))
    dp.add_handler(CommandHandler("restart", restart))
    dp.add_handler(CommandHandler("stop", stop))
    # dp.add_handler(MessageHandler(checkf, setType))

    dp.add_handler(MessageHandler(forecasttrue, whichDay))
    dp.add_handler(MessageHandler(dayf, whatTime))
    dp.add_handler(MessageHandler(timef, askLocation))
    dp.add_handler(MessageHandler(schoolf, askLevel))
    
    dp.add_handler(MessageHandler(forecastfalse, askLocation))
    dp.add_handler(MessageHandler(levelf, crowdlevel))
    dp.add_handler(MessageHandler(suggestf, suggestion))
        
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    begin()