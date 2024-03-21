import psycopg2
from psycopg2 import sql
import logging
from bot import logging


DATABASE = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '12345'
}


def add_user(user_id, gender, age, interest):
    try:
        conn = psycopg2.connect(**DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, gender, age, interest) VALUES (%s, %s, %s, %s)",
            (user_id, gender, age, interest)
        )
        conn.commit()
        conn.close()
        logging.info(f"User {user_id} added successfully")
    except psycopg2.Error as e:
        logging.error(f"Error adding user {user_id}: {str(e)}")



def user_exists(user_id):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)"), (user_id,))
            result = cursor.fetchone()[0]
    return result

def get_chat():
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users ORDER BY RANDOM() LIMIT 1")
            chat = cursor.fetchone()
            return chat[0] if chat else None


def delete_chat(id_chat):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            return cursor.execute("DELETE FROM chats WHERE id = %s", (id_chat,))
   

def create_chat(chat_one, chat_two):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            if chat_one != chat_two:  # Check if chat_one is different from chat_two
                cursor.execute("INSERT INTO chats (chat_one, chat_two) VALUES (%s, %s)", (chat_one, chat_two))
                return True
            else:
                return False
 

def get_active_chat(chat_id):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            # Check if chat_one matches the provided chat_id
            cursor.execute("SELECT * FROM chats WHERE chat_one = %s::text", (str(chat_id),))
            row = cursor.fetchone()  # Fetch only one row if found
            if row:
                return [row[0], row[2]]  # Return chat_info

            # Check if chat_two matches the provided chat_id
            cursor.execute("SELECT * FROM chats WHERE chat_two = %s::text", (str(chat_id),))
            row = cursor.fetchone()  # Fetch only one row if found
            if row:
                return [row[0], row[1]]  # Return chat_info

            # If no chat is found, return False
            return False



   
            
def save_user_gender(user_id, gender):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)"), (user_id,))
            user_exists = cursor.fetchone()[0]

            if user_exists:
                cursor.execute(sql.SQL("UPDATE users SET gender = %s WHERE user_id = %s"), (gender, user_id))
            else:
                cursor.execute(sql.SQL("INSERT INTO users (user_id, gender) VALUES (%s, %s)"), (user_id, gender))

    logging.info(f"User {user_id} updated gender to {gender}")


def save_user_interest(user_id, interest):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET interest = %s WHERE user_id = %s", (interest, user_id))
    conn.commit()
    conn.close()


def save_user_age(user_id, age):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET age = %s WHERE user_id = %s", (age, user_id))
    logging.info(f"User {user_id} updated age to {age}")


def get_user_profile(user_id):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    profile_data = cursor.fetchone()
    conn.close()
    
    if profile_data:
        profile = {
            'gender': '🙎‍♂Парень' if profile_data[1] == 'male' else '🙍‍♀Девушка',
            'age': profile_data[2],
            'interest': 'Общение' if profile_data[3] == 'chat' else 'Интим 18+',
        }
        return profile
    else:
        return None
    

def update_user_age(user_id, new_age):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET age = %s WHERE user_id = %s", (new_age, user_id))
    conn.commit()
    conn.close()

    



