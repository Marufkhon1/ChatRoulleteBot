import sys

sys.path.append("C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot")


import telebot
from telebot import types
import logging
from config import TOKEN_BOT, help_of_bot, rules_of_bot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import time

from datasystem.database import *

logging.basicConfig(
    filename="C:\\Users\\mmman\\OneDrive\\Рабочий стол\\ChatTelebot\\signals\\bot.log",
    level=logging.INFO,
)

bot = telebot.TeleBot(TOKEN_BOT)

CHANNEL_ID = -1002044984398


def user_subscribed_channel(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Error checking channel subscription:", e)
        return False


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        markup = create_gender_keyboard()
        bot.send_message(
            message.chat.id,
            "Привет!\n\nДобро пожаловать в нашего бота! Я здесь, чтобы помочь тебе расширить круг общения и найти новых друзей или просто пообщаться со случайными людьми.",
        )

        bot.send_message(
            message.chat.id,
            "📝 Регистрация\n👣 Шаг 1 из 3\n\nВыбери ниже, какого ты пола?",
            reply_markup=markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            "✅Твой профиль уже создан.",
            reply_markup=create_main_keyboard(),
        )


@bot.message_handler(commands=["search"])
def handle_search_command(message):
    handle_find_partner(message)


@bot.message_handler(commands=["rules"])
def rules(message):
    user_id = message.from_user.id
    if user_exists(user_id):

        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(
                row_width=1
            )  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton(
                "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
            )
            continue_button = types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_registration"
            )
            markup.add(subscribe_button, continue_button)
            bot.send_message(
                message.chat.id,
                '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
                reply_markup=markup,
            )
            return
        else:
            bot.send_message(
                message.chat.id, rules_of_bot, reply_markup=create_main_keyboard()
            )
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


@bot.message_handler(commands=["help"])
def help(message):
    user_id = message.from_user.id
    if user_exists(user_id):
        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(
                row_width=1
            )  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton(
                "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
            )
            continue_button = types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_registration"
            )
            markup.add(subscribe_button, continue_button)
            bot.send_message(
                message.chat.id,
                '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
                reply_markup=markup,
            )
            return
        else:
            bot.send_message(
                message.chat.id, help_of_bot, reply_markup=create_main_keyboard()
            )
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


def create_gender_keyboard():
    keyboard = InlineKeyboardMarkup()
    male_button = InlineKeyboardButton("👨 Мужской", callback_data="gender_male_create")
    female_button = InlineKeyboardButton(
        "👩 Женский", callback_data="gender_female_create"
    )
    # Add other buttons or customization for creating a new gender
    keyboard.add(male_button, female_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("gender_"))
