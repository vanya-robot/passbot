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
create_users()  # Создание базы данных и таблицы Users в ней
create_orders()  # Создание таблицы Orders
create_codes()  # Создание таблиц InvitationCodes
wait = query.wait(1)


def registration(message):
    if len(message.text) != 20:
        msg = bot.send_message(message.chat.id, "Код должен состоять из 20 символов. Повторите попытку.")
        bot.register_next_step_handler(msg, registration)
    else:
        if query.if_code_exists(message.text):
            global register_data
            register_data[message.chat.id] = []
            register_data[message.chat.id].append(message.text)
            bot.send_message(message.chat.id, "Код подтверждён.")
            query.swap_code_to_used(message.text)
            query.delete_code(message.text)
            wait
            name_reg(message)
        else:
            msg_fail = bot.send_message(message.chat.id, "Код не распознан. Повторите попытку.")
            bot.register_next_step_handler(msg_fail, registration)


def registration_complete(message):
    global register_data
    register_data[message.chat.id].append(message.chat.id)
    query.add_row_users(register_data[message.chat.id][0], register_data[message.chat.id][1], register_data[message.chat.id][2],
                        register_data[message.chat.id][3], register_data[message.chat.id][4], register_data[message.chat.id][5])
    register_data.pop(message.chat.id)
    bot.send_message(message.chat.id, "Регистрация завершена. Приятного пользования!")
    wait
    bot.send_message(message.chat.id, "Для заказа пропуска нажмите /order")


def if_name_valid(message):
    wait
    if len(message.text.split()) == 3:
        global register_data
        register_data[message.chat.id].append(message.text)
        house_reg(message)
        print(register_data[message.chat.id])
    else:
        msg_name = bot.send_message(message.chat.id, "Неверный формат ввода имени. Проверьте пробелы.")
        bot.register_next_step_handler(msg_name, if_name_valid)


def name_reg(message):
    msg_name = bot.send_message(message.chat.id, "Введите имя в формате 'Фамилия Имя Отчество'.")
    bot.register_next_step_handler(msg_name, if_name_valid)


def number_reply(message):
    msg_phone = bot.send_message(message.chat.id, "Введите номер телефона в формате '74950000000'.")
    bot.register_next_step_handler(msg_phone, number_reply2)


def number_reply2(message):
    wait
    if not (message.text.isdigit() and len(message.text) == 11):
        msg_fail = bot.send_message(message.chat.id, "Некорректно введён номер телефона, повторите попытку.")
        bot.register_next_step_handler(msg_fail, number_reply)
    elif message.text.isdigit() and len(message.text) == 11:
        bot.send_message(message.chat.id, "Номер телефона подтверждён.")
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
    msg_house = bot.send_message(message.chat.id, "Введите номер своего участка.")
    bot.register_next_step_handler(msg_house, if_house_valid)


def if_house_valid(message):
    if message.text.isdigit() and len(str(message.text)) <= 3:
        bot.send_message(message.chat.id, "Номер подтверждён.")
        global register_data
        register_data[message.chat.id].append(message.text)
        print(register_data[message.chat.id])
        number_reply(message)
    elif (message.text[:len(message.text) - 1]).isdigit():
        bot.send_message(message.chat.id, "Номер подтверждён.")
        register_data[message.chat.id].append(message.text)
        print(register_data[message.chat.id])
        wait
        number_reply(message)
    else:
        msg_fail = bot.send_message(message.chat.id, "Некорректно введён номер участка, повторите попытку.")
        bot.register_next_step_handler(msg_fail, house_reg)


def order_number(message):
    number = message.text
    if len(number) != 6 or not number[1:4].isdigit() or not isinstance(number[0] + number[4:6], str)\
            or not query.check_characters(number[0] + number[4:6]):
        bot.send_message(message.chat.id, "Неверный формат ввода, повторите попытку.")
        wait
        msg_numb = bot.send_message(message.chat.id, 'Введите регистрационный номер автомобиля в виде "а123аа":')
        bot.register_next_step_handler(msg_numb, order_number)
    else:
        global order_data
        order_data[message.chat.id].append(message.text)
        query.add_row_orders(order_data[message.chat.id][0], order_data[message.chat.id][2], order_data[message.chat.id][1])
        bot.send_message(message.chat.id, "Пропуск заказан.")
        order_data.pop(message.chat.id)


def order_brand(message):
    brand = message.text
    global order_data
    order_data[message.chat.id].append(query.select_code(message))
    order_data[message.chat.id].append(brand)
    msg_numb = bot.send_message(message.chat.id, 'Введите регистрационный номер автомобиля в виде "а123аа":')
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
            bot.send_message(message.chat.id, "Код сгенерирован.\n")
            wait
            bot.send_message(message.chat.id, str(code))
        else:
            print()
    if message.text == "/help":
        bot.send_message(message.chat.id, "Список команд:\n/register - Регистрация в системе\n/order"
                                          " - Заказать пропуск")
    if message.text not in ["/order", "/start", "/register", "/botstop", "/code", "/help"]:
        bot.send_message(message.chat.id, "Команда не распознана. Для получения списка команд нажмите: /help")


def order_helper(message):
    global order_data
    order_data[message.chat.id] = []
    wait
    if query.select_code(message) is not None:
        msg_help = bot.send_message(message.chat.id, "Введите марку автомобиля:")
        bot.register_next_step_handler(msg_help, order_brand)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы. Нажмите\n/register")


def start_message(message):
    if query.select_code(message) is None:
        bot.send_message(message.chat.id, "Приветствую! Это Бот, созданный для заказа пропусков.\n "
                         + "Чтобы зарегистрироваться нажмите \n/register.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/register")
        markup.add(item1)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы. Вы можете приступить к использованию по команде "
                                          "/order")


def register_reply(message):
    if query.select_code(message) is None:
        msg1 = bot.send_message(message.chat.id, "Введите код пригласившего Вас пользователя.")
        bot.register_next_step_handler(msg1, registration)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы. Вы можете приступить к использованию по команде "
                                          "/order")


bot.infinity_polling()
