import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
import aiogram.utils.markdown as md
from custom_json import getData, addData, delData
from auxiliary_modules import getPhrase, generateResponse, keyboardRegroup, findUserById
from traceback import format_exc

bot_config = getData("data/settings.json")

API_TOKEN = bot_config["api token"]  # Токен от telegram бота

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
message_ids = {}
message_types = {}
is_anonim = {}
groups = getData('data/groups.json')
memes = {}
functions = {
  "suggestion": "Предложка",
  "history function": "Бронирование параграфов",
  "homeworks check": "Домашние задания",
  "general suggestion": "Отправка на публикацию"
}


@dp.message_handler(commands=['hello'])
async def hello_world(message: types.Message):
  await bot.send_message(chat_id="-1001764913156", text="Hello, World!")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
  chat_id = message.chat.id  # Получение chat_id
  user_id = message.from_user.id  # Получение user_id

  user_info = findUserById(user_id)
  if user_info == None:
    first_name = message.from_user.first_name
  else:
    first_name = findUserById(user_id)["first_name"]

  start_button = types.InlineKeyboardButton(text="Начать",
                                            callback_data="start work")

  help_button = types.InlineKeyboardButton(text="Помощь",
                                           callback_data="help from start")

  bot_message = await bot.send_message(
    text=getPhrase("welcome").format(first_name),
    chat_id=chat_id,
    reply_markup=keyboardRegroup(start_button, help_button))

  message_types[chat_id] = "start"
  message_ids[chat_id] = [bot_message.message_id]


