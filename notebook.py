from configure import TOKEN
import telebot
import pickle
from telebot import types
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup  # States
from telebot.storage import StateMemoryStorage

bot = telebot.TeleBot(TOKEN)


class Contact(StatesGroup):
    name = State()
    surname = State()
    phone = State()
    address = State()
    age = State()


#  File manager
def check_contacts(user_id):
    with open(f'{user_id}.txt', 'rb') as f:
        print(pickle.load(f))
        contacts_list = pickle.load(f)
        return contacts_list


def add_contact(user_id, user_data):
    with open(f'{user_id}.txt', 'wb') as f:
        pickle.dump(user_data, f)
        f.write(pickle.dumps(user_data))


#  First Bot Start. Create file with Contacts
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('📒 Контакты')
    item2 = types.KeyboardButton('🆕 Добавить')
    item3 = types.KeyboardButton('🔚 Выход')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}!'.format(message.from_user), reply_markup=markup)
    try:
        check_contacts(message.chat.id)
    except FileNotFoundError:
        user_data = []
        add_contact(message.chat.id, user_data)
        print('contact was added')


# Contacts Data
@bot.message_handler(state=Contact.name)
def name_get(message):
    """
    State 1. Will process when user's state is MyStates.name.
    """
    bot.send_message(message.chat.id, 'Now write me a surname')
    bot.set_state(message.from_user.id, Contact.surname, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=Contact.surname)
def ask_age(message):
    """
    State 2. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "What is your phone?")
    bot.set_state(message.from_user.id, Contact.age, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text


@bot.message_handler(state=Contact.phone)
def ask_phone(message):
    """
    State 3. Will process when user's state is MyStates.phone.
    """
    bot.send_message(message.chat.id, "What is your phone?")
    bot.set_state(message.from_user.id, Contact.address, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['phone'] = message.text


@bot.message_handler(state=Contact.address)
def ask_address(message):
    """
    State 4. Will process when user's state is MyStates.surname.
    """
    bot.send_message(message.chat.id, "What is your phone?")
    bot.set_state(message.from_user.id, Contact.age, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['address'] = message.text


# result
@bot.message_handler(state=Contact.age, is_digit=True)
def ready_for_answer(message):
    """
    State 3. Will process when user's state is MyStates.age.
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        msg = ("Ready, take a look:\n<b>"
               f"Name: {data['name']}\n"
               f"Surname: {data['surname']}\n"
               f"Age: {message.text}</b>")
        bot.send_message(message.chat.id, msg, parse_mode="html")
    bot.delete_state(message.from_user.id, message.chat.id)


# incorrect number
@bot.message_handler(state=Contact.age, is_digit=False)
def age_incorrect(message):
    """
    Wrong response for MyStates.age
    """
    bot.send_message(message.chat.id, 'Looks like you are submitting a string in the field age. Please enter a number')


# register filters

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())


#  Add NEW Contact
@bot.message_handler(content_types=['text'])
def start_ex(message):
    if message.chat.type == 'private':
        if message.text == '🆕 Добавить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('◀️Назад')
            markup.add(back)
            bot.set_state(message.from_user.id, Contact.name, message.chat.id)
            print('go')
            bot.send_message(message.chat.id, 'Hi, write me a name')
        elif message.text == '◀️Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('📒 Контакты')
            item2 = types.KeyboardButton('🆕 Добавить')
            item3 = types.KeyboardButton('🔚 Выход')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, '{0.first_name}, вы отменили создание контакта'.format(message.from_user),
                             reply_markup=markup)
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            ...
    else:
        ...


bot.polling(none_stop=True)
