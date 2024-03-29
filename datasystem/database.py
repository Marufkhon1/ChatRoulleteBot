import psycopg2
import json
import logging
import dj_database_url

# Set up logging
logging.basicConfig(level=logging.INFO)

DATABASE = {
    "dbname": "dgnf1arp7q6a",
    "user": "ueach8c2u26cg9",
    "password": "p2744a7f94694fd4796173ed2836d762c3f643390921ef1140db4c9647bbae1b3",
    "host": "ec2-54-160-201-5.compute-1.amazonaws.com",
    "port": "5432",
}


def connect_to_database():
    try:
        conn = psycopg2.connect(**DATABASE)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None


def add_user(user_id, gender, age, interest):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, gender, age, interest) VALUES (%s, %s, %s, %s)",
                (user_id, gender, age, interest),
            )
            conn.commit()
            logging.info(f"User {user_id} added successfully")
        except psycopg2.Error as e:
            logging.error(f"Error adding user {user_id}: {e}")
        finally:
            conn.close()


def user_exists(user_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,)
                )
                result = cursor.fetchone()[0]
            return result
        except psycopg2.Error as e:
            logging.error(f"Error checking if user exists: {e}")
        finally:
            conn.close()
    return None


def save_user_gender(user_id, gender):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,)
                )
                user_exists = cursor.fetchone()[0]

                if user_exists:
                    cursor.execute(
                        "UPDATE users SET gender = %s WHERE user_id = %s",
                        (gender, user_id),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO users (user_id, gender) VALUES (%s, %s)",
                        (user_id, gender),
                    )
            conn.commit()
            logging.info(f"User {user_id} updated gender to {gender}")
        except psycopg2.Error as e:
            logging.error(f"Error saving user gender for user {user_id}: {e}")
        finally:
            conn.close()


def save_user_interest(user_id, interest):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET interest = %s WHERE user_id = %s",
                    (interest, user_id),
                )
            conn.commit()
            logging.info(f"User {user_id} updated interest to {interest}")
        except psycopg2.Error as e:
            logging.error(f"Error saving user interest for user {user_id}: {e}")
        finally:
            conn.close()


def save_user_age(user_id, age):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET age = %s WHERE user_id = %s", (age, user_id)
                )
            conn.commit()
            logging.info(f"User {user_id} updated age to {age}")
        except psycopg2.Error as e:
            logging.error(f"Error saving user age for user {user_id}: {e}")
        finally:
            conn.close()


def get_user_profile(user_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                profile_data = cursor.fetchone()
                if profile_data:
                    gender = profile_data[1] if profile_data[1] is not None else None
                    age = profile_data[2] if profile_data[2] is not None else None
                    interest = profile_data[3] if profile_data[3] is not None else None

                    if gender == "male":
                        gender = "Мужской"
                    elif gender == "female":
                        gender = "Женский"

                    # Translate "chat" into Russian
                    if interest == "chat":
                        interest = "Чат"

                    # Translate "other" into Russian
                    elif interest == "other":
                        interest = "Другое"

                    profile = {"gender": gender, "age": age, "interest": interest}

                    return profile
        except psycopg2.Error as e:
            logging.error(f"Error fetching user profile for user {user_id}: {e}")
        finally:
            conn.close()
    return None


def update_user_age(user_id, new_age):
    conn = connect_to_database()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET age = %s WHERE user_id = %s", (new_age, user_id)
            )
        conn.commit()
    except psycopg2.Error as e:
        print("Error updating user age:", e)
    finally:
        conn.close()


def get_user_age(user_id):
    conn = connect_to_database()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT age FROM users WHERE user_id = %s", (user_id,))
            age = cursor.fetchone()
            if age:
                return age[0]
    except psycopg2.Error as e:
        print("Error fetching user age:", e)
    finally:
        conn.close()
    return None


def get_user_gender(user_id):
    conn = connect_to_database()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT gender FROM users WHERE user_id = %s", (user_id,))
            gender = cursor.fetchone()
            if gender:
                return gender[0]
    except psycopg2.Error as e:
        print("Error fetching user gender:", e)
    finally:
        conn.close()
    return None


def get_user_interest(user_id):
    conn = connect_to_database()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT interest FROM users WHERE user_id = %s", (user_id,))
            interest = cursor.fetchone()
            if interest:
                return interest[0]
    except psycopg2.Error as e:
        print("Error fetching user interest:", e)
    finally:
        conn.close()
    return None


def save_reaction(partner_user_id, reaction):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cur:
                # Get the current reactions for the partner user
                cur.execute(
                    "SELECT reactions FROM users WHERE user_id = %s", (partner_user_id,)
                )
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
                    current_reactions = current_reactions_json  # No need to parse JSON

                # Update the count for the reaction
                current_reactions[reaction] = current_reactions.get(reaction, 0) + 1

                # Convert the dictionary to a JSON string
                updated_reactions_json = json.dumps(current_reactions)

                # Update the user's record with the new reactions
                cur.execute(
                    "UPDATE users SET reactions = %s WHERE user_id = %s",
                    (updated_reactions_json, partner_user_id),
                )

                conn.commit()
                print("Reaction saved successfully.")
        except psycopg2.Error as e:
            print("Error saving reaction:", e)
        finally:
            conn.close()



def get_user_reactions(user_id):
    conn = connect_to_database()
    try:
        with conn.cursor() as cur:
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
        conn.close()


def save_user_age(user_id, age):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,)
                )
                user_exists = cursor.fetchone()[0]

                if user_exists:
                    cursor.execute(
                        "UPDATE users SET age = %s WHERE user_id = %s", (age, user_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO users (user_id, age) VALUES (%s, %s)",
                        (user_id, age),
                    )
            conn.commit()
            logging.info(f"User {user_id} updated age to {age}")
        except psycopg2.Error as e:
            logging.error(f"Error saving user age for user {user_id}: {e}")
        finally:
            conn.close()


def save_user_interest(user_id, interest):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,)
                )
                user_exists = cursor.fetchone()[0]

                if user_exists:
                    cursor.execute(
                        "UPDATE users SET interest = %s WHERE user_id = %s",
                        (interest, user_id),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO users (user_id, interest) VALUES (%s, %s)",
                        (user_id, interest),
                    )
            conn.commit()
            logging.info(f"User {user_id} updated interest to {interest}")
        except psycopg2.Error as e:
            logging.error(f"Error saving user interest for user {user_id}: {e}")
        finally:
            conn.close()
