from datetime import datetime
import os
import hashlib

from config import Config
from utils import (
    rsa_encrypt,
    rsa_decrypt,
    datetime_to_string,
)
from managers.base_manager import BaseManager
from entities.user import User


class UserManager(BaseManager):
    def __init__(self, config: Config):
        super().__init__(config)

    def login(self, username, password):
        user = self.get_user(username)
        if user is None:
            return None
        return user if self.verify_password(user.password, password) else None

    def update_last_login(self, user):
        encrypted_last_login = rsa_encrypt(datetime_to_string(datetime.now()), self.config.public_key)
        SQL_UPDATE_LAST_LOGIN = """
                UPDATE users SET last_login = ? WHERE id = ?;
                """
        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_UPDATE_LAST_LOGIN, (encrypted_last_login, user.id))
            self.config.con.commit()
        finally:
            cursor.close()

    def hash_and_salt(self, password):
        salt = os.urandom(16)
        hashed_password = hashlib.sha256(salt + password.encode()).hexdigest()
        salt_hex = salt.hex()
        return f"{salt_hex}:{hashed_password}"

    def verify_password(self, stored_password, provided_password):
        salt_hex, hashed_password = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        provided_hashed_password = hashlib.sha256(salt + provided_password.encode()).hexdigest()
        return provided_hashed_password == hashed_password

    def get_users(self) -> list[User]:
        SQL_SELECT_USERS = "SELECT * FROM users;"
        cursor = None
        result = []
        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_SELECT_USERS)
            result = cursor.fetchall()
        except Exception as e:
            # print(f"Error fetching users: {e}")
            ...
        finally:
            if cursor is not None:
                cursor.close()

        users = []
        for user_data in result:
            user = User(*user_data)
            user.username = rsa_decrypt(user.username, self.config.private_key)
            user.password = rsa_decrypt(user.password, self.config.private_key)
            user.role = rsa_decrypt(user.role, self.config.private_key)
            user.last_login = rsa_decrypt(user.last_login, self.config.private_key)
            users.append(user)

        return users

    def get_user(self, username: str) -> User:
        for user in self.get_users():
            if user.username == username:
                return user
        return None

    def create_user(self, username: str, password: str, role: str):
        hashed_password = self.hash_and_salt(password)
        encrypted_username = rsa_encrypt(username, self.config.public_key)
        encrypted_password = rsa_encrypt(hashed_password, self.config.public_key)
        encrypted_role = rsa_encrypt(role, self.config.public_key)
        encrypted_last_login = rsa_encrypt(datetime_to_string(datetime.now()), self.config.public_key)

        SQL_CREATE_USER = """
            INSERT INTO users (username, password, role, last_login) VALUES (?, ?, ?, ?);
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_CREATE_USER,
                (
                    encrypted_username,
                    encrypted_password,
                    encrypted_role,
                    encrypted_last_login,
                ),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_user(username)

    def update_user(self, user: User, username: str, role: str):
        encrypted_username = rsa_encrypt(username, self.config.public_key)
        encrypted_role = rsa_encrypt(role, self.config.public_key)

        SQL_UPDATE_USER = """
            UPDATE users SET username = ?, role = ? WHERE id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_USER,
                (encrypted_username, encrypted_role, user.id),
            )
            self.config.con.commit()
        finally:
            cursor.close()

    def reset_password(self, user: User, new_password: str):
        hashed_password = self.hash_and_salt(new_password)
        encrypted_new_password = rsa_encrypt(hashed_password, self.config.public_key)
        SQL_UPDATE_USER = """
            UPDATE users SET password = ?, reset_password = ? WHERE id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_USER,
                (encrypted_new_password, True, user.id),
            )
            self.config.con.commit()
        finally:
            cursor.close()

    def reset_password_status(self, user: User, reset_password: bool = False):
        SQL_UPDATE_USER = """
            UPDATE users SET reset_password = ? WHERE id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_USER,
                (reset_password, user.id),
            )
            self.config.con.commit()
            return True
        except Exception as e:
            # print(f"Error resetting status: {str(e)}")
            ...
        finally:
            cursor.close()

    def delete_user(self, user: User):
        SQL_DELETE_USER = """
            DELETE FROM users WHERE id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_DELETE_USER, (user.id,))
            self.config.con.commit()

        finally:
            cursor.close()

    def is_available_username(self, username):
        if username not in (user.username for user in self.get_users()):
            return True
        return False
