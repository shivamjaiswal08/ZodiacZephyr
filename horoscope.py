import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import *

'''
This project user telebot module to create a telegram bot using python.
OS module is used to read the BOT TOKEN  from .env file.
load_dotenv is used because in normal cases if we want OS module to read the bot token  from env, we have to provide env in environmental path of our device. But using load_dotenv saves us from this hussle.
'''
load_dotenv()
sign_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius','Pisces']

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


user_choice = {}                                # store user_id and sign as key:value pair. 


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello there!!")


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    '''
    Whenever user run the /horoscope command this func will be called.
    This function shows the sign menu and ask the user to select his/her sign by simply clicking on one of the given buttons.
    input -> user's /horoscope command as messsage to use it to get user's id
    output-> none
    '''
    keyboard = [[InlineKeyboardButton("Aries", callback_data='aries')],
                [InlineKeyboardButton("Taurus", callback_data='taurus')],
                [InlineKeyboardButton("Gemini", callback_data='gemini')],
                [InlineKeyboardButton("Cancer", callback_data='Cancer')],
                [InlineKeyboardButton("Leo", callback_data='leo')],
                [InlineKeyboardButton("Virgo", callback_data='virgo')],
                [InlineKeyboardButton("Libra", callback_data='libra')],
                [InlineKeyboardButton("Scorpio", callback_data='scorpio')],
                [InlineKeyboardButton(
                    "Sagittarius", callback_data='sagittarius')],
                [InlineKeyboardButton("Capricorn", callback_data='capricorn')],
                [InlineKeyboardButton("Aquarius", callback_data='aquarius')],
                [InlineKeyboardButton("Pisces", callback_data='pisces')]]

    rp1 = InlineKeyboardMarkup(keyboard, row_width=1)
    sent_msgs = bot.send_message(message.chat.id, "Select your zodiac sign: ",
                                 reply_markup=rp1, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda calls: True)
def button(calls):
    '''
    This func will be called whenever there is a callback from user. Callback occurs everytime user press a button.
    With callback data we get to know user choices.
    input -> calls
    Based on user's input we decide our next step.
    '''
    if calls.data.capitalize() in sign_list:                            #sign_list is global list which contains all the 12 zodiac signs.
        ''' This condition will become true when we show user, the menu of sign_handler().'''
        user_choice[calls.from_user.id] = calls.data                    # storing user's sign with it's id as a key in dictonary user_choice{}

        text = f"Hello {calls.from_user.username}! So you have chosen {user_choice[calls.from_user.id]}."
        sent_msgs = bot.send_message(calls.from_user.id, text)
        choice_handler(calls)
    
    elif calls.data in ['daily', 'weekly', 'monthly']:
        '''This condition will will become true when we show the user menu of choice_handle.'''

        if calls.data == 'daily':
            day_handler(calls)
            
        elif calls.data == 'weekly':
            fetch_horoscope_weekly(calls)

        elif calls.data == 'monthly':
            fetch_horoscope_monthly(calls)
    
    elif calls.data in ['tomorrow', 'today', 'yesterday']:
        '''This conditon will become true when we show the user, menu of day_handler()'''

        fetch_horoscope_daily(calls)

    else:
        bot.send_message(calls.from_user.id, 'Some Error Occurred! \nStart Again!')

def choice_handler(calls):
    ''' This func show user a menu to select its choice. As if user wants to see horoscope on daily basis, weekly or monthly basis.
    input -> callback 
    '''
    keyboard = [[InlineKeyboardButton("Daily", callback_data='daily')],
                [InlineKeyboardButton("Weekly", callback_data='weekly')],
                [InlineKeyboardButton("Monthly", callback_data='monthly')]]

    rp = InlineKeyboardMarkup(keyboard, row_width=1)
    sent_msg = bot.send_message(calls.from_user.id, "Select the situation you wish to view a horoscope for: ",
                                reply_markup=rp, parse_mode="Markdown")

def day_handler(call):
    ''' This func show user a menu to select its choice. As if user wants to see horoscope of today, tomorrow, or yesterday. 
    input -> callback 
    output -> date decided by user
    '''
    text = "Pick the day on which you wish to get your horoscope."
    keyboard = [[InlineKeyboardButton("TODAY", callback_data='today')],
                [InlineKeyboardButton("TOMORROW", callback_data='tomorrow')],
                [InlineKeyboardButton("YESTERDAY", callback_data='yesterday')]]

    rp2 = InlineKeyboardMarkup(keyboard, row_width=1) 

    sent_msg = bot.send_message(call.from_user.id, text, reply_markup=rp2, parse_mode="Markdown")

