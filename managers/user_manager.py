import os
from entities.user import User
import hashlib


class UserManager:
    @staticmethod
    def initialize(con):
        SQL_CREATE_USER_TABLE = """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY ,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
                );
            """

        cursor = con.cursor()
        cursor.execute(SQL_CREATE_USER_TABLE)
        con.commit()
        cursor.close()

    @staticmethod
    def create_super_admin(con):
        password = UserManager.password_hash("Admin_123?")
        CREATE_SUPER_ADMIN = f"INSERT INTO users (username, password, role) VALUES ('super_admin', '{password}', '{User.Role.SUPER_ADMIN.value}');"
        cursor = con.cursor()
        cursor.execute(CREATE_SUPER_ADMIN)
        con.commit()
        cursor.close()

    @staticmethod
    def login(con, username, password):
        cursor = con.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?;",
            (username,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return None
        
        user = User(*result)
        if UserManager.verify_password(user.password, password):
            return user
        else:
            return None

    @staticmethod
    def password_hash(password):
        salt = os.urandom(16)
        hashed_password = hashlib.sha256(salt + password.encode()).hexdigest()
        salt_hex = salt.hex()
        return f"{salt_hex}:{hashed_password}"
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        salt_hex, hashed_password = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        provided_hashed_password = hashlib.sha256(salt + provided_password.encode()).hexdigest()
        return provided_hashed_password == hashed_password