from custom_json import addData, delData, getData
import openai
from random import choice
import json
from aiogram import types


# Функция для выдали фразы из базы с текстами
def getPhrase(key):
  texts_data = getData('data/texts.json')
  phrase = texts_data[key]
  if type(phrase) == list:
    return choice(phrase)
  return phrase


def keyboardRegroup(*args):
  keyboard = types.InlineKeyboardMarkup()
  for iteration_button in args:
    if isinstance(iteration_button, list):
      for button in iteration_button:
        keyboard.add(iteration_button)
        print('igoigrjeroig')
    else:
      keyboard.add(iteration_button)
  return keyboard


def findUserById(user_id):
  with open('data/users.json', 'r', encoding='utf-8') as json_file:
    user_list = json.load(json_file)
  for user in user_list:
    if user['user_id'] == user_id:
      return user
  return None


def generateResponse(prompt):
  settings = getData("data/gpt_settings.json")
  openai.api_key = settings["openai key"]
  completions = openai.Completion.create(engine=settings["engine"],
                                         prompt=prompt,
                                         max_tokens=settings["max_tokens"],
                                         n=settings["n"],
                                         stop=None,
                                         temperature=settings["temperature"])

  message = completions.choices[0].text.strip()
  return message
