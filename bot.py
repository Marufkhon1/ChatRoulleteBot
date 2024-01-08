import sys
sys.path.append("C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot")



import telebot
from telebot import types 
import logging
from config import TOKEN_BOT
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from datasystem.database import *

logging.basicConfig(filename='C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot\\signals\\bot.log', level=logging.INFO)

bot = telebot.TeleBot(TOKEN_BOT)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        markup = create_gender_keyboard()
        bot.send_message(message.chat.id, 'Привет!\n\nЯ помогу тебе найти друзей или просто пообщаться со случайными людьми.')
        bot.send_message(message.chat.id, '📝 Регистрация\n👣 Шаг 1 из 3\n\nВыбери ниже, какого ты пола?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Твой профиль уже создан.',reply_markup=create_main_keyboard())


def create_gender_keyboard():
    keyboard = InlineKeyboardMarkup()
    male_button = InlineKeyboardButton('Мужской', callback_data='gender_male_create')
    female_button = InlineKeyboardButton('Женский', callback_data='gender_female_create')
    # Add other buttons or customization for creating a new gender
    keyboard.add(male_button, female_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('gender_'))
def handle_gender_selection(call):
    user_id = call.from_user.id
    gender = call.data.split('_')[1]

    # Save gender to the database
    save_user_gender(user_id, gender)

    bot.send_message(call.message.chat.id, '📝 Регистрация\n👣 Шаг 2 из 3\n\nВыбери ниже, что тебе интересно?', reply_markup=create_interests_keyboard())


def create_interests_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    chat_button = types.InlineKeyboardButton('Общение', callback_data='interest_chat')
    intimate_button = types.InlineKeyboardButton('Интим 18+', callback_data='interest_intimate')
    keyboard.add(chat_button, intimate_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('interest_'))
def handle_interest_selection(call):
    user_id = call.from_user.id
    interest = call.data.split('_')[1]
    # Save interest to the database
    save_user_interest(user_id, interest)
    bot.send_message(call.message.chat.id, '📝 Регистрация\n👣 Шаг 3 из 3\n\nНапиши, сколько тебе лет? (от 10 до 99)')


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_age(message):
    user_id = message.from_user.id
    age = int(message.text)
    # Save age to the database
    markup = create_main_keyboard()
    save_user_age(user_id, age)
    bot.send_message(message.chat.id, '✅ Регистрация успешно завершена. Профиль создан.', reply_markup=markup)


def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton('👤 Профиль')
    find_partner_button = types.KeyboardButton('Найти собеседника 🔎')
    keyboard.add(profile_button, find_partner_button)
    return keyboard


@bot.message_handler(commands=['menu'])
def show_menu(message):
    markup = create_main_keyboard()
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def handle_profile(message):
    user_id = message.from_user.id
    profile_data = get_user_profile(user_id)
    if profile_data:
        profile_text = f"👤 Профиль\n\n#️⃣ ID — {user_id}\n👫 Пол — {profile_data['gender']}\n🔞 Возраст — {profile_data['age']}\n🚪 Комната - {profile_data['interest']}"
        bot.send_message(message.chat.id, profile_text, reply_markup=create_profile_keyboard())
    else:
        bot.send_message(message.chat.id, 'Профиль не найден. Пожалуйста, пройдите регистрацию.')

def create_profile_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    change_age_button = types.InlineKeyboardButton('Изменить возраст', callback_data='change_age')
    keyboard.add(change_age_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_'))
def handle_change_profile(call):
    user_id = call.from_user.id
    action = call.data.split('_')[1]
    if action == 'age':
        bot.send_message(call.message.chat.id, 'Напиши новый возраст:')
        bot.register_next_step_handler(call.message, process_new_age)

def process_new_age(message):
    user_id = message.from_user.id
    new_age = int(message.text)
    # Update the age in the database
    update_user_age(user_id, new_age)
    bot.send_message(message.chat.id, 'Возраст успешно изменен.')


@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    chat_info = get_active_chat(user_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('👤 Профиль')
    item2 = types.KeyboardButton('Найти собеседника 🔎')
    markup.add(item1, item2)

    if chat_info:
        # User is in an active chat
        delete_chat(chat_info[0])  # Delete the chat information, not the user
        bot.send_message(chat_info[1], '❌ Собеседник покинул чат', reply_markup=markup)
        bot.send_message(user_id, '❌ Вы вышли из чата. Оцените вашего собеседника:', reply_markup=create_reaction_inline_keyboard())
    else:
        # User is not in an active chat
        bot.send_message(user_id, '❌ Вы не начали чат', reply_markup=markup)


def create_reaction_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    like_button = types.InlineKeyboardButton('👍', callback_data='like')
    dislike_button = types.InlineKeyboardButton('👎', callback_data='dislike')
    heart_button = types.InlineKeyboardButton('♥️', callback_data='heart')
    fire_button = types.InlineKeyboardButton('🔥', callback_data='fire')
    ok_button = types.InlineKeyboardButton('👌', callback_data='ok')
    cancel_button = types.InlineKeyboardButton('🚫', callback_data='cancel')
    keyboard.row(like_button, dislike_button, heart_button)
    keyboard.row(fire_button, ok_button, cancel_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data in ['like', 'dislike', 'heart', 'fire', 'ok', 'cancel'])
def handle_reaction_callback(call):
    user_id = call.from_user.id
    reaction = call.data

    # Save the reaction in the database
    save_user_reaction(user_id, reaction)

    bot.send_message(user_id, f'Ваша оценка сохранена: {reaction}',reply_markup=create_main_keyboard())

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Найти собеседника 🔎':
            handle_find_partner(message)
        elif message.text == '❌ Остановить поиск':
            handle_stop_search(message)
        else:
            handle_chat_message(message)


def handle_find_partner(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('❌ Остановить поиск')
    markup.add(item1)

    chat_two = get_chat()

    if create_chat(message.chat.id, chat_two) is False:
        user_id = message.from_user.id
        handle_user_profile(user_id)

        bot.send_message(message.chat.id, 'Найти собеседника 🔎', reply_markup=markup)
    else:
        mess = 'Собеседник найден. Чтобы остановиться, напишите /stop'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('/stop')
        markup.add(item1)

        bot.send_message(message.chat.id, mess, reply_markup=markup)
        bot.send_message(chat_two, mess, reply_markup=markup)

def handle_user_profile(user_id):
    user_profile = get_user_profile(user_id)
    if user_profile is not None:
        gender = user_profile['gender']
        age = user_profile['age']
        interest = user_profile['interest']
    else:
        # Set default values if user profile not found
        gender = '🙎‍♂Парень'
        age = 25
        interest = 'Общение'

    add_user(user_id, gender, age, interest)

def handle_stop_search(message):
    bot.send_message(message.chat.id, '❌ Поиск остановлен. Напишите /menu')

def handle_chat_message(message):
    chat_info = get_active_chat(message.chat.id)
    bot.send_message(chat_info[1], message.text)

print("==========================================")
print('                                         ')
print('Telegram bot is working without any errors')
print('                                         ')
print("==========================================")


if __name__ == "__main__":
    logging.info("Bot is starting.")
    bot.polling()