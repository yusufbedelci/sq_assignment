import re


def validate_username(username):
    pattern = r"^(?!.*[_.]{2})[a-zA-Z_](?:[\w.\'-]{6,8})$"
    if re.match(pattern, username) and "\x00" not in username:
        return True
    return False


def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/])[A-Za-z\d~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/]{12,30}$"
    if re.match(pattern, password) and "\x00" not in password:
        return True
    return False


def validate_name(name):
    pattern = r"^[a-zA-Z]{2,20}$"
    if re.match(pattern, name) and "\x00" not in name:
        return True
    return False


def validate_age(age):
    pattern = r"^(?:[1-9][0-9]?|100)$"
    if re.match(pattern, age) and "\x00" not in age:
        return True
    return False


def validate_weight(weight):
    pattern = r"^(?:[1-9][0-9]?|1[0-9]{2}|200|201)$"  # 1-201 KG
    if re.match(pattern, str(weight)) and "\x00" not in weight:
        return True
    return False


def validate_email(email):
    """
    Username part (before the @): between 1 and 64 characters.
    The domain part (after the @) to a range of between 1 and 255.
    The TLD is between 2 and 24 characters.
    """
    pattern = r"^[a-zA-Z0-9_.+-]{1,64}@[a-zA-Z0-9-]{1,255}\.[a-zA-Z]{2,24}$"

    if re.match(pattern, email) and "\x00" not in email:
        return True
    return False


def validate_phone_number(phone_number):
    pattern = r"^(?:\+?31|0)(?:[1-9][0-9]?|6[1-6])\d{7}$"  # Dutch phone number
    if re.match(pattern, phone_number) and "\x00" not in phone_number:
        return True
    return False


def validate_street_name(street_name):
    pattern = r"^[a-zA-Z0-9\s]{2,30}$"
    if re.match(pattern, street_name) and "\x00" not in street_name:
        return True
    return False


def validate_house_number(house_number):
    pattern = r"^[1-9][0-9]{0,3}[a-zA-Z]{0,1}$"
    if re.match(pattern, house_number) and "\x00" not in house_number:
        return True
    return False

def validate_zip_code(zip_code):
    pattern = r"^[1-9][0-9]{3}\s?[a-zA-Z]{2}$"
    if re.match(pattern, zip_code) and "\x00" not in zip_code:
        return True
    return False

def validate_server_input(option, options):
    if option in options:
        return True
    return False