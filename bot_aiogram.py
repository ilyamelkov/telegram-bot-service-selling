from queries_fun import *
from bot_fun import *
from constants import intro_text, com_desc_text, conf_text, tg_token
from data_st import user_data, upcoming_all_dict, ext_dt_id_dic, ext_order_no_bid

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.enums.parse_mode import ParseMode


bot = Bot(token=tg_token)
dp = Dispatcher()

"""
service -> employee -> date->time_slot
service ->date ->time_slot->employee

"""

# Start command
@dp.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(text=f"Hello, {message.from_user.full_name}!")
    await bot.send_sticker(
        message.from_user.id,
        sticker="CAACAgIAAxkBAAELZRRlzFrDwhULedRdx_gvnTMeukAjIwACHgkAAhhC7gj5WNnuHSGcITQE",
    )
    await message.answer(text=intro_text)

    await message.answer(text=com_desc_text)
    await message.delete()


@dp.message(Command("upcoming"))
async def ret_upcoming(message: types.Message):
    user_data.update({"user_tgid": message.from_user.id})
    # Return dictionary of booking_id-date from user Telegram id
    baid_date_dic = upcoming_id_date(
        user_id=int(user_data["user_tgid"])
    )  # {1: '2024-04-03 16:00', 2: '2024-04-05 17:00', 4: '2024-04-05 17:00'}
    # Case with no appointments
    if len(baid_date_dic) == 0:
        await message.answer(text="You don't have any upcoming appointments")
    # Case with at least 1 appointment
    else:
        # Clear the dictionary
        upcoming_all_dict.clear()
        # Pass {1: '2024-04-03 16:00', 2: '2024-04-05 17:00', 4: '2024-04-05 17:00'} into other file
        upcoming_all_dict.update(baid_date_dic)
        date_id_dict = date_time_co(
            baid_date_dic
        )  # {'2025-12-04 13:00':[1, 3, 6]} If more than 1 appointment at the same date-time
        msg = ""
        msg = msg + f"Please, choose one of your upcoming appointments!\n"
        if len(date_id_dict) > 0:
            for key in date_id_dict:
                msg += f"🛎️ REMINDER: You have {len(date_id_dict[key])} appointments on {key}\n"
            # Pass {'2025-12-04 13:00':[1, 3, 6]} to other file
            ext_dt_id_dic.update(date_id_dict)
        # Create a list for keyboard
        tokb = list(unique(upcoming_all_dict.values()))
        await message.answer(
            text=msg,
            reply_markup=gen_ikb_from_list(tokb, bperrow=2),
        )


@dp.message(Command("prices"))
async def handle_price(message: types.Message):
    df = show_table_all(path, "service")[["service_name", "service_price_eu"]]
    df["show"] = df.service_name + " " + "€" + df.service_price_eu.astype(str)
    np_list = df.show.tolist()
    msg = ""
    msg = msg + f"💶<b>Here are relevant prices for now:</b>\n"
    for item in np_list:
        msg += f"\t\t\t•{item}\n"
    await message.answer(text=msg, parse_mode=ParseMode.HTML)
    await message.delete()


# Enroll command
@dp.message(Command("enroll"))
async def handle_enroll(message: types.Message):
    s_kb = gen_ikb_from_list(ret_s_list(), bperrow=2)
    await message.answer(text="Please, choose a service!", reply_markup=s_kb)
    await message.delete()


# Callback query handler for services inline keyboard
@dp.callback_query(F.data.in_(ret_s_list()))
async def handle_serv_click(callback_query: CallbackQuery):
    user_data.update({"service_name": callback_query.data})
    await callback_query.message.edit_text(
        text=f"•Chosen service: {user_data['service_name']}",
        reply_markup=gen_ikb_from_list(
            ["Choose employee", "Choose a date"],
            2,
            back_b="Go back to choosing a service",
        ),
    )


