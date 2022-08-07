
from fnmatch import translate
from hmac import trans_36
import os
import random
from random import randint
import telebot
import boto3
import json
from telebot import types
import logging
from reverso_api.context import ReversoContextAPI

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

def highlight_example(text, highlighted):
    """'Highlights' ALL the highlighted parts of the word usage example with * characters.
    Args:
        text: The text of the example
        highlighted: Indexes of the highlighted parts' indexes
    Returns:
        The highlighted word usage example
    """

    def insert_char(string, index, char):
        """Inserts the given character into a string.
        Example:
            string = "abc"
            index = 1
            char = "+"
            Returns: "a+bc"
        Args:
            string: Given string
            index: Index where to insert
            char: Which char to insert
        Return:
            String string with character char inserted at index index.
        """

        return string[:index] + char + string[index:]

    def highlight_once(string, start, end, shift):
        """'Highlights' ONE highlighted part of the word usage example with two * characters.
        Example:
            string = "This is a sample string"
            start = 0
            end = 4
            shift = 0
            Returns: "*This* is a sample string"
        Args:
            string: The string to be highlighted
            start: The start index of the highlighted part
            end: The end index of the highlighted part
            shift: How many highlighting chars were already inserted (to get right indexes)
        Returns:
            The highlighted string.
        """

        s = insert_char(string, start + shift, "`")
        s = insert_char(s, end + shift + 1, "`")
        return s

    shift = 0
    for start, end in highlighted:
        text = highlight_once(text, start, end, shift)
        shift += 2
    return text


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


def get_translations(word):
    api = ReversoContextAPI(word, "", "en", "ru")
    translations = []
    for x in sorted(api.get_translations(), key=lambda x: -x.frequency):
        translations.append(x.translation)
    return translations

def get_contexts(word):
    api = ReversoContextAPI(word, "", "en", "ru")
    examples_num = 0
    examples = []
    for source, _ in api.get_examples():
        examples.append(highlight_example(source.text, source.highlighted))
        examples_num += 1
        if examples_num == 20:
            break
    
    return examples

def get_translations_nice_str(message, word):
    data = load_user_data()
    nice_str = ''
    for translation in data[str(message.chat.id)]["words"][word]["possible_translations"][:7]:
        nice_str += '`'
        nice_str += translation
        nice_str += '`; '
    return nice_str



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
    bot.register_next_step_handler(msg, input_translate_word, True)

def input_translate_word(message, is_first=True):
    data = load_user_data()
    if is_first:
        word = data[str(message.chat.id)]["current_word"] = message.text.strip().lower()
        data[str(message.chat.id)]["words"][word] = {"translations": [], "possible_translations": [], "contexts": []}
        data[str(message.chat.id)]["words"][word]["possible_translations"] = get_translations(word)
        data[str(message.chat.id)]["words"][word]["contexts"] = get_contexts(word)
        upload_user_data(data)
    
    word = data[str(message.chat.id)]["current_word"]
    bot.send_message(message.chat.id, INPUT_TRANSLATE_WORD, reply_markup=hide_markup, parse_mode="HTML")
    bot.send_message(message.chat.id, get_translations_nice_str(message, word), reply_markup=hide_markup, parse_mode="Markdown")
    msg = bot.send_message(message.chat.id, "\n\n".join(data[str(message.chat.id)]["words"][word]["contexts"][:5]), reply_markup=hide_markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, handle_translate)

def handle_translate(message):
    data = load_user_data()
    word = data[str(message.chat.id)]["current_word"]
    data[str(message.chat.id)]["words"][word]["translations"].append(message.text.strip().lower())
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
    for word, word_translate_data in data[str(message.chat.id)]["words"].items():
        translates_str = ""
        for translate in word_translate_data["translations"]:
            translates_str += translate + '; '
        words_list_str += word + " --> " + translates_str + '\n\n'
    bot.send_message(message.chat.id, words_list_str, reply_markup=common_markup, parse_mode="HTML")
