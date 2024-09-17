from datetime import datetime
from random import randint
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
import re


def rsa_encrypt(message: str, public_key: RSAPublicKey) -> bytes:
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def rsa_decrypt(ciphertext: bytes, private_key: RSAPrivateKey) -> str:
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    ).decode()


def generate_registration_date() -> str:
    return str(datetime.now().date())


def generate_membership_id(registration_date: str) -> str:
    initial = registration_date[2:4]
    random_digits = "".join([str(randint(0, 9)) for _ in range(7)])
    membership_id = f"{initial}{random_digits}"
    checksum = sum(int(digit) for digit in membership_id) % 10
    return f"{membership_id}{checksum}"


def validate_username(username):
    pattern = r"^(?!.*[_.]{2})[a-zA-Z_](?:[\w.\'-]{6,8})$"
    return bool(re.match(pattern, username))


def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/])[A-Za-z\d~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/]{12,30}$"
    return bool(re.match(pattern, password))


def datetime_to_string(time_to_convert):
    return time_to_convert.strftime("%m/%d/%Y, %H:%M:%S")


def string_to_datetime(datetime_to_convert):
    return datetime.strptime(datetime_to_convert, "%m/%d/%Y, %H:%M:%S")