# Callback query handling for service vs date keyboard
## Callback query handler for choosing date --> show the date
### service ->date ->time_slot->employee
@dp.callback_query(F.data == "Choose a date")
async def handle_choose_emp_click(callback_query: CallbackQuery):
    user_data.update({"path": "date"})
    dates = ret_empty_slots(se_name=user_data["service_name"], ret_dates=True)
    formatted_dates = from_ymd_to_adby(dates)
    await callback_query.message.edit_text(
        text=f"•Chosen service: {user_data['service_name']}\n Please, choose a date:",
        reply_markup=gen_date_ikb_from_list(
            formatted_dates, 2, back_b="Go back to previous step"
        ),
    )


## Callback query handler for choosing employee --> show employees
@dp.callback_query(F.data == "Choose employee")
async def handle_choose_emp_click(callback_query: CallbackQuery):
    user_data.update({"path": "emp"})
    await callback_query.message.edit_text(
        text=f"•Chosen service: {user_data['service_name']}\nPlease, choose an employee:",
        reply_markup=gen_ikb_from_list(
            get_first_last(s_name=user_data["service_name"]),
            2,
            back_b="Go back to previous step",
        ),
    )


# Callback handler for chosen employee
@dp.callback_query(F.data.in_(get_first_last_all()))
async def employee_click(callback_query: CallbackQuery):
    chosen_emp_id, name, surname = callback_query.data.split(" ")
    chosen_emp_id = int(chosen_emp_id.replace(".", ""))
    user_data.update({"emp_name": f"{name} {surname}"})
    user_data.update({"emp_id": chosen_emp_id})
    # service - employee - day-slot; show available days
    if user_data["path"] == "emp":
        dates = days_from_emp_id_s(
            s_name=user_data["service_name"], emp_id=user_data["emp_id"]
        )

        formatted_dates = from_ymd_to_adby(dates)
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\nPlease, choose a day:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_date_ikb_from_list(
                formatted_dates, 2, back_b="Go back to choosing an employee"
            ),
        )
    # service - day - time - employee; show confirmation menu
    elif user_data["path"] == "date":
        msg = (
            f"•Chosen service:{user_data['service_name']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\n•Chosen time: {user_data['time_slot']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n\n❕Reminding you that after pressing 'Enter name' you won't be able to change details of your booking"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                ["Enter name"], bperrow=1, back_b="Go back to choosing an employee"
            ),
        )


# Manage callbacks for a date
@dp.callback_query(F.data.regexp(r"\d{8}"))
async def handle_date_click(callback_query: CallbackQuery):
    # tranform data into suitable format
    chosen_date = cb_back_to_date(callback_query.data)
    # append to the user data
    user_data.update({"date": chosen_date})
    df = ret_empty_slots(se_name=user_data["service_name"])
    date_f = df.date.isin([user_data["date"]])
    # service-employee-day-slot
    if user_data["path"] == "emp":
        name, surname = user_data["emp_name"].split(" ")
        name_f = df.first_name.isin([name])
        surname_f = df.last_name.isin([surname])
        slots = df.loc[name_f & surname_f & date_f].free_slots.tolist()
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\nPlease, choose a time slot:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                slots, 3, back_b="Go back to choosing a date"
            ),
        )
    # service -day-slot-employee
    elif user_data["path"] == "date":
        slots = unique(df.loc[date_f].free_slots.tolist())
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\nPlease, choose a time slot:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                slots, 3, back_b="Go back to choosing a date"
            ),
        )


