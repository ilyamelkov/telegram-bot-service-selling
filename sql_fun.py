# Import packages
import sqlite3 as sql
from sqlite3 import OperationalError
import pandas as pd
import numpy as np
import calendar


def del_all_tables(path: str):
    """ 
    Deletes all tables from the database which is located in 'path'

    """
    # Connect to the database or create it
    conn = sql.connect(path)
    # Create a cursor for database manipulation
    c = conn.cursor()
    # Check if there are any tables in the database &
    # delete them to recreate later on
    sql_command_tabname = """ 
    SELECT name 
    FROM sqlite_master WHERE type='table';"""
    c.execute(sql_command_tabname)
    table_names = c.fetchall()

    if len(table_names) > 0:
        for i in range(len(table_names)):
            sql_del = f"DROP table {table_names[i][0]}"
            c.execute(sql_del)
            print(f" The following table was deleted: {table_names[i][0]}")

    else:
        pass

    conn.commit()
    conn.close()


def gen_tabhead_query(
    tabname: str,
    colname_type: dict,
    primary=False,
    foreign: list = None,
    reference_tab_col: dict = None,
):
    """ 
     Returns SQL command which, if executed, creates a table with primary/secondary keys
    """ 
    p_create = f"CREATE TABLE {tabname} "
    orig_cols = []
    for i in colname_type.items():
        col_type = i[0] + " " + i[1]
        orig_cols.append(col_type)
    # Table headers if there's no need in primary|foreign keys (default option)
    if (reference_tab_col == None) & (foreign == None) & (primary == False):
        cols = str(orig_cols).replace("'", "").replace("[", "(").replace("]", ")")
        final = "".join(p_create + cols)
    # Table headers if we need ONLY primary key
    elif (primary == True) & (reference_tab_col == None) & (foreign == None):
        p_primary = f"{tabname}_id INTEGER PRIMARY KEY"
        orig_cols.insert(0, p_primary)
        cols = str(orig_cols).replace("'", "").replace("[", "(").replace("]", ")")
        final = "".join(p_create + cols)
    # Table headers if we need to have some foreign keys
    elif (reference_tab_col != None) & (foreign != None):
        f = len(foreign)
        ref = len(reference_tab_col)
        if f != ref:
            print("EACH FOREIGN COLUMN SHOULD HAVE A REFERENCE COLUMN")
        else:
            k = 0
            ref = []
            for key_val in reference_tab_col.items():
                ref_col = (
                    "FOREIGN KEY"
                    + " "
                    + f"({foreign[k]})"
                    + " "
                    + "REFERENCES "
                    + " "
                    + key_val[0]
                    + "("
                    + key_val[1]
                    + ")"
                )
                ref.append(ref_col)
                k += 1
            ref = str(ref).replace("'", "").replace("[", "").replace("]", "")
            h = len(orig_cols)
            orig_cols.insert(h, ref)
            # If we  want to add  a primary key to a new table
            if primary == True:
                p_primary = f"{tabname}_id INTEGER PRIMARY KEY"
                orig_cols.insert(0, p_primary)
                cols = (
                    str(orig_cols).replace("'", "").replace("[", "(").replace("]", ")")
                )
                final = "".join(p_create + cols)
            # foreign keys only
            else:
                cols = (
                    str(orig_cols).replace("'", "").replace("[", "(").replace("]", ")")
                )
                final = "".join(p_create + cols)

    return final


def show_table_all(path: str, tab_name):
    """
    Shows desired table from a database as pandas dataframe object
    """
    # Connect to the database
    conn = sql.connect(path)
    # Return updated table
    sql_ret_tab = f"SELECT * FROM {tab_name}"
    df = pd.read_sql_query(sql_ret_tab, conn)
    conn.close()
    return df


def show_table_from_q(path: str, sql_command: str):
    ''' 
     Shows desired table filtered by 'sql_command' variable as pandas dataframe 
    '''
    conn = sql.connect(path)
    df = pd.read_sql_query(sql_command, conn)
    conn.close()
    return df


def add_row(path: str, tab_name: str, row_val: tuple):
    '''
    Adds row to a desired table in a database
    '''
    # Connect to the database
    conn = sql.connect(path)
    # Create a cursor to interact with the database
    c = conn.cursor()
    data = c.execute(f"SELECT * FROM {tab_name}")
    ex_colnames = []
    for column in data.description:
        if column[0] == f"{tab_name}_id":
            pass
        else:
            ex_colnames.append(column[0])
    columns = tuple(ex_colnames)
    # SQL command
    query = f"INSERT INTO {tab_name} {columns} VALUES {row_val}"
    # Execute SQL command
    c.execute(query)
    # Save changes
    conn.commit()
    # Close the database
    conn.close()
    # Return the resulting table
    return None
