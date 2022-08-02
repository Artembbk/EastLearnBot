
import os
import random
from random import randint
import re
import telebot
import boto3
import json
from telebot import types
import logging

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

s3 = boto3.resource(
    's3',
    aws_access_key_id='YCAJEQY_Run9ousdsHaG3SNsD',
    aws_secret_access_key='YCM11rgKrplh_QYbucxhlPq454ool15ghcunX0_N',
    region_name='ru-central1',
    endpoint_url='https://storage.yandexcloud.net'
).Bucket('easy-learn-bucket')

json.load_s3 = lambda f: json.load(s3.Object(key=f).get()["Body"])
json.dump_s3 = lambda obj, f: s3.Object(key=f).put(Body=json.dumps(obj))


def load_user_data():
    return json.load_s3("data.json")


def upload_user_data(data):
    json.dump_s3(data, "data.json")


RESET_LEARNING = 'Сбросить прогресс'

DELETE_ALL_WORDS = 'Удалить все'

DELETE_ONE = 'Удалить слово'

LIST = 'Список слов'

LEARN = 'Учить'

ADD_WORDS = 'Добавить слова'

START_MESSAGE = 'Привет! Я помогу тебе учить слова!'

INPUT_ENGLISH_WORD = 'Введите слово на английском'

INPUT_TRANSLATE_WORD = 'Введите перевод слова на русском'

WORD_ADDED = 'Добавлено слово'

ADD_TRANSLATE = 'Добавить перевод'

ADD_WORD = 'Новое слово'

END_ADDING_WORDS = 'Меню'

def create_common_markup(one_time=False):
    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=one_time)

    # Создаем кнопки
    start_learning_btn = types.KeyboardButton(RESET_LEARNING)
    learn_btn = types.KeyboardButton(LEARN)
    add_words_btn = types.KeyboardButton(ADD_WORDS)
    words_list_btn = types.KeyboardButton(LIST)
    delete_all_btn = types.KeyboardButton(DELETE_ALL_WORDS)
    delete_one_btn = types.KeyboardButton(DELETE_ONE)



    # Добавляем кнопки в клавиатуру в два ряда
    markup.add(start_learning_btn, learn_btn, add_words_btn)
    markup.add(words_list_btn, delete_all_btn, delete_one_btn)
    return markup

def create_adding_words_markup(one_time=False):
    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=one_time)

    # Создаем кнопки
    add_translate_btn = types.KeyboardButton(ADD_TRANSLATE)
    add_word_btn = types.KeyboardButton(ADD_WORD)
    end_adding_btn = types.KeyboardButton(END_ADDING_WORDS)

    # Добавляем кнопки в клавиатуру в два ряда
    markup.add(add_translate_btn, add_word_btn)
    markup.add(end_adding_btn)
    return markup


common_markup = create_common_markup()
hide_markup = types.ReplyKeyboardRemove()
adding_words_markup = create_adding_words_markup()


@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    bot.send_message(message.chat.id, START_MESSAGE, reply_markup=common_markup, parse_mode="HTML")

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == ADD_WORDS:
        add_words(message)
    elif message.text == LIST:
        list(message)

def reset_learning(message):
    data = load_user_data()
    data[str(message.chat.id)] = {"words": {},
                            "current_word": "0"}
    upload_user_data(data)

def add_words(message):
    data = load_user_data()
    if str(message.chat.id) not in data:
        reset_learning(message)

    input_word(message)
        


def input_word(message):
    msg = bot.send_message(message.chat.id, INPUT_ENGLISH_WORD, reply_markup=hide_markup, parse_mode="HTML")
    bot.register_next_step_handler(msg, input_translate_word)

def input_translate_word(message, is_first=True):
    if is_first:
        data = load_user_data()
        word = data[str(message.chat.id)]["current_word"] = message.text.strip().lower()
        data[str(message.chat.id)]["words"].setdefault(word, [])
        upload_user_data(data)
    msg = bot.send_message(message.chat.id, INPUT_TRANSLATE_WORD, reply_markup=hide_markup, parse_mode="HTML")
    bot.register_next_step_handler(msg, handle_translate)

def handle_translate(message):
    data = load_user_data()
    word = data[str(message.chat.id)]["current_word"]
    data[str(message.chat.id)]["words"][word].append(message.text.strip().lower())
    upload_user_data(data)
    msg = bot.send_message(message.chat.id, WORD_ADDED, reply_markup=adding_words_markup, parse_mode="HTML")
    bot.register_next_step_handler(msg, after_added_word)

def after_added_word(message):
    if message.text == ADD_WORD:
        input_word(message)
    elif message.text == ADD_TRANSLATE:
        input_translate_word(message, False)
    elif message.text == END_ADDING_WORDS:
        bot.send_message(message.chat.id, "Вы вышли из режима добавления слов", reply_markup=common_markup, parse_mode="HTML")

def list(message):
    words_list_str = ''
    data = load_user_data()
    for word, translates in data[str(message.chat.id)]["words"].items():
        translates_str = ""
        for translate in translates:
            translates_str += translate + '; '
        words_list_str += word + " --> " + translates_str + '\n\n'
    bot.send_message(message.chat.id, words_list_str, reply_markup=common_markup, parse_mode="HTML")
