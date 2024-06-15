import os
import hashlib

from config import Config
from utils import rsa_encrypt, rsa_decrypt
from managers.base_manager import BaseManager
from entities.user import User


class UserManager(BaseManager):
    def __init__(self, config: Config):
        super().__init__(config)

    def initialize(self):
        SQL_CREATE_USER_TABLE = """
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                reset_password BOOLEAN NOT NULL DEFAULT 0
                );
            """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_CREATE_USER_TABLE)
            self.config.con.commit()
        finally:
            cursor.close()

    def create_super_admin(self):
        # check if super admin already exists
        if any(user.role == User.Role.SUPER_ADMIN.value for user in self.get_users()):
            return

        # create super admin
        password = self.hash_and_salt("Admin_123?")
        encrypted_username = rsa_encrypt("super_admin", self.config.public_key)
        encrypted_password = rsa_encrypt(password, self.config.public_key)
        encrypted_role = rsa_encrypt(
            User.Role.SUPER_ADMIN.value, self.config.public_key
        )

        SQL_CREATE_SUPER_ADMIN = (
            f"INSERT INTO users (username, password, role) VALUES (?, ?, ?);"
        )

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_CREATE_SUPER_ADMIN,
                (encrypted_username, encrypted_password, encrypted_role),
            )
            self.config.con.commit()
        finally:
            cursor.close()

    def login(self, username, password):
        user = self.get_user(username)
        if user is None:
            return None

        return user if self.verify_password(user.password, password) else None

    def hash_and_salt(self, password):
        salt = os.urandom(16)
        hashed_password = hashlib.sha256(salt + password.encode()).hexdigest()
        salt_hex = salt.hex()
        return f"{salt_hex}:{hashed_password}"

    def verify_password(self, stored_password, provided_password):
        salt_hex, hashed_password = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        provided_hashed_password = hashlib.sha256(
            salt + provided_password.encode()
        ).hexdigest()
        return provided_hashed_password == hashed_password

    def get_users(self) -> list[User]:
        SQL_SELECT_USERS = "SELECT * FROM users;"
        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_SELECT_USERS)
            result = cursor.fetchall()
        finally:
            cursor.close()

        users = []
        for user_data in result:
            user = User(*user_data)
            user.username = rsa_decrypt(user.username, self.config.private_key)
            user.password = rsa_decrypt(user.password, self.config.private_key)
            user.role = rsa_decrypt(user.role, self.config.private_key)
            users.append(user)

        return users

    def get_user(self, username: str) -> User:
        for user in self.get_users():
            if user.username == username:
                return user
        return None

    def create_user(self, username: str, password: str, role: str):
        if next(filter(lambda user: user.username == username, self.get_users()), None):
            return None

        encrypted_username = rsa_encrypt(username, self.config.public_key)
        encrypted_password = rsa_encrypt(password, self.config.public_key)
        encrypted_role = rsa_encrypt(role, self.config.public_key)

        SQL_CREATE_USER = """
            INSERT INTO users (username, password, role) VALUES (?, ?, ?);
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_CREATE_USER,
                (encrypted_username, encrypted_password, encrypted_role),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_user(username)

    def update_user(self, user: User, username: str, password: str, role: str):
        if next(filter(lambda user: user.username == username, self.get_users()), None):
            return None

        encrypted_username = rsa_encrypt(username, self.config.public_key)
        encrypted_password = rsa_encrypt(password, self.config.public_key)
        encrypted_role = rsa_encrypt(role, self.config.public_key)

        SQL_UPDATE_USER = """
            UPDATE users SET username = ?, password = ?, role = ? WHERE user_id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_USER,
                (encrypted_username, encrypted_password, encrypted_role, user.id),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_user(username)

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
