from configure import TOKEN
import telebot
import pickle
from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from models import *

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN)
contact_id = 0


#  File manager
def check_contacts(user_id):
    with open(f'{user_id}.txt', 'rb') as f:
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
    item1 = types.KeyboardButton(f'📒 Контакты')
    item2 = types.KeyboardButton('🆕 Добавить')
    item3 = types.KeyboardButton('🔍 Поиск')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}!'.format(message.from_user), reply_markup=markup)
    try:
        check_contacts(message.chat.id)
    except FileNotFoundError:
        user_data = []
        add_contact(message.chat.id, user_data)
        print('contact was added')


@bot.message_handler(state="*", regexp='Назад')
def any_state(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('📒 Контакты')
    item2 = types.KeyboardButton('🆕 Добавить')
    item3 = types.KeyboardButton('🔍 Поиск')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Главное меню'.format(message.from_user),
                     reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)


# Contacts new Data
@bot.message_handler(state=Contact.name)
def name_get(message):
    bot.send_message(message.chat.id, 'Теперь фамилию')
    bot.set_state(message.from_user.id, Contact.surname, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=Contact.surname)
def ask_surname(message):
    bot.send_message(message.chat.id, "Номер телефона")
    bot.set_state(message.from_user.id, Contact.phone, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text


@bot.message_handler(state=Contact.phone)
def ask_phone(message):
    bot.send_message(message.chat.id, "Уточните имейл")
    bot.set_state(message.from_user.id, Contact.email, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['phone'] = message.text


@bot.message_handler(state=Contact.email)
def ask_address(message):
    bot.send_message(message.chat.id, "Дата рождения")
    bot.set_state(message.from_user.id, Contact.age, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['email'] = message.text


# result
@bot.message_handler(state=Contact.age)
def ready_for_answer(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text
        msg = ("<b>Новая запись 🧾:\n</b>"
               f"<b>Имя:</b> {data['name']}\n"
               f"<b>Фамилия:</b> {data['surname']}\n"
               f"<b>📱 Мобильный:</b> {data['phone']}\n"
               f"<b>📧 Email:</b> {data['email']}\n"
               f"<b>🪪 День рождения:</b> {data['age']}")
        bot.send_message(message.chat.id, msg, parse_mode="html")
    contact = check_contacts(message.chat.id)
    contact.append(data)
    add_contact(message.chat.id, contact)
    bot.delete_state(message.from_user.id, message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('📒 Контакты')
    item2 = types.KeyboardButton('🆕 Добавить')
    item3 = types.KeyboardButton('🔍 Поиск')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Контакт успешно создан.'.format(message.from_user),
                     reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))


#  Update contact
@bot.message_handler(state=Phone.value)
def name_update(message):
    bot.send_message(message.chat.id, 'Спасибо')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('По имени')
    item2 = types.KeyboardButton('По фамилии')
    item3 = types.KeyboardButton('◀️ Назад')
    markup.add(item1, item2, item3)
    if len(check_contacts(message.chat.id)) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['value'] = message.text
        bot.delete_state(message.from_user.id, message.chat.id)
        temp = check_contacts(message.chat.id)
        temp[int(contact_id) - 1]['phone'] = data['value']
        add_contact(message.chat.id, temp)
        msg = ("<b>Номер обновлен 🧾:\n</b>"
               f"<b>Имя:</b> {temp[int(contact_id) - 1]['name']}\n"
               f"<b>Фамилия:</b> {temp[int(contact_id) - 1]['surname']}\n"
               f"<b>📱 Мобильный:</b> {temp[int(contact_id) - 1]['phone']}\n"
               f"<b>📧 Email:</b> {temp[int(contact_id) - 1]['email']}\n"
               f"<b>🪪 День рождения:</b> {temp[int(contact_id) - 1]['age']}")
        bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Все контакты удалены', reply_markup=markup)


#  Search contact
@bot.message_handler(state=Search.value)
def name_update(message):
    bot.send_message(message.chat.id, 'Поиск...')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['value'] = message.text
    bot.delete_state(message.from_user.id, message.chat.id)
    temp = check_contacts(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('◀️ Назад')
    markup.add(back)
    x = 0
    for i in range(len(temp)):
        if temp[i]['name'] == message.text or temp[i]['phone'] == message.text:
            x += 1
            msg = (
                f"<b>Имя:</b> {temp[i]['name']}\n"
                f"<b>Фамилия:</b> {temp[i]['surname']}\n"
                f"<b>📱 Мобильный:</b> {temp[i]['phone']}\n"
                f"<b>📧 Email:</b> {temp[i]['email']}\n"
                f"<b>🪪 День рождения:</b> {temp[i]['age']}")
            bot.send_message(message.chat.id, msg, parse_mode="html")
    if x == 0:
        bot.send_message(message.chat.id, 'Поиск завершен. Найденных контактов: 0',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Поиск завершен. Найденных контактов: {x}',
                         reply_markup=markup)


#  Add NEW Contact
@bot.message_handler(content_types=['text'])
def start_ex(message):
    if message.chat.type == 'private':
        if message.text == '🆕 Добавить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('◀️ Назад')
            markup.add(back)
            bot.set_state(message.from_user.id, Contact.name, message.chat.id)
            bot.send_message(message.chat.id, 'Введите имя', reply_markup=markup)
        elif message.text == '📒 Контакты':
            msg1 = check_contacts(message.chat.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('По имени')
            item2 = types.KeyboardButton('По фамилии')
            item3 = types.KeyboardButton('◀️ Назад')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, f'Всего контактов: {len(msg1)}',
                             reply_markup=markup)
            if len(msg1) > 0:
                for i in range(len(msg1)):
                    msg = (f"<b>{i + 1}. {msg1[i]['name']} {msg1[i]['surname']} 🧾:\n</b>"
                           f"<b>📱 Мобильный:</b> {msg1[i]['phone']}\n"
                           f"<b>📧 Email:</b> {msg1[i]['email']}\n"
                           f"<b>🪪 День рождения:</b> {msg1[i]['name']}")
                    markup_inline = types.InlineKeyboardMarkup()
                    item_del = types.InlineKeyboardButton(text='Удалить', callback_data='delete')
                    item_change = types.InlineKeyboardButton(text='Изменить номер', callback_data='change')
                    markup_inline.add(item_change, item_del)
                    bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=markup_inline)
            else:
                bot.send_message(message.chat.id, 'Список контактов пуст')
        elif message.text == '🔍 Поиск':
            if len(check_contacts(message.chat.id)) > 0:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('◀️ Назад')
                markup.add(back)
                bot.set_state(message.from_user.id, Search.value, message.chat.id)
                bot.send_message(message.chat.id, 'Введите Имя или номер телефона полностью для осуществления '
                                                  'поиска', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Список контактов пуст')
        elif message.text == 'По имени' or message.text == 'По фамилии':
            temp = []
            if message.text == 'По имени':
                temp = sorted(check_contacts(message.chat.id), key=lambda k: k['name'])
            elif message.text == 'По фамилии':
                temp = sorted(check_contacts(message.chat.id), key=lambda k: k['surname'])
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('По имени')
            item2 = types.KeyboardButton('По фамилии')
            item3 = types.KeyboardButton('◀️ Назад')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, f'Всего контактов: {len(temp)}',
                             reply_markup=markup)
            for i in range(len(temp)):
                msg = (f"<b>{i + 1}. {temp[i]['name']} {temp[i]['surname']} 🧾:\n</b>"
                       f"<b>📱 Мобильный:</b> {temp[i]['phone']}\n"
                       f"<b>📧 Email:</b> {temp[i]['email']}\n"
                       f"<b>🪪 День рождения:</b> {temp[i]['name']}")
                markup_inline = types.InlineKeyboardMarkup()
                item_del = types.InlineKeyboardButton(text='Удалить', callback_data='delete')
                item_change = types.InlineKeyboardButton(text='Изменить номер', callback_data='change')
                markup_inline.add(item_change, item_del)
                bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=markup_inline)


#  Inline Buttons Callback
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'delete':
        msg1 = check_contacts(call.message.chat.id)
        if len(msg1) > 0:
            msg1.pop(int(call.message.text[0]) - 1)
            add_contact(call.message.chat.id, msg1)
            if len(msg1) != 0:
                bot.send_message(call.message.chat.id, f'Контакт успешно удален.')
                for i in range(len(msg1)):
                    msg = (f"<b>{i + 1}. {msg1[i]['name']} {msg1[i]['surname']} 🧾:\n</b>"
                           f"<b>📱 Мобильный:</b> {msg1[i]['phone']}\n"
                           f"<b>📧 Email:</b> {msg1[i]['email']}\n"
                           f"<b>🪪 День рождения:</b> {msg1[i]['name']}")
                    markup_inline = types.InlineKeyboardMarkup()
                    item_del = types.InlineKeyboardButton(text='Удалить', callback_data='delete')
                    item_change = types.InlineKeyboardButton(text='Изменить', callback_data='change')
                    markup_inline.add(item_change, item_del)
                    bot.send_message(call.message.chat.id, msg, parse_mode="html", reply_markup=markup_inline)
            else:
                bot.send_message(call.message.chat.id, f'Удален последний контакт. Справочник теперь пуст')
        else:
            bot.send_message(call.message.chat.id, 'Ваш список контактов теперь пуст')
    elif call.data == 'change':
        bot.set_state(call.from_user.id, Phone.value, call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Укажите новый номер')
        global contact_id
        contact_id = call.message.text[0]


bot.polling(none_stop=True)
