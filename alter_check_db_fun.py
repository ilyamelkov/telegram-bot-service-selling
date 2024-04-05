import pandas as pd
import calendar
import sqlite3 as sql
from sql_fun import *
import re


def add_days(path: str, id: int, *args):
    wdays = list(calendar.day_name)
    for d in args:
        if d.capitalize() not in wdays:
            print("THERE IS NO SUCH DAY OF THE WEEK AS {d}")
        else:
            # print(f"{id}, {d.capitalize()}")
            add_row(
                f"{path}",
                tab_name="working_days",
                row_val=(f"{id}", f"{d.capitalize()}"),
            )


def check_foreign_match(path: str, val_check: int, r_tab_col: dict) -> bool:
    # print(f"\nCHECKING {val_check} EXISTANCE IN REFERENCE TABLE...\n")
    for key in r_tab_col:
        query = f"SELECT {r_tab_col[key]} FROM {key}"
        conn = sql.connect(path)
        ref = pd.read_sql_query(query, conn).iloc[:, 0].tolist()
        conn.close()
        if val_check in ref:
            # print(f"\tValue {val_check} WAS found in a reference column ({r_tab_col[key]}) from table {key} ✅")
            return True
        else:
            pass
            # print(f"\tValue {val_check} WAS NOT found in a reference column ({r_tab_col[key]}) from table {key} ❌")
            return False


def add_hours(path: str, wd_id: int, *args):
    if check_foreign_match(
        path, val_check=wd_id, r_tab_col={"working_days": "working_days_id"}
    ):
        # Check format of args
        pattern = r"^\d{2}:\d{2}$"
        # print("\nChecking correction of time input...")
        for h in args:
            # Check that time is in HH:MM format
            if re.search(pattern, h):
                # print(f"Start time {h} matches format....✅")
                # Split it into hours and minutes
                hour, m = h.split(":")
                # Convert strings into input
                hour = int(hour)
                m = int(m)
                # Check that hours do not exceed 24 & minutes do not exceed
                if (hour not in range(0, 25, 1)) | (m not in range(0, 61, 1)):
                    pass
                    # print( f"\tHour:{hour} or minute: {m} is wrong.\n\tEach element can't exceed 24-hour or 60-min boundaries! ❌")
                else:
                    add_row(path, "working_hours", row_val=(f"{wd_id}", f"{h}"))
                    print(f"\n\t({wd_id}, {h}) were added to working_hours table;")
            else:
                pass
                # print(f"\n\tStart time {h} doesn't match format...\n\tIt should be hh:mm\n")