# Manage callback of a time slot
@dp.callback_query(F.data.regexp(r"\d{2}:\d{2}"))
async def handle_slot_click(callback_query: CallbackQuery):
    user_data.update({"time_slot": callback_query.data})
    # service-date-slot-emp
    if user_data["path"] == "date":
        # Check that user doesn't already have an appointment at that time and date
        df = ret_empty_slots(se_name=user_data["service_name"])
        slot_f = df.free_slots.isin([user_data["time_slot"]])
        date_f = df.date.isin([user_data["date"]])
        df = df.loc[date_f & slot_f]
        df["id_first_last"] = (
            df.emp_id.astype(str) + "." + " " + df.first_name + " " + df.last_name
        )
        id_first_last = unique(df.id_first_last.tolist())
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen date: {user_data['date']}"
            f"\n•Chosen timeslot: {user_data['time_slot']}"
            f"\nPlease, choose an employee:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                id_first_last, 2, back_b="Go back to choosing a time slot"
            ),
        )
    # service-emp-day-slot
    elif user_data["path"] == "emp":
        msg = (
            f"•Chosen service:{user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\n•Chosen time: {user_data['time_slot']}"
            f"\n\n<b>❕Reminding you that after pressing 'Enter name' you won't be able to change details of your booking</b>"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                ["Enter name"], bperrow=1, back_b="Go back to choosing a time slot"
            ),
            parse_mode=ParseMode.HTML,
        )


# Manage callback for entering name
@dp.callback_query(F.data == "Enter name")
async def ask_name_surname(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(text=conf_text)
    user_data.update({"name_asked": "True"})


# Manage callback for upcoming appointment click
@dp.callback_query(F.data.regexp(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"))
async def ret_info_upc(callback_query: CallbackQuery):
    if callback_query.data not in ext_dt_id_dic.keys():
        ba_id = fromvaltokey(upcoming_all_dict, callback_query.data)
        ba_id = ba_id[0]
        msg = str(ba_id)
        user_data.update({"upc_id": ba_id})
        msg = get_txtinfo_by_bid(b_id=ba_id)
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                b_names=["Cancel 🚫", "All upcoming"], bperrow=2
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        ext_order_no_bid.clear()
        order_no_bid = {}
        buttons = []
        msg = ""
        for key in ext_dt_id_dic:
            for i in range(len(ext_dt_id_dic[key])):
                msg += "\n"
                # print(f"{i+1}.{date_ids_dict[key][i]}")
                order_no_bid.update({f"#{i+1}": ext_dt_id_dic[key][i]})
                msg += f"#{i+1}"
                buttons.append(f"#{i+1}")
                msg += get_txtinfo_by_bid(ext_dt_id_dic[key][i])
                msg += "\n"
        ext_order_no_bid.update(order_no_bid)
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                b_names=buttons, bperrow=2, back_b="All upcoming"
            ),
            parse_mode=ParseMode.HTML,
        )


# Manage callback in case there are two appointments in the same day in the same time
@dp.callback_query(F.data.in_(ext_order_no_bid))
async def order_no_click(callback_query: CallbackQuery):
    user_data.update({"upc_id": ext_order_no_bid[callback_query.data]})
    msg = get_txtinfo_by_bid(ext_order_no_bid[callback_query.data])
    await callback_query.message.edit_text(
        text=msg,
        reply_markup=gen_ikb_from_list(b_names=["Cancel 🚫", "All upcoming"], bperrow=2),
        parse_mode=ParseMode.HTML,
    )


# Manage callback from cancel button
@dp.callback_query(F.data == "Cancel 🚫")
async def ret_info_upc(callback_query: CallbackQuery):
    msg = get_txtinfo_by_bid(
        b_id=user_data["upc_id"], cancel_info=True
    )  # user_data['upc_id']
    cancel_by_ba_id(path, ba_id=user_data["upc_id"])  # user_data['upc_id']
    await callback_query.message.edit_text(text=msg, parse_mode=ParseMode.HTML)


# Manage callback for all upcoming
@dp.callback_query(F.data == "All upcoming")
async def show_upc(callback_query: CallbackQuery):
    user_data.update({"user_tgid": callback_query.from_user.id})
    # Return dictionary of booking_id-datetime from user Telegram id
    baid_date_dic = upcoming_id_date(
        user_id=int(user_data["user_tgid"])
    )  # {1: '2024-04-03 16:00', 2: '2024-04-05 17:00', 4: '2024-04-05 17:00'}
    # Case with no appointments
    if len(baid_date_dic) == 0:
        await callback_query.message.edit_text(
            text="You don't have any upcoming appointments"
        )
    # Case with at least 1 appointment
    else:
        # Clear the dictionary
        upcoming_all_dict.clear()
        # Pass {1: '2024-04-03 16:00', 2: '2024-04-05 17:00', 4: '2024-04-05 17:00'} into other file
        upcoming_all_dict.update(baid_date_dic)
        # Check if there are more than 1 appointment
        date_id_dict = date_time_co(
            baid_date_dic
        )  # {'2025-12-04 13:00':[1, 3, 6]} If more than 1 appointment at the same date-time
        msg = ""
        msg = msg + f"Please, choose one of your upcoming appointments!\n"
        if len(date_id_dict) > 0:
            for key in date_id_dict:
                msg += f"🛎️ REMINDER: You have {len(date_id_dict[key])} appointments on {key}\n"
            # Pass {'2025-12-04 13:00':[1, 3, 6]} to other file
            ext_dt_id_dic.update(date_id_dict)
        # Create a list for keyboard
        tokb = list(unique(upcoming_all_dict.values()))
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(tokb, bperrow=2),
        )


