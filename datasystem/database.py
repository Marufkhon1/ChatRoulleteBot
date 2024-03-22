import psycopg2
from psycopg2 import sql
import logging
import json
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



   
            
def save_user_gender(user_id, gender='Скрытый'):
    with psycopg2.connect(**DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)"), (user_id,))
            user_exists = cursor.fetchone()[0]

            if user_exists:
                cursor.execute(sql.SQL("UPDATE users SET gender = %s WHERE user_id = %s"), (gender, user_id))
            else:
                cursor.execute(sql.SQL("INSERT INTO users (user_id, gender) VALUES (%s, %s)"), (user_id, gender))

    logging.info(f"User {user_id} updated gender to {gender}")


def save_user_interest(user_id, interest="other"):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET interest = %s WHERE user_id = %s", (interest, user_id))
    conn.commit()
    conn.close()

    logging.info(f"User {user_id} updated interest to {interest}")


def save_user_age(user_id, age=None):
    if age is None:
        age = "Скрытый "
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
        gender = 'Скрытый' if profile_data[1] is None else ('🙎‍♂Парень' if profile_data[1] == 'male' else '🙍‍♀Девушка')
        age = profile_data[2] if profile_data[2] is not None else 'Возраст не указан'
        interest = 'Общение' if profile_data[3] == 'chat' else 'Другое'
        
        profile = {
            'gender': gender,
            'age': age,
            'interest': interest
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

def save_reaction(partner_user_id, reaction):
    conn = psycopg2.connect(**DATABASE)
    cur = conn.cursor()
    try:
        # Get the current reactions for the partner user
        cur.execute("SELECT reactions FROM users WHERE user_id = %s", (partner_user_id,))
        row = cur.fetchone()
        
        # If no row is found, log the error and return
        if row is None:
            print("User ID not found:", partner_user_id)
            return
        
        current_reactions_json = row[0]
        
        # If there are no reactions yet, initialize an empty dictionary
        if current_reactions_json is None:
            current_reactions = {}
        else:
            current_reactions = current_reactions_json
        
        # Update the count for the reaction
        current_reactions[reaction] = current_reactions.get(reaction, 0) + 1
        
        # Convert the dictionary to a JSON string
        updated_reactions_json = json.dumps(current_reactions)
        
        # Update the user's record with the new reactions
        cur.execute("UPDATE users SET reactions = %s WHERE user_id = %s", (updated_reactions_json, partner_user_id))
        
        conn.commit()
        print("Reaction saved successfully.")
    except psycopg2.Error as e:
        print("Error saving reaction:", e)
    finally:
        cur.close()
        conn.close()

def get_user_reactions(user_id):
    conn = psycopg2.connect(**DATABASE)
    cur = conn.cursor()
    try:
        # Fetch reactions data for the user
        cur.execute("SELECT reactions FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        
        # If no row is found, return an empty dictionary
        if row is None:
            return {}
        
        reactions_data = row[0]
        
        # If reactions data is None, return an empty dictionary
        if reactions_data is None:
            return {}
        
        return reactions_data
    except psycopg2.Error as e:
        print("Error fetching reactions:", e)
        return {}
    finally:
        cur.close()
        conn.close()