@dp.callback_query_handler(lambda call: call.data == 'help from start')
async def help_from_start(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id

  if message_types[chat_id] == "help":
    text = getPhrase("help choice (again)")
  else:
    text = getPhrase("help choice")

  start_button = types.InlineKeyboardButton(text="Начать",
                                            callback_data="start work")

  how_to_use_button = types.InlineKeyboardButton(text="Как пользоваться?",
                                                 callback_data="how to use")

  functions_help_button = types.InlineKeyboardButton(
    text="Функции", callback_data="functions help")

  bot_message = await bot.edit_message_text(
    text=text,
    message_id=message_ids[chat_id][-1],
    chat_id=chat_id,
    reply_markup=keyboardRegroup(start_button, how_to_use_button,
                                 functions_help_button)
    if message_types[chat_id] == "help" else keyboardRegroup(
      how_to_use_button, functions_help_button))

  #message_ids[chat_id] = [bot_message.message_id]


@dp.callback_query_handler(lambda call: call.data == 'start work')
async def start_work(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id
  is_anonim[chat_id] = False

  buttons = []

  for function in functions:
    function_button = types.InlineKeyboardButton(
      text=functions[function], callback_data=f'{function} function')
    buttons.append([function_button])

  help_button = types.InlineKeyboardButton(text="Помощь",
                                           callback_data="help from start")

  buttons.append([help_button])

  reply_markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)

  bot_message = await bot.edit_message_text(
    text="Выберите функцию",
    message_id=message_ids[chat_id][-1],
    chat_id=chat_id,
    reply_markup=reply_markup)


@dp.callback_query_handler(
  lambda call: call.data in
  ["suggestion function", "suggestion function (again)"])
async def suggestion_function(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id

  back_button = types.InlineKeyboardButton(text='Отмена',
                                           callback_data="start work")

  if callback.data == "suggestion function (again)":
    if is_anonim[chat_id] == False:
      is_anonim[chat_id] = True
    else:
      is_anonim[chat_id] = False

  message_types[user_id] = "suggestion"

  if is_anonim[chat_id] == True:
    anonim_text = "Анонимность ✅"
    await bot.answer_callback_query(callback.id,
                                    text="Теперь сообщение будет анонимным",
                                    show_alert=False,
                                    cache_time=5)
  else:
    anonim_text = "Анонимность ❌"

  anonim_button = types.InlineKeyboardButton(
    text=anonim_text, callback_data="suggestion function (again)")

  if callback.data == "suggestion function (again)":
    bot_message = await bot.edit_message_reply_markup(
      message_id=message_ids[chat_id][-1],
      chat_id=chat_id,
      reply_markup=keyboardRegroup(anonim_button, back_button))
  else:
    bot_message = await bot.edit_message_text(
      text="Напишите своё сообщение мемоделам",
      message_id=message_ids[chat_id][-1],
      chat_id=chat_id,
      reply_markup=keyboardRegroup(anonim_button, back_button))

  message_types[chat_id] = 'suggestion'


@dp.callback_query_handler(
  lambda call: call.data == 'general suggestion function')
async def general_suggestion_function(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id

  back_button = types.InlineKeyboardButton(text='Отмена',
                                           callback_data="start work")

  if str(chat_id) not in groups["meme creators"]:
    await bot.answer_callback_query(callback.id,
                                    text="Вы не являетесь мемоделом",
                                    show_alert=False,
                                    cache_time=5)
  else:
    bot_message = await bot.edit_message_text(
      text="Отправьте свой мем на рассмотрение к отправке",
      message_id=message_ids[chat_id][-1],
      chat_id=chat_id,
      reply_markup=keyboardRegroup(back_button))
    message_types[chat_id] = 'general suggestion'


@dp.callback_query_handler(lambda call: call.data == 'functions help')
async def functions_help(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id
  buttons = []

  for function in functions:
    function_button = types.InlineKeyboardButton(
      text=functions[function], callback_data=f'{function}_function_help')
    buttons.append([function_button])

  exit_button = types.InlineKeyboardButton(text="Назад",
                                           callback_data="help from start")
  buttons.append([exit_button])

  reply_markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)

  bot_message = await bot.edit_message_text(
    text="Информация о какой функции Вас интересует?",
    message_id=message_ids[chat_id][-1],
    chat_id=chat_id,
    reply_markup=reply_markup)

  message_types[chat_id] = "help"


@dp.callback_query_handler(lambda call: call.data == 'how to use')
async def how_to_use_help(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id

  exit_button = types.InlineKeyboardButton(text="Назад",
                                           callback_data="help from start")

  bot_message = await bot.edit_message_text(
    text=getPhrase("how to use help"),
    message_id=message_ids[chat_id][-1],
    chat_id=chat_id,
    reply_markup=keyboardRegroup(exit_button))

  message_types[chat_id] = "help"


@dp.callback_query_handler(lambda call: call.data.endswith("_function_help"))
async def functions_help(callback: types.CallbackQuery):
  user_id = callback.message.from_user.id
  chat_id = callback.message.chat.id

  exit_button = types.InlineKeyboardButton(text="Назад",
                                           callback_data="help from start")

  bot_message = await bot.edit_message_text(
    text=getPhrase(f"{str(callback.data).split('_')[0]} help"),
    message_id=message_ids[chat_id][-1],
    chat_id=chat_id,
    reply_markup=keyboardRegroup(exit_button))


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def get_photo(message: types.Message):
  user_id = message.from_user.id
  chat_id = message.chat.id

  if message_types[user_id] == 'suggestion':
    back_button = types.InlineKeyboardButton(text='Назад',
                                             callback_data="start work")
    caption = '<i>' + str(message.caption) + '</i>' + "\n\n"
    if "None" in caption:
      caption = ""
    photo = message.photo[-1]

    if is_anonim[chat_id] == False:
      from_user = f"👤 <code>{message.from_user.username}</code>;"
    else:
      from_user = f"👤 <code>Аноним</code>;"

    for meme_creator_chat_id in groups["meme creators"]:
      bot_message = await bot.send_photo(chat_id=meme_creator_chat_id,
                                         photo=photo.file_id,
                                         caption=caption + from_user,
                                         parse_mode="HTML")

    bot_message = await bot.send_message(
      chat_id=chat_id,
      text='Сообщение отправлено!',
      reply_markup=keyboardRegroup(back_button))
  elif message_types[user_id] == 'general suggestion':
    add_tags_button = types.InlineKeyboardButton(text="Добавить теги",
                                                 callback_data="add tags")
    approve_button = types.InlineKeyboardButton(
      text="Одобрить ✅",
      callback_data=f"approve meme:{bot_message.message_id}")
    reject_button = types.InlineKeyboardButton(
      text="Отклонить ❌",
      callback_data=f"reject meme:{bot_message.message_id}")

    admin_keyboard = types.InlineKeyboardMarkup()

    photo = message.photo[-1]
    caption = str(message.caption) + "\n\n"

    back_button = types.InlineKeyboardButton(text='Назад',
                                             callback_data="start work")
    if "None" in caption:
      caption = ""

    from_user = from_user = f"<i>Автор мема: {findUserById(user_id)['last_name']} {findUserById(user_id)['first_name'][0]}.</i>"

    bot_message = await bot.send_photo(chat_id=groups["admin"],
                                       photo=photo.file_id,
                                       caption=caption + from_user,
                                       parse_mode="HTML")

    memes[bot_message.message_id] = bot_message

    bot_message = await bot.send_message(chat_id=chat_id,
                                         text='Сообщение отправлено!',
                                         reply_markup=admin_keyboard)

  message_ids[chat_id] = [bot_message.message_id]


@dp.message_handler(content_types=types.ContentType.TEXT)
async def get_text(message: types.Message):
  user_id = message.from_user.id
  chat_id = message.chat.id

  back_button = types.InlineKeyboardButton(text='Назад',
                                           callback_data="start work")

  if message_types[user_id] == 'suggestion':
    caption = '<i>' + str(message.text) + '</i>' + "\n\n"
    if caption == "'<i>'None'</i>'\n\n":
      caption = ""

    if is_anonim[chat_id] == False:
      from_user = f"👤 <code>{message.from_user.username}</code>;"
    else:
      from_user = f"👤 <code>Аноним</code>;"

    for meme_creator_chat_id in groups["meme creators"]:
      bot_message = await bot.send_message(chat_id=meme_creator_chat_id,
                                           text=caption + from_user,
                                           parse_mode="HTML")

    bot_message = await bot.send_message(
      chat_id=chat_id,
      text='Сообщение отправлено!',
      reply_markup=keyboardRegroup(back_button))

    message_ids[chat_id] = [bot_message.message_id]
  elif message_types[user_id] == 'general suggestion':
    add_tags_button = types.InlineKeyboardButton(text="Добавить теги",
                                                 callback_data="add tags")
    approve_button = types.InlineKeyboardButton(
      text="Одобрить ✅",
      callback_data=f"approve meme:{bot_message.message_id}")
    reject_button = types.InlineKeyboardButton(
      text="Отклонить ❌",
      callback_data=f"reject meme:{bot_message.message_id}")

    admin_keyboard = types.InlineKeyboardMarkup()

    admin_keyboard.add(add_tags_button)
    admin_keyboard.add(approve_button, reject_button)

    caption = str(message.text) + "\n\n"
    if caption == "<i>None</i>\n\n":
      caption = ""

    from_user = f"<i>Автор мема: {findUserById(user_id)['last_name']} {findUserById(user_id)['first_name'][0]}.</i>"

    bot_message = await bot.send_message(chat_id=groups['admin'],
                                         text=caption + from_user,
                                         parse_mode="HTML",
                                         reply_markup=admin_keyboard)

    memes[bot_message.message_id] = bot_message

    bot_message = await bot.send_message(
      chat_id=chat_id,
      text='Сообщение отправлено!',
      reply_markup=keyboardRegroup(back_button))

    message_ids[chat_id] = [bot_message.message_id]


if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)
