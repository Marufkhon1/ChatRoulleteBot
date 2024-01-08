import unittest
from unittest.mock import patch,MagicMock,mock_open
import psycopg2
from datasystem.database import * # Import your add_user function here


mock_cursor = MagicMock()

class TestDatabaseFunctions(unittest.TestCase):
    def test_get_chat(self):
        result = get_chat()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)

    @patch('datasystem.database.psycopg2.connect')
    def test_add_user(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Call the function
        add_user('user123', 'male', 25, 'chat')

        # Assertions
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (user_id, gender, age, interest, last_reaction) VALUES (%s, %s, %s, %s, NULL)",
            ('user123', 'male', 25, 'chat')
        )
        mock_connect.return_value.commit.assert_called_once()

    @patch('datasystem.database.psycopg2.connect')
    def test_user_exists(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Mock the execute method of the cursor
        mock_cursor.fetchone.return_value = (1,)  # User exists

        # Call the function
        result = user_exists('user123')

        # Assertions
        self.assertTrue(result)

    def test_delete_chat(self):
        # Assume there is an existing chat with id 1
        id_chat = 1
        delete_chat(id_chat)
        self.assertFalse(self.chat_exists(id_chat))

    def test_create_chat(self):
        chat_one = 1
        chat_two = 2
        self.assertTrue(create_chat(chat_one, chat_two))

        # Attempt to create a chat with the same chat_one and chat_two
        self.assertFalse(create_chat(chat_one, chat_one))

    def chat_exists(self, id_chat):
        with psycopg2.connect(**DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM chats WHERE id = %s)", (id_chat,))
                result = cursor.fetchone()[0]
        return result

    @patch('datasystem.database.psycopg2.connect')
    def test_get_active_chat(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Mock the execute method of the cursor
        mock_cursor.fetchall.return_value = []  # Simulate no chat found

        # Call the function
        result = get_active_chat('user1')

        # Assertions
        self.assertFalse(result, "Expected False, indicating no chat found")

    def get_user_gender_from_database(self, user_id):
        with psycopg2.connect(**DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT gender FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    def test_save_user_gender(self):
        # Assume there is an existing user with user_id '123' and gender 'male'
        user_id = '123'
        gender = 'male'
        save_user_gender(user_id, gender)

        # Check if the user's gender is updated correctly
        updated_gender = self.get_user_gender_from_database(user_id)
        self.assertEqual(updated_gender, gender)

        # Assume a new user with user_id '456' and gender 'female'
        user_id = '456'
        gender = 'female'
        save_user_gender(user_id, gender)

        # Check if the new user and their gender are saved correctly
        saved_gender = self.get_user_gender_from_database(user_id)
        self.assertEqual(saved_gender, gender)

    def test_save_user_interest(self):
        # Assume there is an existing user with user_id '123'
        user_id = '123'
        interest = 'music'
        save_user_interest(user_id, interest)

        # Check if the user's interest is updated correctly
        updated_interest = self.get_user_interest_from_database(user_id)
        self.assertEqual(updated_interest, interest)

    def test_save_user_age(self):
        # Assume there is an existing user with user_id '123'
        user_id = '123'
        age = 30
        save_user_age(user_id, age)

        # Check if the user's age is updated correctly
        updated_age = self.get_user_age_from_database(user_id)
        self.assertEqual(updated_age, age)

    def get_user_interest_from_database(self, user_id):
        with psycopg2.connect(**DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT interest FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    def get_user_age_from_database(self, user_id):
        with psycopg2.connect(**DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT age FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        
    @patch('datasystem.database.psycopg2.connect')
    def test_get_user_profile_with_nonexistent_profile(self, mock_connect):
        # Set up mock data and expected results
        user_id = 456
        
        # Configure the mock cursor to return None
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        
        # Configure the mock connection to return the mock cursor
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        # Call the function under test
        profile = get_user_profile(user_id)
        
        # Assert the results
        self.assertIsNone(profile)
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,)
        )
        mock_connect.return_value.close.assert_called_once()           

    def test_update_user_age(self):
        # Assume there is an existing user with user_id '123'
        user_id = '123'
        new_age = 35
        update_user_age(user_id, new_age)

        # Check if the user's age is updated correctly
        updated_age = self.get_user_age_from_database(user_id)
        self.assertEqual(updated_age, new_age)

    def get_user_age_from_database(self, user_id):
        with psycopg2.connect(**DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT age FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    @patch('datasystem.database.psycopg2.connect')
    def test_save_user_reaction(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value

        # Call the function
        save_user_reaction('user123', 'like')

        # Assertions
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET last_reaction = %s WHERE user_id = %s",
            ('like', 'user123')
        )
        mock_connect.return_value.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