# Manage user's input after entering his name
@dp.message()
async def user_messages(message: types.Message):
    if user_data["name_asked"] != "True":
        await message.answer(
            "Please, use one of the commands or continue following the bot structure"
        )
        await message.delete()
    else:
        user_data.update({"user_name": message.text})
        user_data.update({"user_tgid": message.from_user.id})
        msg = (
            f"\n<b>{message.text.capitalize()}, reminding you that you chose a service with the following properties:</b> "
            f"\n\n•Service_name: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Chosen date: {user_data['date']}"
            f"\n•Chosen time: {user_data['time_slot']}"
        )
        await message.answer(
            msg,
            reply_markup=gen_ikb_from_list(
                ["Make booking 🏆", "Enter name again"], bperrow=2
            ),
            parse_mode=ParseMode.HTML,
        )
        user_data.update({"name_asked": ""})


# Re-enter name callback
@dp.callback_query(F.data == "Enter name again")
async def reentername(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(text="Please, enter your name!")
    user_data.update({"name_asked": "True"})


# Manage callback for booking
@dp.callback_query(F.data == "Make booking 🏆")
async def book_ts(callback_query: CallbackQuery):
    # Get employee_service_id
    idtosave = get_s_emp_id(user_data["service_name"], user_data["emp_id"])
    # Check if the time is still available
    if (
        check_slot(
            s_emp_id=idtosave, date=user_data["date"], time=user_data["time_slot"]
        )
        == False
    ):
        add_row(
            path,
            "booked_appointments",
            row_val=(
                idtosave,
                user_data["user_name"],
                user_data["user_tgid"],
                user_data["time_slot"],
                user_data["date"],
                "ACTIVE",
            ),
        )
        user_data.update({"name_asked": ""})
        msg = (
            f"<b>Congratulations, {user_data['user_name'].capitalize()}!🎉</b>"
            f"\nYou have <b>booked an appointment!</b> ✅"
            f"\n\n<b>Here is info about the booking:</b>"
            f"\n•Service_name: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Chosen date: {user_data['date']}"
            f"\n•Chosen time: {user_data['time_slot']}"
            f"\n\n Thank you for using our services!"
        )
        await callback_query.message.edit_text(text=msg, parse_mode=ParseMode.HTML)
    else:
        msg = (
            f"While you were deciding on the appointment, someone already booked the timeslot!"
            f"\nPlease choose a different one!"
        )
        await callback_query.message.edit_text(text=msg)


# Back buttons handling

## Callback query handling for ~Go to previous step button
@dp.callback_query(F.data == "Go back to previous step")
async def backto_empvsdate(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text=f"•Chosen service: {user_data['service_name']}",
        reply_markup=gen_ikb_from_list(
            ["Choose employee", "Choose a date"],
            2,
            back_b="Go back to choosing a service",
        ),
    )


## ~Go back to choosing an employee
@dp.callback_query(F.data == "Go back to choosing an employee")
async def backto_employees(callback_query: CallbackQuery):
    if user_data["path"] == "emp":
        await callback_query.message.edit_text(
            text=f"•Chosen service: {user_data['service_name']}\nPlease, choose an employee:",
            reply_markup=gen_ikb_from_list(
                get_first_last(s_name=user_data["service_name"]),
                2,
                back_b="Go back to previous step",
            ),
        )
    elif user_data["path"] == "date":
        df = ret_empty_slots(se_name=user_data["service_name"])
        slot_f = df.free_slots.isin([user_data["time_slot"]])
        date_f = df.date.isin([user_data["date"]])
        df = df.loc[date_f & slot_f]
        df["first_last"] = df.first_name + " " + df.last_name
        first_last = unique(df.first_last.tolist())
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen date: {user_data['date']}"
            f"\n•Chosen timeslot: {user_data['time_slot']}"
            f"\nPlease, choose an employee:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                first_last, 2, back_b="Go back to choosing a time slot"
            ),
        )


