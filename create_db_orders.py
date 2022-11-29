import sqlite3


def create_orders():
    connection = sqlite3.connect('vol/passbot.db')
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (Number INTEGER PRIMARY KEY not null, Code TEXT not null, 
    Car_num TEXT not null, Car_brand TEXT, Time TIMESTAMP, Time_of_arrival TIMESTAMP, Status INT DEFAULT 0)''')

    connection.commit()
    connection.close()
