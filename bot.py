import sys
sys.path.append("C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot")



import telebot
from telebot import types 
import logging
from config import TOKEN_BOT,help_of_bot,rules_of_bot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from datasystem.database import *

logging.basicConfig(filename='C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot\\signals\\bot.log', level=logging.INFO)

bot = telebot.TeleBot(TOKEN_BOT)

CHANNEL_ID = -1002044984398

def user_subscribed_channel(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print("Error checking channel subscription:", e)
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        markup = create_gender_keyboard()
        bot.send_message(message.chat.id, 'Привет!\n\nЯ помогу тебе найти друзей или просто пообщаться со случайными людьми.')
        bot.send_message(message.chat.id, '📝 Регистрация\n👣 Шаг 1 из 3\n\nВыбери ниже, какого ты пола?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, '✅Твой профиль уже создан.',reply_markup=create_main_keyboard())

@bot.message_handler(commands=['search'])
def handle_search_command(message):
    handle_find_partner(message)

@bot.message_handler(commands=['rules'])
def rules(message):    
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return
    else:
        bot.send_message(message.chat.id, rules_of_bot , reply_markup=create_main_keyboard())

@bot.message_handler(commands=['help'])
def help(message):    
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return
    else:
        bot.send_message(message.chat.id, help_of_bot , reply_markup=create_main_keyboard())


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

    if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return

    else:
        if user_exists(user_id):
            bot.send_message(message.chat.id, '❌ Неверное сообщение. Пожалуйста, следуйте процедуре регистрации или используйте действительные команды.',reply_markup=create_main_keyboard())
            return
    
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
    bot.send_message(message.chat.id, '✏️Выберите действие:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def handle_profile(message):
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
        continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
        markup.add(subscribe_button, continue_button)
        bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
        return
    else:
        profile_data = get_user_profile(user_id)
        if profile_data:
            # Fetch reactions data
            reactions_data = get_user_reactions(user_id)
            
            # Create profile text
            profile_text = f"👤 Профиль\n\n#️⃣ ID — {user_id}\n👫 Пол — {profile_data['gender']}\n🔞 Возраст — {profile_data['age']}\n🚪 Комната - {profile_data['interest']}"
            
            # Add reactions data to profile text
            if reactions_data:
                profile_text += "\n\n👍: {}  👎: {}  ♥️: {}  🔥: {}  👌: {}  🚫: {}".format(
                    reactions_data.get('👍', 0),
                    reactions_data.get('👎', 0),
                    reactions_data.get('♥️', 0),
                    reactions_data.get('🔥', 0),
                    reactions_data.get('👌', 0),
                    reactions_data.get('🚫', 0)
                )

            bot.send_message(message.chat.id, profile_text, reply_markup=create_profile_keyboard())
        else:
            bot.send_message(message.chat.id, 'Профиль не найден. Пожалуйста, пройдите регистрацию.')


@bot.message_handler(commands=['profile'])
def profile(message):
    handle_profile(message)

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
    try:
        new_age = int(message.text)
        # Update the age in the database
        update_user_age(user_id, new_age)
        bot.send_message(message.chat.id, '✅ Возраст успешно изменен.',reply_markup=create_main_keyboard())
    except ValueError:
        bot.send_message(message.chat.id, '❌ Неверный формат возраста. Пожалуйста, введите число.')


 

left_user_id = None

@bot.message_handler(commands=['stop'])
def stop(message):
    global left_user_id
    
    user_id = message.chat.id
    chat_info = get_active_chat(user_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('👤 Профиль')
    item2 = types.KeyboardButton('Найти собеседника 🔎')
    markup.add(item1, item2)

    if not user_subscribed_channel(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)  
        subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
        continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
        markup.add(subscribe_button, continue_button)
        bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
        return
    else:
        if chat_info:
            if left_user_id is None:
                # Store the user ID of the person who initiated the stop command
                left_user_id = user_id  
                bot.send_message(user_id, '✋ Подождите, пока ваш собеседник завершит чат.')
            else:
                # Both users are present, initiate the reaction process
                delete_chat(chat_info[0]) 
                bot.send_message(chat_info[1], '❌ Собеседник покинул чат', reply_markup=markup)
                bot.send_message(user_id, '❌ Вы вышли из чата', reply_markup=markup)
                # Ask for reaction
                reaction_markup = types.InlineKeyboardMarkup(row_width=3)
                item1 = types.InlineKeyboardButton('👍', callback_data='reaction_👍')
                item2 = types.InlineKeyboardButton('👎', callback_data='reaction_👎')
                item3 = types.InlineKeyboardButton('♥️', callback_data='reaction_♥️')
                item4 = types.InlineKeyboardButton('🔥', callback_data='reaction_🔥')
                item5 = types.InlineKeyboardButton('👌', callback_data='reaction_👌')
                item6 = types.InlineKeyboardButton('🚫', callback_data='reaction_🚫')
                reaction_markup.add(item1, item2, item3, item4, item5, item6)

                bot.send_message(chat_info[1], 'Пожалуйста, реагируйте на действия собеседника смайлами ✨:', reply_markup=reaction_markup)
        else:
            bot.send_message(user_id, '❌ Вы не начали чат', reply_markup=markup)


# Define a dictionary to keep track of reactions that have been saved during the current session
saved_reactions = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('reaction_'))
def handle_reaction(call):
    global left_user_id
    global saved_reactions
    
    reaction = call.data.split('_')[1]  # Extract the reaction from the callback data
    
    if left_user_id is None:
        # Handle the case where left_user_id is not set (unexpected behavior)
        bot.answer_callback_query(call.id, "Error: left_user_id not set")
        return
    
    if left_user_id in saved_reactions:
        # If the reaction has already been saved for this user, send a message indicating so
        bot.answer_callback_query(call.id, "You have already saved a reaction")
    else:
        # Save the reaction into the database associated with the user who left
        save_reaction(left_user_id, reaction)
        saved_reactions[left_user_id] = reaction  # Mark the reaction as saved for this user
        
        # Send a message confirming the reaction and sending the menu
        bot.send_message(call.message.chat.id, "Your reaction has been saved to your partner's database.")
        create_main_keyboard()

@bot.message_handler(content_types=['text'])
def bot_message(message):
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return
    else:
        if message.chat.type == 'private':
            if message.text == 'Найти собеседника 🔎':
                handle_find_partner(message)
            elif message.text == '❌ Остановить поиск':
                handle_stop_search(message)
            else:
                handle_chat_message(message)



searching_users = []


@bot.message_handler(func=lambda message: message.text == 'Найти собеседника 🔎')
def handle_find_partner(message):
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return
    else:
        global searching_users
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('❌ Остановить поиск')
        markup.add(item1)

        searching_users.append(message.from_user.id)

        def send_waiting_message():
            if len(searching_users) == 1:
                bot.send_message(message.chat.id, 'Ожидаем собеседника...', reply_markup=markup)

        if len(searching_users) >= 2:
            chat_two = searching_users.pop(0)
            chat_one = searching_users.pop(0)

            if create_chat(chat_one, chat_two):
                mess = 'Собеседник найден. Чтобы остановиться, напишите /stop'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton('/stop')
                markup.add(item1)
                bot.send_message(chat_one, mess, reply_markup=markup)
                bot.send_message(chat_two, mess, reply_markup=markup)
            else:
                bot.send_message(chat_one, 'Произошла ошибка при создании чата. Попробуйте еще раз.')
                bot.send_message(chat_two, 'Произошла ошибка при создании чата. Попробуйте еще раз.')
                searching_users.append(chat_one)
                searching_users.append(chat_two)
        else:
            send_waiting_message() 

def handle_stop_search(message):
    global searching_users
    
    # Remove the user from the list of searching users
    if message.from_user.id in searching_users:
        searching_users.remove(message.from_user.id)
    bot.send_message(message.chat.id, '❌ Поиск остановлен.',reply_markup=create_main_keyboard())

def handle_chat_message(message):
    user_id = message.from_user.id
    chat_info = get_active_chat(message.chat.id)
    
    # Check if chat_info is not False (indicating chat is active)
    if chat_info:
        bot.send_message(chat_info[1], message.text)
    else:

        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton("Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz")
            continue_button = types.InlineKeyboardButton("Продолжить", callback_data="continue_registration")
            markup.add(subscribe_button, continue_button)
            bot.send_message(message.chat.id, '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".', reply_markup=markup)
            return
        
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('👤 Профиль')
            item2 = types.KeyboardButton('Найти собеседника 🔎')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, "❌ Неверное сообщение. Пожалуйста, следуйте процедуре регистрации или используйте действительные команды.",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('continue_registration'))
def after_subscribing(call):
    user_id = call.message.chat.id
    if user_subscribed_channel(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('👤 Профиль')
        item2 = types.KeyboardButton('Найти собеседника 🔎')
        markup.add(item1, item2)
        bot.send_message(user_id, '✅ Вы успешно подписаны', reply_markup=markup)
    else:
        # User did not follow and press continue registration
        bot.send_message(user_id, '❌ Пожалуйста, подпишитесь на наши каналы перед продолжением.')


print("==========================================")
print('                                         ')
print('Telegram bot is working without any errors')
print('                                         ')
print("==========================================")


if __name__ == "__main__":
    logging.info("Bot is starting.")
    bot.polling()