def fetch_horoscope_daily(calls):
    '''
    This func takes calls as input. From calls.data we access the date decided by user and in try block we first try to store value of sign. In case of many users using the bot at same time, a user gets data of different user to we use calls id to access user_choice dict to assign value of sign.
    We call the get_daily_horoscope function from utils.py which fetches the user's horoscope and return the data in  dictonary. 
    input -> callback
    output -> daily horoscope of user 
    '''
    try:
        sign = user_choice[calls.from_user.id]
    except KeyError:
        bot.send_message(
            calls.from_user.id, "Please use command /horoscope first", parse_mode="Markdown")
        return

    day = calls.data                                    # getting the user decided date 
    temp_msg = bot.send_message(calls.from_user.id, "Fetching your Horoscope *{}*".format(
        sign), parse_mode="MarkdownV2")
    
    horoscope = get_daily_horoscope(sign, day)                              # horoscope is a python dict 
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:*  {data["horoscope_data"]} \n*Sign:* {sign} \n*Day:* {data["date"]}'
    bot.edit_message_text(
        horoscope_message, calls.from_user.id, temp_msg.id, parse_mode="Markdown")
    


def fetch_horoscope_weekly(calls):
    '''
    This func takes callback as input through which it access the user's id to get user's sign from user_choice dictonary. And then it calls the get_weekly_horoscope function which return user's weekly horoscope as dict.
    For more info read doctring of function fetch_daily_horoscope.
    input -> callback
    output -> weekly horoscope of user
    '''
    try:
        sign = user_choice[calls.from_user.id]
    except KeyError:
        bot.send_message(
            calls.from_user.id, "Please use command /horoscope first", parse_mode="Markdown")
        return

    temp_msg = bot.send_message(calls.from_user.id, "Fetching your Horoscope *{}*".format(
        sign), parse_mode="MarkdownV2")
    horoscope = get_weekly_horoscope(sign)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:*  {data["horoscope_data"]} \n*Sign:* {sign} \n*Week:* {data["week"]}'
    bot.edit_message_text(
        horoscope_message, calls.from_user.id, temp_msg.id, parse_mode="Markdown")


def fetch_horoscope_monthly(message):
    '''
    This func takes callback as input through which it access the user's id to get user's sign from user_choice dictonary. And then it calls the get_monthly_horoscope function which return user's weekly horoscope as dict.
    For more info read doctring of function fetch_daily_horoscope.
    input -> callback
    output -> monthly horoscope of user
    '''
    try:
        sign = user_choice[message.from_user.id]
    except KeyError:
        bot.send_message(
            message.from_user.id, "Please use command /horoscope first", parse_mode="Markdown")
        return
    temp_msg = bot.send_message(message.from_user.id, "Fetching your Horoscope *{}*".format(
        sign), parse_mode="MarkdownV2")
    horoscope = get_monthly_horoscope(sign)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:*  {data["horoscope_data"]} \n*Sign:* {sign} \n*Month:* {data["month"]}'
    bot.edit_message_text(
        horoscope_message, message.from_user.id, temp_msg.id, parse_mode="Markdown")
    


# def fetch_random_date(message,sign):
#     # try:
#     #     sign = user_choice[message.from_user.id]
#     # except KeyError:
#     #     bot.send_message(
#     #         message.from_user.id, "Please use command /horoscope first", parse_mode="Markdown")
#     #     return
#     day = message.text
#     temp_msg = bot.send_message(message.from_user.id, "Fetching your Horoscope *{}*".format(
#         sign), parse_mode="MarkdownV2")
    
#     horoscope = get_daily_horoscope(sign, day)
#     data = horoscope["data"]
#     horoscope_message = f'*Horoscope:*  {data["horoscope_data"]} \n*Sign:* {sign} \n*Day:* {data["date"]}'
#     bot.edit_message_text(
#         horoscope_message, message.from_user.id, temp_msg.id, parse_mode="Markdown")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    ''' This func will simply echo all the non-predefined messages of users.'''
    bot.send_message(message.chat.id, message.text +
                     '\n*Just repeating your messages.*')


bot.polling()