## ~Back to time slots
@dp.callback_query(F.data == "Go back to choosing a time slot")
async def backto_ts(callback_query: CallbackQuery):
    chosen_date = user_data["date"]
    df = ret_empty_slots(se_name=user_data["service_name"])
    date_f = df.date.isin([user_data["date"]])
    # service-employee-day-slot
    if user_data["path"] == "emp":
        name, surname = user_data["emp_name"].split(" ")
        name_f = df.first_name.isin([name])
        surname_f = df.last_name.isin([surname])
        slots = df.loc[name_f & surname_f & date_f].free_slots.tolist()
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Chosen day: {user_data['date']}"
            f"\n•Please, choose a time slot:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                slots, 3, back_b="Go back to choosing a date"
            ),
        )
    # service -day-slot-employee
    elif user_data["path"] == "date":
        slots = unique(df.loc[date_f].free_slots.tolist())
        msg = (
            f"Chosen service: {user_data['service_name']}"
            f"\nChosen day: {user_data['date']}"
            f"\nPlease, choose a time slot:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_ikb_from_list(
                slots, 3, back_b="Go back to choosing a date"
            ),
        )


## ~Back to choosing a service
@dp.callback_query(F.data == "Go back to choosing a service")
async def backtoservice(callback_query: CallbackQuery):
    s_kb = gen_ikb_from_list(ret_s_list(), bperrow=2)
    await callback_query.message.edit_text(
        text="Please, choose a service!", reply_markup=s_kb
    )


## ~Back to choosing a date
@dp.callback_query(F.data == "Go back to choosing a date")
async def backtodate(callback_query: CallbackQuery):
    if user_data["path"] == "emp":
        dates = days_from_emp_id_s(
            s_name=user_data["service_name"], emp_id=user_data["emp_id"]
        )

        formatted_dates = from_ymd_to_adby(dates)
        msg = (
            f"•Chosen service: {user_data['service_name']}"
            f"\n•Chosen employee: {user_data['emp_name']}"
            f"\n•Please, choose a day:"
        )
        await callback_query.message.edit_text(
            text=msg,
            reply_markup=gen_date_ikb_from_list(
                formatted_dates, 2, back_b="Go back to choosing an employee"
            ),
        )
    elif user_data["path"] == "date":
        dates = ret_empty_slots(se_name=user_data["service_name"], ret_dates=True)
        formatted_dates = from_ymd_to_adby(dates)
        await callback_query.message.edit_text(
            text=f"•Chosen service: {user_data['service_name']}\n Please, choose a date:",
            reply_markup=gen_date_ikb_from_list(
                formatted_dates, 2, back_b="Go back to previous step"
            ),
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
