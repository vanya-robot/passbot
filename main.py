import telebot
from telebot import types
from codegen import generate_code
import queries_db as query
from create_db_orders import create_orders
from create_db_users import create_users, create_codes

with open('vol/token.txt') as token:
    token = token.readline()

bot = telebot.TeleBot(token)

bot.remove_webhook()

register_data = {}  # [Inviter_code, Name, House_num, Phone, Code, Chat_id]
order_data = {}  # [code, car_num, car_brand]
create_users()  # Create database and Users table in it
create_orders()  # Create Orders table
create_codes()  # Create InvitationCodes tables
wait = query.wait(1)


def registration(message):
    if len(message.text) != 20:
        msg = bot.send_message(message.chat.id, "Code must be 20 characters long. Try again.")
        bot.register_next_step_handler(msg, registration)
    else:
        if query.if_code_exists(message.text):
            global register_data
            register_data[message.chat.id] = []
            register_data[message.chat.id].append(message.text)
            bot.send_message(message.chat.id, "Code accepted.")
            query.swap_code_to_used(message.text)
            query.delete_code(message.text)
            wait
            name_reg(message)
        else:
            msg_fail = bot.send_message(message.chat.id, "Can't recognise the code. Try again.")
            bot.register_next_step_handler(msg_fail, registration)


def registration_complete(message):
    global register_data
    register_data[message.chat.id].append(message.chat.id)
    query.add_row_users(register_data[message.chat.id][0], register_data[message.chat.id][1], register_data[message.chat.id][2],
                        register_data[message.chat.id][3], register_data[message.chat.id][4], register_data[message.chat.id][5])
    register_data.pop(message.chat.id)
    bot.send_message(message.chat.id, "Registration completed.")
    wait
    bot.send_message(message.chat.id, "To order a pass print: /order")


def if_name_valid(message):
    wait
    if len(message.text.split()) == 3:
        global register_data
        register_data[message.chat.id].append(message.text)
        house_reg(message)
        print(register_data[message.chat.id])
    else:
        msg_name = bot.send_message(message.chat.id, "Invalid format of name. Check spaces.")
        bot.register_next_step_handler(msg_name, if_name_valid)


def name_reg(message):
    msg_name = bot.send_message(message.chat.id, "Print your name like: 'Name Surname Patronymic'.")
    bot.register_next_step_handler(msg_name, if_name_valid)


def number_reply(message):
    msg_phone = bot.send_message(message.chat.id, "Print your phone number like: 'XXXXXXXXXXX'.")
    bot.register_next_step_handler(msg_phone, number_reply2)


def number_reply2(message):
    wait
    if not (message.text.isdigit() and len(message.text) == 11):
        msg_fail = bot.send_message(message.chat.id, "Incorrect format. Try again.")
        bot.register_next_step_handler(msg_fail, number_reply)
    elif message.text.isdigit() and len(message.text) == 11:
        bot.send_message(message.chat.id, "Phone number accepted.")
        register_data[message.chat.id].append(message.text)
        print(register_data[message.chat.id])
        wait
        code_reg(message)


def code_reg(message):
    code = generate_code()
    global register_data
    register_data[message.chat.id].append(code)
    print(register_data[message.chat.id])
    registration_complete(message)


def house_reg(message):
    msg_house = bot.send_message(message.chat.id, "Enter your house number.")
    bot.register_next_step_handler(msg_house, if_house_valid)


def if_house_valid(message):
    if message.text.isdigit() and len(str(message.text)) <= 3:
        bot.send_message(message.chat.id, "House number accepted.")
        global register_data
        register_data[message.chat.id].append(message.text)
        print(register_data[message.chat.id])
        number_reply(message)
    elif (message.text[:len(message.text) - 1]).isdigit():
        bot.send_message(message.chat.id, "House number accepted.")
        register_data[message.chat.id].append(message.text)
        print(register_data[message.chat.id])
        wait
        number_reply(message)
    else:
        msg_fail = bot.send_message(message.chat.id, "Incorrect house number format. Try again.")
        bot.register_next_step_handler(msg_fail, house_reg)


def order_number(message):
    number = message.text
    if len(number) != 6 or not number[1:4].isdigit() or not isinstance(number[0] + number[4:6], str)\
            or not query.check_characters(number[0] + number[4:6]):
        bot.send_message(message.chat.id, "Incorrect format. Try again.")
        wait
        msg_numb = bot.send_message(message.chat.id, 'Enter license plate number as "а123аа":')
        bot.register_next_step_handler(msg_numb, order_number)
    else:
        global order_data
        order_data[message.chat.id].append(message.text)
        query.add_row_orders(order_data[message.chat.id][0], order_data[message.chat.id][2], order_data[message.chat.id][1])
        bot.send_message(message.chat.id, "Pass ordered.")
        order_data.pop(message.chat.id)


def order_brand(message):
    brand = message.text
    global order_data
    order_data[message.chat.id].append(query.select_code(message))
    order_data[message.chat.id].append(brand)
    msg_numb = bot.send_message(message.chat.id, 'Enter license plate number as "а123аа":')
    bot.register_next_step_handler(msg_numb, order_number)


@bot.message_handler(content_types=["text"])  # Order, start, register, stop, code function
def order_message(message):
    if message.text == "/order":
        order_helper(message)
    if message.text == "/start":
        start_message(message)
    if message.text == "/register":
        register_reply(message)
    if message.text == "/code":
        if query.check_for_admin(message.chat.id):
            code = generate_code()
            query.add_new_code(code, message.chat.id)
            bot.send_message(message.chat.id, "Code generated.\n")
            wait
            bot.send_message(message.chat.id, str(code))
        else:
            print()
    if message.text == "/help":
        bot.send_message(message.chat.id, "List of commands:\n/register - Registration in system\n/order"
                                          " - Order a pass")
    if message.text not in ["/order", "/start", "/register", "/botstop", "/code", "/help"]:
        bot.send_message(message.chat.id, "Can't recognise the command. Try /help")


def order_helper(message):
    global order_data
    order_data[message.chat.id] = []
    wait
    if query.select_code(message) is not None:
        msg_help = bot.send_message(message.chat.id, "Enter car brand.")
        bot.register_next_step_handler(msg_help, order_brand)
    else:
        bot.send_message(message.chat.id, "You are not registred. Use\n/register")


def start_message(message):
    if query.select_code(message) is None:
        bot.send_message(message.chat.id, "Greetings! This is a Bot created to order car passes to a closed area.\n "
                         + "To register print \n/register.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/register")
        markup.add(item1)
    else:
        bot.send_message(message.chat.id, "You are already registered. To order a pass enter: "
                                          "/order")


def register_reply(message):
    if query.select_code(message) is None:
        msg1 = bot.send_message(message.chat.id, "Enter registration code.")
        bot.register_next_step_handler(msg1, registration)
    else:
        bot.send_message(message.chat.id, "You are already registered. To order a pass enter: "
                                          "/order")


bot.infinity_polling()
