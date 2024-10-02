from datetime import datetime
from config import Config
from utils import rsa_encrypt, rsa_decrypt, generate_registration_date
from managers.base_manager import BaseManager
from entities.profile import Profile


class ProfileManager(BaseManager):
    def __init__(self, config: Config):
        super().__init__(config)

    def initialize(self):
        SQL_CREATE_PROFILES_TABLE = """
            CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            user_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_CREATE_PROFILES_TABLE)
            self.config.con.commit()
        finally:
            cursor.close()

    def seed_profiles(self):
        profiles = [
            {
                "id": 2,
                "first_name": "Jason",
                "last_name": "Wang",
            },
            {
                "id": 3,
                "first_name": "Emily",
                "last_name": "Jansen",
            },
            {
                "id": 4,
                "first_name": "David",
                "last_name": "De Vries",
            },
            {
                "id": 5,
                "first_name": "Sarah",
                "last_name": "Meijer",
            },
        ]

        for profile in profiles:
            if any(
                profile["first_name"] == existing_profile.first_name
                and profile["last_name"] == existing_profile.last_name
                for existing_profile in self.get_profiles()
            ):
                return

            encrypted_first_name = rsa_encrypt(profile["first_name"], self.config.public_key)
            encrypted_last_name = rsa_encrypt(profile["last_name"], self.config.public_key)
            encrypted_registration_date = rsa_encrypt(generate_registration_date(), self.config.public_key)

            SQL_CREATE_USER_PROFILES = (
                f"INSERT INTO profiles (first_name, last_name, registration_date, user_id) VALUES (?, ?, ?, ?);"
            )
            try:
                cursor = self.config.con.cursor()
                cursor.execute(
                    SQL_CREATE_USER_PROFILES,
                    (
                        encrypted_first_name,
                        encrypted_last_name,
                        encrypted_registration_date,
                        profile["id"],
                    ),
                )

                self.config.con.commit()

            finally:
                cursor.close()

    def get_profiles(self) -> list[Profile]:
        SQL_SELECT_PROFILES = "SELECT * FROM profiles;"
        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_SELECT_PROFILES)
            result = cursor.fetchall()
        finally:
            cursor.close()

        profiles = []
        for profile_data in result:
            profile = Profile(*profile_data)
            profile.first_name = rsa_decrypt(profile.first_name, self.config.private_key)
            profile.last_name = rsa_decrypt(profile.last_name, self.config.private_key)
            profile.registration_date = rsa_decrypt(profile.registration_date, self.config.private_key)
            profiles.append(profile)

        return profiles

    def get_profile(self, user_id: int) -> Profile:
        for profile in self.get_profiles():
            if profile.user_id == user_id:
                return profile
        return None

    def create_profile(self, first_name: str, last_name: str, user_id: int) -> Profile:
        encrypted_first_name = rsa_encrypt(first_name, self.config.public_key)
        encrypted_last_name = rsa_encrypt(last_name, self.config.public_key)
        encrypted_registration_date = rsa_encrypt(generate_registration_date(), self.config.public_key)

        SQL_CREATE_PROFILE = """
            INSERT INTO profiles (first_name, last_name, registration_date, user_id)
            VALUES (?, ?, ?, ?);
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_CREATE_PROFILE,
                (
                    encrypted_first_name,
                    encrypted_last_name,
                    encrypted_registration_date,
                    user_id,
                ),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_profile(user_id)

    def update_profile(self, profile: Profile, first_name: str, last_name: str) -> Profile:
        encrypted_first_name = rsa_encrypt(first_name, self.config.public_key)
        encrypted_last_name = rsa_encrypt(last_name, self.config.public_key)

        SQL_UPDATE_PROFILE = """
            UPDATE profiles SET first_name = ?, last_name = ? WHERE user_id = ?;
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_PROFILE,
                (encrypted_first_name, encrypted_last_name, profile.user_id),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_profile(profile.user_id)
