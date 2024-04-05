import os

# PATH TO THE DATABASE
#path = "C:\Рабочий стол\Python\Git projects\Telegram Bot\projecttg_db.db"
path = os.getcwd() + '\\project_tg.db'

# NUMBER OF WORKERS
no_workers = 4

# NUMBER OF SERVICES
number_of_services = 8

# BOOKING HORIZON
booking_horizon = 7

# TIMEZONE (UTC+03:00)
timezone_offset = +3.0

# TELEGRAM BOT TOKEN
tg_token = " "

# TEXT MESSAGES WHICH DO NOT CONTAIN ANY VARIABLES
intro_text = (
    f" I'm happy to see you in this bot!"
    f"\nThis is my attempt to utilize functionality of a Telegram bot by creating one for service-selling."
)

com_desc_text = (
    f"This bot can process the following commands:"
    f"\n\n /enroll - book a time slot"
    f"\n\n /prices - check prices for our services"
    f"\n\n /upcoming - check upcoming appointments"
    f"\n\n You can proceed by pressing the command right is this message!"
)

conf_text = "We're almost done.\nNow, please, enter your name!"
