from constants import *
from sql_fun import *
from queries_fun import *
import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def gen_ikb_from_list(b_names: list, bperrow: int, back_b=None):
    ''' 
    Generates inline keyboard layout from a list of values. Callback data mirros text on a button. 
    '''
    nrows = len(b_names) / bperrow
    # Start while loop for nrow
    btt_ind = 0
    r = 0
    inline_keyboard = []
    # If not natural number
    if nrows.is_integer() == False:
        full_r = math.floor(nrows)
        # Number of elements in a non-full row
        el_emp = len(b_names) - bperrow * full_r
        while btt_ind < len(b_names):
            nonf = 0
            # There will be only one non-full row
            while nonf < 1:
                nfull_row = []
                for i in range(el_emp):
                    nfull_row.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{b_names[btt_ind]}",
                        )
                    )
                    # Move to the next element in a list
                    btt_ind += 1
                inline_keyboard.append(nfull_row)
                nonf += 1
            while r < full_r:
                row_full = []
                for i in range(bperrow):
                    row_full.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{b_names[btt_ind]}",
                        )
                    )
                    btt_ind += 1
                inline_keyboard.append(row_full)
                r += 1

    else:
        while btt_ind < len(b_names):
            while r < nrows:
                row_full = []
                for i in range(bperrow):
                    row_full.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{b_names[btt_ind]}",
                        )
                    )
                    btt_ind += 1
                inline_keyboard.append(row_full)
                r += 1

    if type(back_b) == str:
        back_row = []
        back_row.append(
            InlineKeyboardButton(text=f"{back_b}", callback_data=f"{back_b}")
        )
        inline_keyboard.append(back_row)

    fin_kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return fin_kb


def gen_date_ikb_from_list(b_names: list, bperrow: int, back_b=None):
    '''
    Generates inline keyboard layout from a list of dates in yyyy-mm-dd format. Callback data is in yymmdd format
    '''
    nrows = len(b_names) / bperrow
    # Start while loop for nrow
    btt_ind = 0
    r = 0
    inline_keyboard = []
    # If not natural number
    if nrows.is_integer() == False:
        full_r = math.floor(nrows)
        # Number of elements in a non-full row
        el_emp = len(b_names) - bperrow * full_r
        while btt_ind < len(b_names):
            nonf = 0
            # There will be only one non-full row
            while nonf < 1:
                nfull_row = []
                for i in range(el_emp):
                    nfull_row.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{gen_date_callback(b_names[btt_ind])}",
                        )
                    )
                    # Move to the next element in a list
                    btt_ind += 1
                inline_keyboard.append(nfull_row)
                nonf += 1
            while r < full_r:
                row_full = []
                for i in range(bperrow):
                    row_full.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{gen_date_callback(b_names[btt_ind])}",
                        )
                    )
                    btt_ind += 1
                inline_keyboard.append(row_full)
                r += 1

    else:
        while btt_ind < len(b_names):
            while r < nrows:
                row_full = []
                for i in range(bperrow):
                    row_full.append(
                        InlineKeyboardButton(
                            text=f"{b_names[btt_ind]}",
                            callback_data=f"{gen_date_callback(b_names[btt_ind])}",
                        )
                    )
                    btt_ind += 1
                inline_keyboard.append(row_full)
                r += 1

    if type(back_b) == str:
        back_row = []
        back_row.append(
            InlineKeyboardButton(text=f"{back_b}", callback_data=f"{back_b}")
        )
        inline_keyboard.append(back_row)

    fin_kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return fin_kb

def cb_back_to_date(cb_str: str):
    ''' 
    Transforms callback data from date keyboard back to yyyy-mm-dd
    '''
    res = datetime.strptime(cb_str, "%Y%m%d").strftime("%Y-%m-%d")
    return res


def from_ymd_to_adby(dates_list: list):
    ''' 
    Reformats date from yyyy-mm-dd to more readable one (personal opinion). Dates in this  format will be seen by the end-user.
    ''' 
    res = [
        datetime.strptime(el, "%Y-%m-%d").strftime("%a, %d %B %Y") for el in dates_list
    ]
    return res


def gen_date_callback(dates):
    ''' 
    Reformats date string/list of dates into yymmdd format
    ''' 
    if type(dates) == str:
        res = datetime.strptime(dates, "%a, %d %B %Y").strftime("%Y%m%d")
    elif type(dates) == list:
        res = [datetime.strptime(el, "%a, %d %B %Y").strftime("%Y%m%d") for el in dates]
    else:
        print("'dates' variable should be either a list or a string")
    return res


def get_txtinfo_by_bid(b_id: int, cancel_info=None):
    ''' 
    Generates message with info about booking based on booking_id;
    If cancel_info variable isn't None, special header notifying about cancellation will be added on top.
    ''' 
    df = show_booking().reset_index(drop=True)
    row_index = df.index[df["booked_appointments_id"] == b_id].tolist()[0]
    df_dict = df.loc[df.booked_appointments_id == b_id].to_dict()
    name = df_dict["first_name"][row_index]
    surname = df_dict["last_name"][row_index]
    date = df_dict["execution_date"][row_index]
    time = df_dict["execution_time"][row_index]
    s_name = df_dict["service_name"][row_index]
    if cancel_info == None:
        msg = (
            f"\n\n•Service_name: {s_name}"
            f"\n•Chosen employee: {name} {surname}"
            f"\n•Chosen date:{date}"
            f"\n•Chosen time: {time}"
        )
    if cancel_info != None:
        msg = (
            f" 🚫❗<b>The following appointment was cancelled!❗🚫</b>"
            f"\n\n•Service_name: {s_name}"
            f"\n•Chosen employee: {name} {surname}"
            f"\n•Chosen date: {date}"
            f"\n•Chosen time: {time}"
        )

    return msg


def cancel_by_ba_id(path: str, ba_id: int):
    ''' 
    Modifies table with booking entries based on booked_appointment_id (changes status from 'ACTIVE' to 'CANCELLED')

    ''' 
    conn = sql.connect(path)
    c = conn.cursor()
    query = f"""
    UPDATE booked_appointments
    SET status = 'CANCELLED'
    WHERE booked_appointments_id = {ba_id}
     """
    c.execute(query)
    conn.commit()
    conn.close()


def fromvaltokey(dictionary:dict, val) -> list:
    ''' 
    Returns key for a value of a dictionary
    ''' 
    res = [k for k, v in dictionary.items() if v == val]
    return res

def date_time_co(my_dict)-> dict:
    ''' 
     Checks if there are keys in my_dict with same values. 
     If there are, the function returns dictionaory with repeating values as keys and former keys as values.
     ex.:
     Input: {1: 'hello', 2: 'bye', 3: 'hello', 4: 'chao', 5: 'bye'}
     Output: {'hello': [1, 3], 'bye': [2, 5]}
    ''' 
    date_ids_dub = {}
    for value in list(unique(my_dict.values())):
        if len(fromvaltokey(my_dict, value)) > 1:
            date_ids_dub.update({value:fromvaltokey(my_dict, value)})
    return date_ids_dub