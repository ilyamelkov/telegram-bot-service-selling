from constants import *
from sql_fun import *
from datetime import datetime, timedelta, timezone
from constants import booking_horizon, timezone_offset


def show_emp_wd_slots():

    ''' 
    Returns pandas dataframe of joined tables with the following columns:
    -  employee_id, first_name, last_name, day_of_the_week, start_time
    '''
    query = """
            SELECT e.employee_id, e.first_name, e.last_name, wd.day_of_the_week, wh.start_time
            FROM working_hours wh
            LEFT JOIN working_days wd
            ON wh.wd_emp = wd.working_days_id
            LEFT JOIN employee e
            ON wd.employee_id = e.employee_id
            """

    df = show_table_from_q(path, query)
    return df


def show_booking():
    '''
    Returns pandas dataframe of joined tables with the following columns:
     - booked_appointments_id, emp_service_id, employee_id, first_name, last_name, service_name, user_name, telegram_id, execution_time, execution_date, status 
    '''

    query = """
            SELECT b.booked_appointments_id, es.emp_service_id, e.employee_id, e.first_name, e.last_name, s.service_name, b.user_name, b.telegram_id, b.execution_time, b.execution_date, b.status
            FROM booked_appointments b
            LEFT JOIN emp_service AS es
            ON b.emp_service_id = es.emp_service_id
            LEFT JOIN employee AS e
            ON es.employee_id = e.employee_id
            LEFT JOIN service AS s 
            ON es.service_id = s.service_id
            WHERE b.status = 'ACTIVE'
            """

    df = show_table_from_q(path, query)
    return df


# Join the employee table and service table based on the data from emp_service table


def show_emp_serv():
    ''' 
    Returns pandas dataframe of joined tables with the following columns:
    - service_id, employee_id, service_id, first_name, last_name, service_name, current_status
    ''' 
    query = """SELECT  es.emp_service_id, es.employee_id, es.service_id, e.first_name, e.last_name, s.service_name, e.current_status
            FROM emp_service es
            LEFT JOIN employee e  
            ON es.employee_id = e.employee_id
            LEFT JOIN service s
            ON es.service_id = s.service_id 
            WHERE e.current_status = 'ACTIVE'"""
            

    df = show_table_from_q(path, query)
    return df


def ret_s_list() -> list:
    '''
    Returns available services as a list
    '''  

    query = """ SELECT service_name
                        FROM service"""
    res = show_table_from_q(path, query).service_name.values.tolist()
    return res


# This dataframe returns available slots based on a service name
def ret_empty_slots(se_name: str, ret_dates=None):
    ''' 
    Returns pandas dataframe of available time slots for a service with the following columns:
    - date, weekday, emp_id, free_slots, first_name, last_name 

    If ret_dates is not 'None', returns list of unique available dates for service i to be executed
    '''
    # Create a dataframe in which all available data will be stored
    c_df = []
    # Return next 14 days
    dates = [
        d.date() for d in pd.date_range(start=datetime.today(), periods=booking_horizon)
    ]
    # print(dates)
    # Return names working days and emp_ids who provide service_i
    id_wdays_dict = ret_wdays_from_s(s_name=se_name)
    # print(id_wdays_dict)
    av_dates = []
    for d in dates:
        wday = d.strftime("%A")
        for key in id_wdays_dict:
            if wday in id_wdays_dict[key]:
                av_dates.append(d)
            else:
                pass
    av_dates = np.unique(av_dates)
    # print(av_dates)
    b = show_booking()
    tslots = show_emp_wd_slots()

    for d in av_dates:
        # Get string of date d
        strd = d.strftime("%Y-%m-%d")
        # print(strd)
        # Get weekday of date d
        wday = d.strftime("%A")
        wday_fil = tslots.day_of_the_week.isin([wday])
        for key in id_wdays_dict:
            id_fil = tslots.employee_id.isin([key])
            df = tslots.loc[id_fil & wday_fil]
            if len(df) == 0:
                pass
            else:
                # print(df)

                pos = df.start_time.tolist()
                name = df.first_name.unique()
                surname = df.last_name.unique()
                # print(name)
                # print(f"Date: {strd}; emp_id: {key}; Day of the week:{wday}; All possible: {pos}")
                if strd in b.execution_date.unique():
                    b_date_fil = b.execution_date.isin([strd])
                    id_fil = b.employee_id.isin([key])
                    # Filter booked table by employee_id and date
                    df_b = b.loc[b_date_fil & id_fil]
                    if len(df) == 0:
                        pass
                    else:
                        occupied = df_b.execution_time.tolist()
                        # print(f"Date: {strd}; emp_id:{key}; Available: {pos}")
                        # print(f"Date: {strd}; emp_id:{key}; Occupied: {occupied}")
                        empty = ret_unique_b(occupied, pos)

                        # print(f"Date: {strd}; emp_id:{key}; Free_slots: {empty}\n")

                        s = pd.DataFrame(
                            {
                                "date": strd,
                                "weekday": wday,
                                "emp_id": key,
                                "free_slots": empty,
                            }
                        )
                        c_df.append(s)

                else:
                    # Case when a day is completely free
                    # print(f"date: {strd}; weekday: {wday}; emp_id:{key}; free_slots: {pos}\n")
                    f = pd.DataFrame(
                        {
                            "date": strd,
                            "weekday": wday,
                            "emp_id": key,
                            "free_slots": pos,
                        }
                    )
                    c_df.append(f)

    fin = pd.concat(c_df)

    query = """
            SELECT employee_id, first_name, last_name
            FROM employee
            """

    id_name = show_table_from_q(path, query)
    # id_name

    res = pd.merge(
        fin, id_name, how="left", left_on="emp_id", right_on="employee_id"
    ).drop(columns=["employee_id"])
    tzinfo = timezone(timedelta(hours=timezone_offset))
    today = datetime.now(tzinfo)
    fmt = "%H:%M %Y-%m-%d"
    now_str = today.strftime(fmt)
    res["date_time_str"] = res.free_slots + " " + res.date
    res["dtobj"] = pd.to_datetime(res["date_time_str"], format="%H:%M %Y-%m-%d")
    res["now"] = now_str
    res["now_dtobj"] = pd.to_datetime(res["now"], format="%H:%M %Y-%m-%d")
    res["dif"] = res.dtobj - res.now_dtobj
    # Format dif column into dates
    res["dif"] = res["dif"] / pd.Timedelta(minutes=1)
    res = res.drop(columns=["now", "date_time_str", "dtobj", "now_dtobj"]).loc[(res.dif > 0)]
    res = res.drop(columns = ['dif'])

    if ret_dates == True:
        res = unique(res.date.tolist())

    return res


