from curses import reset_shell_mode
from http.client import RESET_CONTENT
from lib2to3.pgen2.token import STAR
import os
from pickle import ADDITEMS
import random
from random import randint
import telebot
import boto3
import json
from telebot import types
import logging

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

s3 = boto3.resource(
    's3',
    aws_access_key_id='YCAJEibMQ54FsR4sCwWVeQOtW',
    aws_secret_access_key='YCPyoSsswGbWGS_dlAcoLmbfOEgyDZJLgyQ1_bjD',
    region_name='ru-central1',
    endpoint_url='https://storage.yandexcloud.net'
).Bucket('nplb')

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


common_markup = create_common_markup()


@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    bot.send_message(message.chat.id, START_MESSAGE, reply_markup=common_markup, parse_mode="HTML")
