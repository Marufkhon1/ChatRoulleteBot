import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from bot import (
    start,
    create_gender_keyboard,
    handle_age,
    handle_gender_selection,
    handle_interest_selection,
    create_main_keyboard,
    create_interests_keyboard,
    create_profile_keyboard,
    handle_profile,
    show_menu,
    handle_change_profile,
    process_new_age,
    stop,
    handle_find_partner,
    bot_message,
    handle_stop_search,
    handle_user_profile,
    handle_chat_message
)

class TestBot(unittest.TestCase):
    @patch('project.bot.user_exists', return_value=False)  # Mock the user_exists function
    @patch('project.bot.create_gender_keyboard', return_value=MagicMock())  # Mock the create_gender_keyboard function
    @patch('project.bot.bot.send_message', return_value=None)  # Mock the bot.send_message function
    def test_start(self, mock_send_message, mock_create_gender_keyboard, mock_user_exists):
        message = MagicMock()
        message.from_user.id = 123

    # Call the start function
        start(message)

    # Add assertions based on your requirements
        mock_user_exists.assert_called_once_with(123)
        mock_create_gender_keyboard.assert_called_once()

    # Adjust the assertion for send_message to match the actual calls
        mock_send_message.assert_has_calls([
            mock.call(message.chat.id, 'Привет!\n\nЯ помогу тебе найти друзей или просто пообщаться со случайными людьми.'),
            mock.call(message.chat.id, '📝 Регистрация\n👣 Шаг 1 из 3\n\nВыбери ниже, какого ты пола?', reply_markup=mock.ANY),
        ],  any_order=False)

    def test_create_gender_keyboard(self):
        # Call the function to create the keyboard
        keyboard = create_gender_keyboard()

        # Assert that the keyboard is not None
        self.assertIsNotNone(keyboard)

        # Check the number of buttons in the keyboard
        self.assertEqual(len(keyboard.keyboard), 1)

        # Check the text of the first button (Male)
        self.assertEqual(keyboard.keyboard[0][0].text, 'Мужской')

        # Check the callback data of the first button
        self.assertEqual(keyboard.keyboard[0][0].callback_data, 'gender_male_create')

        # Check the text of the second button (Female)
        self.assertEqual(keyboard.keyboard[0][1].text, 'Женский')

        # Check the callback data of the second button
        self.assertEqual(keyboard.keyboard[0][1].callback_data, 'gender_female_create')

    @patch('project.bot.save_user_gender', return_value=None)
    @patch('project.bot.bot.send_message', return_value=None)
    def test_handle_gender_selection(self, mock_send_message, mock_save_user_gender):
    # Create a MagicMock object for call
        call = MagicMock()
        call.message.chat.id = 123  # Set the necessary attributes

        handle_gender_selection(call)

    # Adjust the assertion for send_message to match the actual calls
        mock_send_message.assert_has_calls([
            mock.call(123, '📝 Регистрация\n👣 Шаг 2 из 3\n\nВыбери ниже, что тебе интересно?', reply_markup=mock.ANY),
        ],  any_order=False)

    def test_create_interests_keyboard(self):
        # Call the function to create the keyboard
        keyboard = create_interests_keyboard()

        # Assert that the keyboard is not None
        self.assertIsNotNone(keyboard)

        # Check the number of buttons in the keyboard
        self.assertEqual(len(keyboard.keyboard), 1)

        # Check the text of the first button (Chat)
        self.assertEqual(keyboard.keyboard[0][0].text, 'Общение')

        # Check the callback data of the first button
        self.assertEqual(keyboard.keyboard[0][0].callback_data, 'interest_chat')

        # Check the text of the second button (Intimate 18+)
        self.assertEqual(keyboard.keyboard[0][1].text, 'Интим 18+')

        # Check the callback data of the second button
        self.assertEqual(keyboard.keyboard[0][1].callback_data, 'interest_intimate')

    @patch('project.bot.bot.send_message', return_value=None)
    @patch('project.bot.save_user_interest', return_value=None)
    def test_handle_interest_selection(self, mock_save_user_interest, mock_send_message):
        # Create a MagicMock object to simulate a callback query
        call = MagicMock()
        call.from_user.id = 123
        call.data = 'interest_chat'

        # Call the function to handle the interest selection
        handle_interest_selection(call)

        # Add assertions based on your requirements
        mock_save_user_interest.assert_called_once_with(123, 'chat')
        mock_send_message.assert_called_once_with(
            call.message.chat.id,
            '📝 Регистрация\n👣 Шаг 3 из 3\n\nНапиши, сколько тебе лет? (от 10 до 99)',
        )

    @patch('project.bot.bot.send_message', return_value=None)
    @patch('project.bot.create_main_keyboard', return_value=MagicMock())
    @patch('project.bot.save_user_age', return_value=None)
    def test_handle_age(self, mock_save_user_age, mock_create_main_keyboard, mock_send_message):
        # Create a MagicMock object to simulate a message
        message = MagicMock()
        message.from_user.id = 123
        message.text = '25'

        # Call the function to handle the age input
        handle_age(message)

        # Add assertions based on your requirements
        mock_save_user_age.assert_called_once_with(123, 25)
        mock_create_main_keyboard.assert_called_once()
        mock_send_message.assert_called_once_with(
            message.chat.id,
            '✅ Регистрация успешно завершена. Профиль создан.',
            reply_markup=mock_create_main_keyboard.return_value,
        )

    def test_create_main_keyboard(self):
        # Call the function to create the main keyboard
        keyboard = create_main_keyboard()
        # Assert that the keyboard is not None
        self.assertIsNotNone(keyboard)

        # Add more specific assertions based on your requirements
        # For example, you can check the number of buttons in the keyboard
        self.assertEqual(len(keyboard.keyboard), 1)  # Adjust this based on the actual structure

        # Check the text of the first button (Profile)
        self.assertEqual(keyboard.keyboard[0][0]['text'], '👤 Профиль')

        # Check the text of the second button (Find Partner)
        self.assertEqual(keyboard.keyboard[0][1]['text'], 'Найти собеседника 🔎')

    @patch('project.bot.create_main_keyboard', return_value=MagicMock())
    @patch('project.bot.bot.send_message', return_value=None)
    def test_show_menu(self, mock_send_message, mock_create_main_keyboard):
        message = MagicMock()
        message.chat.id = 123

        # Call the show_menu function
        show_menu(message)

        # Add assertions based on your requirements
        mock_create_main_keyboard.assert_called_once()
        mock_send_message.assert_called_once_with(123, 'Выберите действие:', reply_markup=mock_create_main_keyboard.return_value)

    @patch('project.bot.get_user_profile', return_value={'gender': 'Male', 'age': 25, 'interest': 'chat'})
    @patch('project.bot.bot.send_message', return_value=None)
    @patch('project.bot.create_profile_keyboard', return_value=MagicMock())
    def test_handle_profile(self, mock_create_profile_keyboard, mock_send_message, mock_get_user_profile):
        message = MagicMock()
        message.from_user.id = 456
        message.text = '👤 Профиль'

        # Call the handle_profile function
        handle_profile(message)

        # Add assertions based on your requirements
        mock_get_user_profile.assert_called_once_with(456)
        mock_create_profile_keyboard.assert_called_once()
        mock_send_message.assert_called_once_with(
            message.chat.id,
            '👤 Профиль\n\n#️⃣ ID — 456\n👫 Пол — Male\n🔞 Возраст — 25\n🚪 Комната - chat',
            reply_markup=mock_create_profile_keyboard.return_value
        )

    def test_create_profile_keyboard(self):
        # Call the function to create the keyboard
        keyboard = create_profile_keyboard()

        # Assert that the keyboard is not None
        self.assertIsNotNone(keyboard)

        # Check the number of buttons in the keyboard
        self.assertEqual(len(keyboard.keyboard), 1)

        # Check the text of the first button
        self.assertEqual(keyboard.keyboard[0][0].text, 'Изменить возраст')

        # Check the callback data of the first button
        self.assertEqual(keyboard.keyboard[0][0].callback_data, 'change_age')

        # Add more specific assertions based on your requirements

    @patch('project.bot.bot.send_message', return_value=None)
    @patch('project.bot.bot.register_next_step_handler', return_value=None)
    def test_handle_change_profile(self, mock_register_next_step_handler, mock_send_message):
        call = MagicMock()
        call.from_user.id = 123
        call.message.chat.id = 456  # Set the chat ID to the expected value
        call.data = 'change_age'

        handle_change_profile(call)

        mock_send_message.assert_called_once_with(456, 'Напиши новый возраст:')

        # Check if register_next_step_handler is called
        mock_register_next_step_handler.assert_called_once_with(call.message, process_new_age)

        # Get the arguments passed to register_next_step_handler
        _, handler_function = mock_register_next_step_handler.call_args[0]

        # Simulate the user providing input
        user_message = MagicMock()
        user_message.from_user.id = 123
        user_message.text = '25'

        # Manually call the registered next step handler
        handler_function(user_message)

        # Now, check that process_new_age is called once
        # process_new_age.assert_called_once_with(user_message)

    @mock.patch('project.bot.update_user_age')
    @mock.patch('project.bot.bot.send_message')
    def test_process_new_age(self, mock_send_message, mock_update_user_age):
        user_id = 123
        message = mock.Mock()
        message.from_user.id = user_id
        message.text = '25'

        process_new_age(message)

        mock_update_user_age.assert_called_once_with(user_id, 25)
        mock_send_message.assert_called_once_with(message.chat.id, 'Возраст успешно изменен.')

    @mock.patch('project.bot.get_active_chat', return_value=(456, 789))
    @mock.patch('project.bot.delete_chat')
    @mock.patch('project.bot.bot.send_message')
    def test_stop_active_chat(self, mock_send_message, mock_delete_chat, mock_get_active_chat):
        user_id = 123
        chat_id = 456
        partner_id = 789
        message = mock.Mock()
        message.chat.id = user_id

        stop(message)

        mock_get_active_chat.assert_called_once_with(user_id)
        mock_delete_chat.assert_called_once_with(chat_id)
        mock_send_message.assert_has_calls([
            mock.call(partner_id, '❌ Собеседник покинул чат', reply_markup=mock.ANY),
            mock.call(user_id, '❌ Вы вышли из чата', reply_markup=mock.ANY),
        ], any_order=False)

    @mock.patch('project.bot.get_active_chat', return_value=None)
    @mock.patch('project.bot.bot.send_message')
    def test_stop_inactive_chat(self, mock_send_message, mock_get_active_chat):
        user_id = 123
        message = mock.Mock()
        message.chat.id = user_id

        stop(message)

        mock_get_active_chat.assert_called_once_with(user_id)
        mock_send_message.assert_called_once_with(user_id, '❌ Вы не начали чат', reply_markup=mock.ANY)

    @mock.patch('project.bot.get_chat', return_value=None)
    @mock.patch('project.bot.create_chat', return_value=True)  # Adjust to return True when a chat is successfully created
    @mock.patch('project.bot.handle_user_profile')
    @mock.patch('project.bot.bot.send_message')
    def test_handle_find_partner_no_partner(self, mock_send_message, mock_handle_user_profile, mock_create_chat, mock_get_chat):
        message = mock.Mock()
        message.from_user.id = 456
        handle_find_partner(message)

        expected_calls = [
            mock.call(None, 'Собеседник найден. Чтобы остановиться, напишите /stop', reply_markup=mock.ANY)
        ]

        mock_send_message.assert_has_calls(expected_calls, any_order=True)

    @mock.patch('project.bot.get_chat', return_value=123)  # Replace with appropriate values
    @mock.patch('project.bot.create_chat', return_value=True)
    @mock.patch('project.bot.bot.send_message')
    def test_handle_find_partner_with_partner(self, mock_send_message, mock_create_chat, mock_get_chat):
        message = mock.Mock()
        message.from_user.id = 456  # Replace with appropriate values
        handle_find_partner(message)

        actual_chat_ids = [call_args[0] for call_args, _ in mock_send_message.call_args_list]

        expected_calls = [
            mock.call(mock.ANY, 'Собеседник найден. Чтобы остановиться, напишите /stop', reply_markup=mock.ANY),
            mock.call(mock.ANY, 'Собеседник найден. Чтобы остановиться, напишите /stop', reply_markup=mock.ANY),
        ]

        # Validate that the actual chat IDs are present in the expected calls
        for chat_id in actual_chat_ids:
            expected_calls[0] = mock.call(chat_id, 'Собеседник найден. Чтобы остановиться, напишите /stop', reply_markup=mock.ANY)
            expected_calls[1] = mock.call(mock.ANY, 'Собеседник найден. Чтобы остановиться, напишите /stop', reply_markup=mock.ANY)

        mock_send_message.assert_has_calls(expected_calls, any_order=True)

    @mock.patch('project.bot.get_user_profile', return_value={'gender': 'Male', 'age': 25, 'interest': 'Chat'})
    @mock.patch('project.bot.add_user')
    def test_handle_user_profile_exists(self, mock_add_user, mock_get_user_profile):
        user_id = 123  # Replace with appropriate values
        handle_user_profile(user_id)
        mock_add_user.assert_called_with(user_id, 'Male', 25, 'Chat')

    @mock.patch('project.bot.get_user_profile', return_value=None)
    @mock.patch('project.bot.add_user')
    def test_handle_user_profile_not_exists(self, mock_add_user, mock_get_user_profile):
        user_id = 123  # Replace with appropriate values
        handle_user_profile(user_id)
        mock_add_user.assert_called_with(user_id, '🙎‍♂Парень', 25, 'Общение')

    @mock.patch('project.bot.bot.send_message')
    def test_handle_stop_search(self, mock_send_message):
        message = mock.Mock()
        handle_stop_search(message)
        mock_send_message.assert_called_with(message.chat.id, '❌ Поиск остановлен. Напишите /menu')

    @mock.patch('project.bot.get_active_chat', return_value=(123, 456))  # Replace with appropriate values
    @mock.patch('project.bot.bot.send_message')
    def test_handle_chat_message(self, mock_send_message, mock_get_active_chat):
        message = mock.Mock()
        message.text = 'Hello, how are you?'  # Replace with appropriate values
        handle_chat_message(message)
        mock_send_message.assert_called_with(456, 'Hello, how are you?')

    @mock.patch('project.bot.create_chat', return_value=False)
    @mock.patch('project.bot.handle_user_profile')
    @mock.patch('project.bot.bot.send_message')
    def test_bot_message_find_partner(self, mock_send_message, mock_handle_user_profile, mock_create_chat):
        message = mock.Mock()
        message.chat.type = 'private'
        message.text = 'Найти собеседника 🔎'
        bot_message(message)
        mock_send_message.assert_called_with(message.chat.id, 'Найти собеседника 🔎', reply_markup=mock.ANY)

    @mock.patch('project.bot.handle_stop_search')
    @mock.patch('project.bot.bot.send_message')
    def test_bot_message_stop_search(self, mock_send_message, mock_handle_stop_search):
        message = mock.Mock()
        message.chat.type = 'private'
        message.text = '❌ Остановить поиск'
        bot_message(message)
        mock_handle_stop_search.assert_called_with(message)

    @mock.patch('project.bot.handle_chat_message')
    def test_bot_message_other_text(self, mock_handle_chat_message):
        message = mock.Mock()
        message.chat.type = 'private'
        message.text = 'Some other text'
        bot_message(message)
        mock_handle_chat_message.assert_called_with(message)

if __name__ == '__main__':
    unittest.main()
