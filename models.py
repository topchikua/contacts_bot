from telebot.handler_backends import State, StatesGroup


class Contact(StatesGroup):
    name = State()
    surname = State()
    phone = State()
    email = State()
    age = State()


class Phone(StatesGroup):
    value = State()


class Search(StatesGroup):
    value = State()
