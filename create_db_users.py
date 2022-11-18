import sqlite3


def create_users():
    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (Phone INT PRIMARY KEY not null, Name TEXT not null, 
    House_num TEXT not null, Code TEXT not null, Inviter_Code TEXT not null, Chat_Id INT not null)''')

    connection.commit()
    connection.close()


def create_codes():
    connection = sqlite3.connect('vol/strawberry.db')
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS InvitationCodes (Code TEXT, Creator TEXT)''')
    connection.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS UsedCodes (Code TEXT, Creator TEXT)''')
    connection.commit()

    connection.close()