def handle_gender_selection(call):
    user_id = call.from_user.id
    gender = call.data.split("_")[1]
    if not user_exists(user_id):
        save_user_gender(user_id, gender)
        bot.delete_message(
            call.message.chat.id, call.message.message_id
        )  # Delete the message after button press
        bot.send_message(
            call.message.chat.id,
            "📝 Регистрация\n👣 Шаг 2 из 3\n\nВыбери ниже, что тебе интересно?",
            reply_markup=create_interests_keyboard(),
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


def create_interests_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    chat_button = types.InlineKeyboardButton("Общение", callback_data="interest_chat")
    intimate_button = types.InlineKeyboardButton(
        "Другое", callback_data="interest_other"
    )
    keyboard.add(chat_button, intimate_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("interest_"))
def handle_interest_selection(call):
    user_id = call.from_user.id
    interest = call.data.split("_")[1]
    # Save interest to the database
    if (
        user_exists(user_id)
        and get_user_gender(user_id) is not None
        and get_user_interest(user_id) is None
    ):
        save_user_interest(user_id, interest)
        bot.delete_message(
            call.message.chat.id, call.message.message_id
        )  # Delete the message after button press
        bot.send_message(
            call.message.chat.id,
            "📝 Регистрация\n👣 Шаг 3 из 3\n\nНапиши, сколько тебе лет? (от 10 до 99)",
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "❌ Неверное сообщение. Пожалуйста, следуйте процедуре регистрации или используйте действительные команды.",
            reply_markup=create_main_keyboard(),
        )


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_age(message):
    user_id = message.from_user.id
    age = int(message.text)

    if user_exists(user_id) and get_user_gender(user_id) is not None:
        if get_user_age(user_id) is None:
            markup = create_main_keyboard()
            save_user_age(user_id, age)
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(
                message.chat.id,
                "✅ Регистрация успешно завершена. Профиль создан.",
                reply_markup=markup,
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Неверное сообщение. Пожалуйста, следуйте процедуре регистрации или используйте действительные команды.",
                reply_markup=create_main_keyboard(),
            )
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton("👤 Профиль")
    find_partner_button = types.KeyboardButton("Найти собеседника 🔎")
    keyboard.add(profile_button, find_partner_button)
    return keyboard


@bot.message_handler(commands=["menu"])
def show_menu(message):
    markup = create_main_keyboard()
    bot.send_message(message.chat.id, "✏️Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "👤 Профиль")
def handle_profile(message):
    user_id = message.from_user.id
    if not user_subscribed_channel(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        subscribe_button = types.InlineKeyboardButton(
            "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
        )
        continue_button = types.InlineKeyboardButton(
            "Продолжить", callback_data="continue_registration"
        )
        markup.add(subscribe_button, continue_button)
        bot.send_message(
            message.chat.id,
            '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
            reply_markup=markup,
        )
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
                profile_text += "\n\n👍 {}  👎 {}  ♥️ {}  🔥 {}  👌 {}  🚫 {}".format(
                    reactions_data.get("👍", 0),
                    reactions_data.get("👎", 0),
                    reactions_data.get("♥️", 0),
                    reactions_data.get("🔥", 0),
                    reactions_data.get("👌", 0),
                    reactions_data.get("🚫", 0),
                )
            else:
                profile_text += "\n\n 👍 0 👎 0  ♥️  0 🔥 0 👌 0 🚫 0"

            bot.send_message(
                message.chat.id, profile_text, reply_markup=create_profile_keyboard()
            )
        else:
            bot.send_message(
                message.chat.id,
                "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
            )


@bot.message_handler(commands=["profile"])
def profile(message):
    handle_profile(message)


def create_profile_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    change_age_button = types.InlineKeyboardButton(
        "✏️ Изменить возраст", callback_data="change_age"
    )
    keyboard.add(change_age_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_"))
def handle_change_profile(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    if user_exists(user_id):

        if action == "age":
            bot.send_message(call.message.chat.id, "Напиши новый возраст:")
            bot.register_next_step_handler(call.message, process_new_age)
    else:
        bot.send_message(
            call.message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


def process_new_age(message):
    user_id = message.from_user.id
    try:
        new_age = int(message.text)
        # Update the age in the database
        update_user_age(user_id, new_age)
        bot.send_message(
            message.chat.id,
            "✅ Возраст успешно изменен.",
            reply_markup=create_main_keyboard(),
        )
    except ValueError:
        bot.send_message(
            message.chat.id, "❌ Неверный формат возраста. Пожалуйста, введите число."
        )


left_user_id = None


def get_active_chat_active(chat_id):
    """
    Get the user IDs of both users in the active chat for the provided chat ID.

    Args:
    - chat_id (int): The chat ID for which to retrieve the active chat.

    Returns:
    - tuple or None: A tuple containing user IDs of both users in the active chat, or None if no active chat is found.
    """
    for user_id, active_chat_id in active_chats.items():
        if active_chat_id == chat_id:
            # Return user IDs of both users involved in the active chat
            return (user_id, active_chats[user_id])
    return None


def delete_chat_active(chat_id):
    """
    Delete the active chat associated with the given chat ID from the active_chats dictionary.

    Args:
    - chat_id (int): The chat ID to be deleted.

    Returns:
    - bool: True if the active chat was successfully deleted, False otherwise.
    """
    for user_id, active_chat_id in active_chats.items():
        if active_chat_id == chat_id:
            # Remove both entries (user ID to chat ID and chat ID to user ID)
            del active_chats[user_id]
            del active_chats[chat_id]
            return True
    return False


left_user_id = None
stop_requests = []


@bot.message_handler(commands=["stop"])
def stop(message):
    global left_user_id

    user_id = message.chat.id
    chat_info = get_active_chat_active(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("👤 Профиль")
    item2 = types.KeyboardButton("Найти собеседника 🔎")
    markup.add(item1, item2)

    if user_exists(user_id):
        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(
                "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
            )
            continue_button = types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_registration"
            )
            markup.add(subscribe_button, continue_button)
            bot.send_message(
                message.chat.id,
                '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
                reply_markup=markup,
            )
            return
        else:
            # Store the user ID who pressed /stop first
            stop_requests.append(user_id)

            if chat_info:
                if left_user_id is None:
                    left_user_id = user_id
                    bot.send_message(
                        user_id, "✋ Подождите, пока ваш собеседник завершит чат."
                    )
                else:
                    delete_chat_active(chat_info[0])
                    bot.send_message(
                        chat_info[0], "❌ Собеседник покинул чат", reply_markup=markup
                    )
                    bot.send_message(
                        user_id, "❌ Вы вышли из чата", reply_markup=markup
                    )
                    reaction_markup = types.InlineKeyboardMarkup(row_width=3)
                    item1 = types.InlineKeyboardButton(
                        "👍", callback_data="reaction_👍"
                    )
                    item2 = types.InlineKeyboardButton(
                        "👎", callback_data="reaction_👎"
                    )
                    item3 = types.InlineKeyboardButton("♥️", callback_data="reaction_♥️")
                    item4 = types.InlineKeyboardButton(
                        "🔥", callback_data="reaction_🔥"
                    )
                    item5 = types.InlineKeyboardButton(
                        "👌", callback_data="reaction_👌"
                    )
                    item6 = types.InlineKeyboardButton(
                        "🚫", callback_data="reaction_🚫"
                    )
                    reaction_markup.add(item1, item2, item3, item4, item5, item6)
                    bot.send_message(
                        chat_info[0],
                        "🖋️Пожалуйста, реагируйте на действия собеседника смайлами ✨:",
                        reply_markup=reaction_markup,
                    )
            else:
                bot.send_message(user_id, "❌ Вы не начали чат", reply_markup=markup)
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


saved_reactions = {}


@bot.callback_query_handler(func=lambda call: call.data.startswith("reaction_"))
def handle_reaction(call):
    global left_user_id
    global saved_reactions

    reaction = call.data.split("_")[1]  # Extract the reaction from the callback data

    if left_user_id is None:
        # Handle the case where left_user_id is not set (unexpected behavior)
        bot.answer_callback_query(call.id, "❌ Вы не начали чат")
        return

    if left_user_id in saved_reactions:
        # If the user has already saved a reaction
        bot.answer_callback_query(call.id, "✅ Вы уже сохранили реакцию")
    else:
        # Save the reaction into the database associated with the user who left
        save_reaction(left_user_id, reaction)
        saved_reactions[left_user_id] = (
            reaction  # Mark the reaction as saved for this user
        )

        # Send a message confirming the reaction
        bot.send_message(call.message.chat.id, "✅ Ваша реакция сохранена.")

        # Delete the reaction keyboard
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )

        # Optionally, you can create and send the main keyboard here
        create_main_keyboard()  # Assuming this function creates and sends the main keyboard

        # Clear saved reaction after sending the menu
        saved_reactions.pop(left_user_id, None)


@bot.message_handler(content_types=["text"])
def bot_message(message):
    user_id = message.from_user.id
    if user_exists(user_id):
        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(
                row_width=1
            )  # Set row_width to 1 for a vertical layout
            subscribe_button = types.InlineKeyboardButton(
                "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
            )
            continue_button = types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_registration"
            )
            markup.add(subscribe_button, continue_button)
            bot.send_message(
                message.chat.id,
                '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
                reply_markup=markup,
            )
            return
        else:
            if message.chat.type == "private":
                if message.text == "Найти собеседника 🔎":
                    handle_find_partner(message)
                elif message.text == "❌ Остановить поиск":
                    handle_stop_search(message)
                else:
                    handle_chat_message(message)
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


active_chats = {}
searching_users = []


@bot.message_handler(func=lambda message: message.text == "Найти собеседника 🔎")
def handle_find_partner(message):
    user_id = message.from_user.id
    if user_exists(user_id):
        if not user_subscribed_channel(user_id):
            markup = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(
                "Подпишитесь на наш канал", url="https://t.me/chatroulletebotuz"
            )
            continue_button = types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_registration"
            )
            markup.add(subscribe_button, continue_button)
            bot.send_message(
                message.chat.id,
                '😔 Вы еще не подписаны на наши каналы! Подпишитесь и нажмите кнопку "Продолжить".',
                reply_markup=markup,
            )
            return
        else:
            global searching_users
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("❌ Остановить поиск")
            markup.add(item1)
            searching_users.append(user_id)

            if len(searching_users) >= 2:
                chat_two = searching_users.pop(0)
                chat_one = searching_users.pop(0)

                # Ensure users don't chat with themselves
                if chat_one != chat_two:
                    # Fetch reactions data for both users
                    chat_one_reactions = get_user_reactions(chat_one)
                    chat_two_reactions = get_user_reactions(chat_two)

                    # Create a new chat
                    active_chats[chat_one] = chat_two
                    active_chats[chat_two] = chat_one

                    thumbs_up = chat_two_reactions.get('👍', 0)
                    thumbs_down = chat_two_reactions.get('👎', 0)
                    fire = chat_two_reactions.get('🔥', 0)
                    heart = chat_two_reactions.get('♥️',0)
                    good = chat_two_reactions.get('👌',0)
                    spam = chat_two_reactions.get('🚫',0)

                    thumbs_up_2 = chat_one_reactions.get('👍', 0)
                    thumbs_down_2 = chat_one_reactions.get('👎', 0)
                    fire_2 = chat_one_reactions.get('🔥', 0)
                    heart_2 = chat_one_reactions.get('♥️',0)
                    good_2 = chat_one_reactions.get('👌',0)
                    spam_2 = chat_one_reactions.get('🚫',0)

                    mess_chat_one = f"Собеседник найден. Чтобы остановиться, напишите /stop\n\n 👍 {thumbs_up}  👎 {thumbs_down}  🔥 {fire}  ♥️ {heart}  👌 {good}  🚫 {spam}"
                    markup_chat_one = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1_chat_one = types.KeyboardButton("/stop")
                    markup_chat_one.add(item1_chat_one)
                    bot.send_message(chat_one, mess_chat_one, reply_markup=markup_chat_one)

                    mess_chat_two = f"Собеседник найден. Чтобы остановиться, напишите /stop \n\n 👍 {thumbs_up_2}  👎 {thumbs_down_2}  🔥 {fire_2}  ♥️ {heart_2}  👌 {good_2}  🚫 {spam_2}"
                    markup_chat_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1_chat_two = types.KeyboardButton("/stop")
                    markup_chat_two.add(item1_chat_two)
                    bot.send_message(chat_two, mess_chat_two, reply_markup=markup_chat_two)
                else:
                    searching_users.append(chat_one)  # Put the user back in the queue
                    bot.send_message(
                        chat_one,
                        "Вы не можете общаться сами с собой. Ожидаем другого собеседника...",
                        reply_markup=markup,
                    )
            else:
                bot.send_message(
                    message.chat.id, "Ожидаем собеседника...", reply_markup=markup
                )
    else:
        bot.send_message(
            message.chat.id,
            "Профиль не найден. Пожалуйста, пройдите регистрацию./start",
        )


def handle_stop_search(message):
    global searching_users
    if message.from_user.id in searching_users:
        searching_users.remove(message.from_user.id)
    bot.send_message(
        message.chat.id, "❌ Поиск остановлен.", reply_markup=create_main_keyboard()
    )


def handle_chat_message(message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            # Attempt to send the message to the partner
            bot.send_message(partner_id, message.text)
        except Exception as e:
            logging.error(f"Error sending message to user {partner_id}: {e}")
            bot.send_message(
                user_id,
                "При отправке сообщения произошла ошибка. Пожалуйста, повторите попытку позже.",
            )
    else:
        bot.send_message(
            user_id,
            "❌ Неверное сообщение. Пожалуйста, следуйте процедуре регистрации или используйте действительные команды.",
            reply_markup=create_main_keyboard(),
        )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("continue_registration")
)
def after_subscribing(call):
    user_id = call.message.chat.id
    if user_subscribed_channel(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("👤 Профиль")
        item2 = types.KeyboardButton("Найти собеседника 🔎")
        markup.add(item1, item2)
        bot.send_message(user_id, "✅ Вы успешно подписаны", reply_markup=markup)
    else:
        # User did not follow and press continue registration
        bot.send_message(
            user_id, "❌ Пожалуйста, подпишитесь на наши каналы перед продолжением."
        )


print("==========================================")
print("                                         ")
print("Telegram bot is working without any errors")
print("                                         ")
print("==========================================")


if __name__ == "__main__":
    logging.info("Bot is starting.")
    bot.polling()
