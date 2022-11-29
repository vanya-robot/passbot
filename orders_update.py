import time
import datetime
import pandas as pd
import sqlite3

import queries_db
import spreadsheets


def select_current_orders(time_difference):  # В переменную time_difference вводится количество часов. Записи из таблицы
    # пропусков будут выводиться за период 'Время_текущее - time_difference'.
    time_difference = float(time_difference * 60 * 60)
    time_now = datetime.datetime.now()
    time_now = time.mktime(time_now.timetuple())

    select_query = '''SELECT Code, Car_num, Car_brand, Time FROM Orders WHERE ? - strftime('%s', Time) <= ? 
    AND Status = 0'''
    query_values = (time_now, time_difference)
    connection = sqlite3.connect('vol/passbot.db')
    df = pd.read_sql_query(sql=select_query, con=connection, params=query_values)

    home_num = []
    name = []
    phone = []
    select_query2 = '''SELECT House_num FROM Users WHERE Code = ?'''
    select_query3 = '''SELECT Name FROM Users WHERE Code = ?'''
    select_query4 = '''SELECT Phone FROM Users WHERE Code = ?'''
    for i in range(len(df['Code'])):
        cursor = connection.cursor()
        cursor.execute(select_query2, (df['Code'][i],))
        home_num.append(cursor.fetchone()[0])
        cursor = connection.cursor()
        cursor.execute(select_query3, (df['Code'][i],))
        name.append(cursor.fetchone()[0])
        cursor = connection.cursor()
        cursor.execute(select_query4, (df['Code'][i],))
        phone.append(cursor.fetchone()[0])

    df['Name'] = name
    df['Phone'] = phone
    df['House_num'] = home_num
    connection.close()

    return df


def update_order_status(df):

    orders = df.loc[df[7] == 1.0][3].tolist()

    update_query = '''Update Orders SET Status = 1, Time_of_arrival = ? WHERE Time = ?'''

    connection = sqlite3.connect('vol/passbot.db')
    cursor = connection.cursor()

    for order in orders:
        cursor.execute(update_query, (datetime.datetime.now(), order))

    connection.commit()

    select_query = 'SELECT Code, Car_num, Car_brand, Time, Time_of_arrival FROM Orders WHERE Time = ?'

    for order in orders:
        cursor.execute(select_query, (order,))
        row = cursor.fetchone()
        info = queries_db.select_info_for_order(row[0])

        spreadsheets.append_row_order(row, info)

    connection.close()