# Returns list of unique values from list b (second argument)
def ret_unique_b(a: list, b: list) -> list:
    res = []
    for i in b:
        if i in a:
            pass
        else:
            res.append(i)
    return res


def ret_wdays_from_s(s_name: str) -> dict:
    ''' 
    Returns employee_id and working days of employees who provide service i
    '''
    query = f"""
                SELECT es.employee_id, es.emp_service_id, e.first_name, e.last_name, s.service_name, s.service_price_eu, wd.day_of_the_week
                FROM emp_service AS es
                LEFT JOIN service AS s
                ON es.service_id = s.service_id
                LEFT JOIN  employee AS e
                ON es.employee_id = e.employee_id
                LEFT JOIN working_days wd
                ON es.employee_id = wd.employee_id
                WHERE service_name = '{s_name}' """
    data = show_table_from_q(path, query)
    uni_ids = data.employee_id.unique()
    res = {}
    for e_id in uni_ids:
        f1 = data.employee_id.isin([e_id])
        subset = data.loc[f1]
        val = subset.day_of_the_week.unique().tolist()
        res.update({e_id: val})

    return res


def get_first_last(s_name: str) ->list:
    ''' 
    Return names & surnames of active employees based on a service name
    '''
    f1 = show_emp_serv().service_name.isin([s_name])
    df = show_emp_serv().loc[f1][["employee_id", "first_name", "last_name"]]
    df["id_first_last"] = (
        df.employee_id.astype(str) + "." + " " + df.first_name + " " + df.last_name
    )
    av_emp = df.id_first_last.tolist()
    return av_emp


def get_first_last_all() -> list:
    ''' 
    Returns names and surnames of all active employees
    ''' 
    df = show_emp_serv()
    df["id_first_last"] = (
        df.employee_id.astype(str) + "." + " " + df.first_name + " " + df.last_name
    )
    emp_all = df.id_first_last.tolist()
    return emp_all


def days_from_emp_id_s(s_name: str, emp_id: int):
    '''
    Returns list of available dates for desired service and employee
    '''
    df = ret_empty_slots(se_name=s_name)
    f1 = df.emp_id.isin([emp_id])
    res = df.loc[f1]
    return unique(res.date.tolist())

def get_s_emp_id(serv_name, emp_id) -> int:

    '''
    Returns serv_emp_id (unique value for combination of employee and service he/she provides) based on employee id and service name 
    '''
    df = show_emp_serv()
    f1 = df.employee_id.isin([emp_id])
    f2 = df.service_name.isin([serv_name])
    df = df.loc[f1 & f2]
    return df["emp_service_id"].values[0]


def unique(list1) -> list:
    # initialize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def check_slot(s_emp_id: int, date: str, time: str) -> bool:
    ''' 
    Checks if the desired slot is available
    ''' 
    df = show_booking()
    id_f = df.emp_service_id.isin([s_emp_id])
    date_f = df.execution_date.isin([date])
    time_f = df.execution_time.isin([time])
    status_f = df.status.isin(["ACTIVE"])
    res = df.loc[id_f & date_f & time_f & status_f].values
    if len(res) == 1:
        return True
    else:
        return False


def upcoming_id_date(user_id: int) -> dict:
    ''' 
    Returns dictionary of upcoming booked appointment ids as keys and date & time strings as values based on Telegram user_id
    ''' 
    df = show_booking()
    df = df.loc[(df.telegram_id == user_id) & (df.status == "ACTIVE")]
    df["date_time_str"] = df.execution_time + " " + df.execution_date
    df["dtobj"] = pd.to_datetime(df["date_time_str"], format="%H:%M %Y-%m-%d")
    # df['relevancy'] = df.datetime_obj.apply(cat_book)
    tzinfo = timezone(timedelta(hours=timezone_offset))
    today = datetime.now(tzinfo)
    fmt = "%H:%M %Y-%m-%d"
    now_str = today.strftime(fmt)
    df["now"] = now_str
    df["now_dtobj"] = pd.to_datetime(df["now"], format="%H:%M %Y-%m-%d")
    df["dif"] = df.dtobj - df.now_dtobj
    df["dif"] = df["dif"] / pd.Timedelta(minutes=1)
    df = df.drop(columns=["now", "date_time_str", "dtobj", "now_dtobj"]).loc[
        (df.dif > 0)
    ]
    df["show"] = df["execution_date"] + " " + df.execution_time
    res = df.show.tolist()
    df1 = df[["booked_appointments_id", "show"]]
    d = df1.set_index("booked_appointments_id")["show"].to_dict()

    return d

