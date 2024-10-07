from datetime import datetime
import hashlib
import os
import sqlite3
from config import Config
from entities.user import User
from cryptography.hazmat.primitives import serialization
from utils import datetime_to_string, generate_membership_id, generate_registration_date, rsa_encrypt
from pathlib import Path


dir_path = Path(__file__).resolve().parent


def load_private_key():
    try:
        private_key_path = dir_path / "keys/private.pem"
        with private_key_path.open("rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
    except FileNotFoundError:
        return None


def load_public_key():
    try:
        public_key_path = dir_path / "keys/public.pem"
        with public_key_path.open("rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
            )
    except FileNotFoundError:
        return None


def hash_and_salt(password):
    salt = os.urandom(16)
    hashed_password = hashlib.sha256(salt + password.encode()).hexdigest()
    salt_hex = salt.hex()
    return f"{salt_hex}:{hashed_password}"


#
# Initialize methods:
#
def initalize_users(config: Config):
    SQL_CREATE_USER_TABLE = """
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            reset_password BOOLEAN NOT NULL DEFAULT 0,
            last_login TEXT NOT NULL
            );
        """

    try:
        cursor = config.con.cursor()
        cursor.execute(SQL_CREATE_USER_TABLE)
        config.con.commit()
    finally:
        cursor.close()


def initalize_profiles(config: Config):
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
        cursor = config.con.cursor()
        cursor.execute(SQL_CREATE_PROFILES_TABLE)
        config.con.commit()
    finally:
        cursor.close()


def initalize_members(config: Config):
    SQL_CREATE_MEMBER_TABLE = """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                weight INTEGER NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                registration_date TEXT NOT NULL,
                membership_id INTEGER NOT NULL
            );
        """

    try:
        cursor = config.con.cursor()
        cursor.execute(SQL_CREATE_MEMBER_TABLE)
        config.con.commit()
    finally:
        cursor.close()


def initalize_addresses(config: Config):
    SQL_CREATE_ADDRESS_TABLE = """
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY,
                street_name TEXT NOT NULL,
                house_number TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                city TEXT NOT NULL,
                member_id INTEGER NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            );
        """

    try:
        cursor = config.con.cursor()
        cursor.execute(SQL_CREATE_ADDRESS_TABLE)
        config.con.commit()
    finally:
        cursor.close()


#
# Seeding methods:
#
def seed_super_admin(config: Config):
    # create super admin
    password = hash_and_salt("Admin_123?")
    encrypted_username = rsa_encrypt("super_admin", config.public_key)
    encrypted_password = rsa_encrypt(password, config.public_key)
    encrypted_role = rsa_encrypt(User.Role.SUPER_ADMIN.value, config.public_key)
    encrypted_last_login = rsa_encrypt(datetime_to_string(datetime.now()), config.public_key)
    SQL_CREATE_SUPER_ADMIN = f"INSERT INTO users (username, password, role, last_login) VALUES (?, ?, ?, ?);"
    try:
        cursor = config.con.cursor()
        cursor.execute(
            SQL_CREATE_SUPER_ADMIN,
            (
                encrypted_username,
                encrypted_password,
                encrypted_role,
                encrypted_last_login,
            ),
        )
        config.con.commit()
    finally:
        cursor.close()


def seed_users(config: Config):
    users = (
        {
            "username": "jasonw12",
            "password": "Pa$$w0rd1234",
            "role": User.Role.CONSULTANT.value,
            "first_name": "Jason",
            "last_name": "Wong",
        },
        {
            "username": "emilyj34",
            "password": "Pa$$w0rd1234",
            "role": User.Role.CONSULTANT.value,
            "first_name": "Emily",
            "last_name": "Jansen",
        },
        {
            "username": "davidd56",
            "password": "Pa$$w0rd1234",
            "role": User.Role.SYSTEM_ADMIN.value,
            "first_name": "David",
            "last_name": "De Vries",
        },
        {
            "username": "sarahm78",
            "password": "Pa$$w0rd1234",
            "role": User.Role.SYSTEM_ADMIN.value,
            "first_name": "Sarah",
            "last_name": "Meijer",
        },
    )

    for user in users:
        # user
        password = hash_and_salt(user["password"])
        encrypted_username = rsa_encrypt(user["username"], config.public_key)
        encrypted_password = rsa_encrypt(password, config.public_key)
        encrypted_role = rsa_encrypt(user["role"], config.public_key)
        encrypted_last_login = rsa_encrypt(datetime_to_string(datetime.now()), config.public_key)
        SQL_CREATE_USERS = f"INSERT INTO users (username, password, role, last_login) VALUES (?, ?, ?, ?);"

        try:
            cursor = config.con.cursor()
            cursor.execute(
                SQL_CREATE_USERS,
                (
                    encrypted_username,
                    encrypted_password,
                    encrypted_role,
                    encrypted_last_login,
                ),
            )
            config.con.commit()
            user_id = cursor.lastrowid
        finally:
            cursor.close()

        # profile
        encrypted_first_name = rsa_encrypt(user["first_name"], config.public_key)
        encrypted_last_name = rsa_encrypt(user["last_name"], config.public_key)
        encrypted_registration_date = rsa_encrypt(generate_registration_date(), config.public_key)
        SQL_CREATE_USER_PROFILES = (
            f"INSERT INTO profiles (first_name, last_name, registration_date, user_id) VALUES (?, ?, ?, ?);"
        )

        try:
            cursor = config.con.cursor()
            cursor.execute(
                SQL_CREATE_USER_PROFILES,
                (
                    encrypted_first_name,
                    encrypted_last_name,
                    encrypted_registration_date,
                    user_id,
                ),
            )
            config.con.commit()
        finally:
            cursor.close()


def seed_members(config: Config):
    data = (
        {
            "member": {
                "first_name": "Johan",
                "last_name": "de Vries",
                "age": 34,
                "gender": "M",
                "weight": 78,
                "email": "johan.devries@uniquemeal.nl",
                "phone_number": "0612345678",
            },
            "address": {
                "street_name": "Langestraat",
                "house_number": "12A",
                "zip_code": "1234 AB",
                "city": "Amsterdam",
            },
        },
        {
            "member": {
                "first_name": "Emma",
                "last_name": "Jansen",
                "age": 28,
                "gender": "F",
                "weight": 62,
                "email": "emma.jansen@uniquemeal.nl",
                "phone_number": "0687654321",
            },
            "address": {
                "street_name": "Hoofdweg",
                "house_number": "34",
                "zip_code": "2345 BC",
                "city": "Utrecht",
            },
        },
    )

    for item in data:
        # member
        member = item["member"]
        encrypted_firstname = rsa_encrypt(f'{member["first_name"]}', config.public_key)
        encrypted_lastname = rsa_encrypt(f'{member["last_name"]}', config.public_key)
        encrypted_age = rsa_encrypt(f'{member["age"]}', config.public_key)
        encrypted_weight = rsa_encrypt(f'{member["weight"]}', config.public_key)
        encrypted_email = rsa_encrypt(f'{member["email"]}', config.public_key)
        encrypted_phone_number = rsa_encrypt(f'{member["phone_number"]}', config.public_key)
        encrypted_gender = rsa_encrypt(f'{member["gender"]}', config.public_key)
        registration_date = generate_registration_date()
        encrypted_registration_date = rsa_encrypt(registration_date, config.public_key)
        encrypted_membership_id = rsa_encrypt(generate_membership_id(registration_date), config.public_key)

        SQL_CREATE_MEMBERS = f"INSERT OR IGNORE INTO members (first_name, last_name, age, gender, weight, email, phone_number, registration_date, membership_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"

        try:
            cursor = config.con.cursor()
            cursor.execute(
                SQL_CREATE_MEMBERS,
                (
                    encrypted_firstname,
                    encrypted_lastname,
                    encrypted_age,
                    encrypted_gender,
                    encrypted_weight,
                    encrypted_email,
                    encrypted_phone_number,
                    encrypted_registration_date,
                    encrypted_membership_id,
                ),
            )
            config.con.commit()
            member_id = cursor.lastrowid
        finally:
            cursor.close()

        # address
        address = item["address"]
        encrypted_street_name = rsa_encrypt(address["street_name"], config.public_key)
        encrypted_house_number = rsa_encrypt(address["house_number"], config.public_key)
        encrypted_zip_code = rsa_encrypt(address["zip_code"], config.public_key)
        encrypted_city = rsa_encrypt(address["city"], config.public_key)

        SQL_CREATE_ADDRESSES = (
            "INSERT INTO addresses (street_name, house_number, zip_code, city, member_id) VALUES (?, ?, ?, ?, ?);"
        )

        try:
            cursor = config.con.cursor()
            cursor.execute(
                SQL_CREATE_ADDRESSES,
                (
                    encrypted_street_name,
                    encrypted_house_number,
                    encrypted_zip_code,
                    encrypted_city,
                    member_id,
                ),
            )
            config.con.commit()
        finally:
            cursor.close()


if "__main__" == __name__:
    db_path = dir_path / "data.db"
    con = sqlite3.connect(db_path)
    config = Config(
        con=con,
        private_key=load_private_key(),
        public_key=load_public_key(),
    )

    # check if database already exists
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    cursor.close()
    if tables:
        print("Database already exists")
        con.close()
        exit()

    # initialize the database
    initalize_users(config)
    initalize_profiles(config)
    initalize_members(config)
    initalize_addresses(config)

    # seed the database
    seed_super_admin(config)
    seed_users(config)
    seed_members(config)

    con.close()
