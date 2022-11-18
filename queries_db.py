import sqlite3
import datetime
import time


def add_row_users(inviter_code, name, house_num, phone, code, chat_id):
    insert_query = '''INSERT INTO Users (Phone, Name, House_num, Code, Inviter_code, Chat_Id)
                        VALUES(?,?,?,?,?,?)'''
    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()

    row = [phone, name, house_num, code, inviter_code, chat_id]

    cursor.execute(insert_query, row)

    connection.commit()
    connection.close()


def add_row_orders(code, car_num, car_brand):
    insert_query = '''INSERT INTO Orders (Code, Car_num, Car_brand, Time)
                        VALUES(?,?,?,?)'''
    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()

    row = [code, car_num, car_brand, datetime.datetime.now()]

    cursor.execute(insert_query, row)

    connection.commit()
    connection.close()


def add_new_code(code, admin_id):
    insert_query = '''INSERT INTO InvitationCodes (Code, Creator)
                            VALUES(?,?)'''
    code = (code, admin_id)

    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()
    cursor.execute(insert_query, code)

    connection.commit()
    connection.close()


def if_code_exists(code):
    select_query = '''SELECT Code FROM InvitationCodes WHERE Code = ?'''
    code = (code,)

    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()
    cursor.execute(select_query, code)
    result = cursor.fetchall()

    return len(result) != 0


def swap_code_to_used(code):
    insert_query = '''INSERT INTO UsedCodes (Code, Creator)
                        SELECT Code, Creator FROM InvitationCodes
                        WHERE Code = ?'''
    code = (code,)

    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()
    cursor.execute(insert_query, code)

    connection.commit()
    connection.close()


def delete_code(code):
    delete_query = '''DELETE FROM InvitationCodes WHERE Code = ?'''
    code = (code,)

    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()
    cursor.execute(delete_query, code)
    connection.commit()

    connection.close()


def select_code(message):
    chat_id = (message.chat.id,)
    select_query = '''SELECT Code FROM Users WHERE Chat_Id = ?'''

    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()
    cursor.execute(select_query, chat_id)
    try:
        return cursor.fetchone()[0]

    except TypeError:
        print(None)
        connection.close()
        return None


def select_info_for_order(code):

    connection = sqlite3.connect('vol/strawberry.db')
    select_query = '''SELECT Name, Phone, House_num FROM Users WHERE Code = ?'''
    code = (code,)
    cursor = connection.cursor()
    cursor.execute(select_query, code)

    return cursor.fetchone()


def wait(sec):
    time.sleep(sec)


def check_for_admin(id):
    with open('vol/admins.txt') as f:
        contents = f.readlines()
        return str(id) in list(map(lambda x: x.strip(), contents))


def check_characters(chars):
    characters_upper = ["А", "В", "Е", "К", "М", "Н", "О", "Р", "С", "Т", "У", "Х"]
    characters_lower = ["а", "в", "е", "к", "м", "н", "о", "р", "с", "т", "у", "х"]
    for i in range(3):
        if chars[i] in characters_lower or chars[i] in characters_upper:
            continue
        else:
            return False
    return True
