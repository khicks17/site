import sqlite3
import secrets
import hashlib


def main():
    # 1.) Prompt user for info
    username = input("Enter username: ")
    password = input("Enter password: ")
    print("User: %s, with password %s" % (username, password))
    # 2.) Generate salt
    salt = secrets.token_hex(6)
    # 3.) Put together the salt and password
    salted_password = password + salt
    # 4.) Hash that thing!
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    conn = sqlite3.connect("tweet_db.db")
    conn.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                 (username, hashed_password, salt))
    cursor = conn.cursor()
    conn.commit()
    cursor.close()
    conn.close()


main()
