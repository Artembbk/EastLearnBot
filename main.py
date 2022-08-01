import os
import random
from random import randint
import telebot
import boto3
import json
from telebot import types
import logging

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я помогу тебе учить слова на английском!")
