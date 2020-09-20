from aiogram.dispatcher.filters.state import StatesGroup, State


class Home(StatesGroup):
    search = State()
    conversation = State()
    profile = State()
    balance = State()


class Profile(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    occupation = State()
    about = State()
    contact = State()
    photo = State()


class EditProfile(StatesGroup):
    name = State()
    age = State()
    city = State()
    occupation = State()
    about = State()
    photo = State()


class Conversation(StatesGroup):
    chats = State()
    room = State()


class Search(StatesGroup):
    gender = State()
    city = State()
    swipes = State()
