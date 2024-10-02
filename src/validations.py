import re


def valid(value, pattern):
    return re.match(pattern, value) and "\x00" not in value


def validate_username(username):
    pattern = r"^(?!.*[_.]{2})[a-zA-Z_](?:[\w.\'-]{6,8})$"
    if valid(username, pattern):
        return True
    return False


def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/])[A-Za-z\d~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/]{12,30}$"
    if valid(password, pattern):
        return True
    return False


def validate_name(name):
    pattern = r"^[a-zA-Z]{2,20}$"
    if valid(name, pattern):
        return True
    return False


def validate_age(age):
    pattern = r"^(?:[1-9][0-9]?|100)$"
    if valid(age, pattern):
        return True
    return False


def validate_weight(weight):
    pattern = r"^(?:[1-9][0-9]?|1[0-9]{2}|200|201)$"  # 1-201 KG
    if valid(weight, pattern):
        return True
    return False


def validate_email(email):
    """
    Username part (before the @): between 1 and 64 characters.
    The domain part (after the @) to a range of between 1 and 255.
    The TLD is between 2 and 24 characters.
    """
    pattern = r"^[a-zA-Z0-9_.+-]{1,64}@[a-zA-Z0-9-]{1,255}\.[a-zA-Z]{2,24}$"
    if valid(email, pattern):
        return True
    return False


def validate_phone_number(phone_number):
    pattern = r"^(?:\+?31|0)(?:[1-9][0-9]?|6[1-6])\d{7}$"  # Dutch phone number
    if valid(phone_number, pattern):
        return True
    return False


def validate_street_name(street_name):
    pattern = r"^[a-zA-Z0-9\s]{2,30}$"
    if valid(street_name, pattern):
        return True
    return False


def validate_house_number(house_number):
    pattern = r"^[1-9][0-9]{0,3}[a-zA-Z]{0,1}$"
    if valid(house_number, pattern):
        return True
    return False


def validate_zip_code(zip_code):
    pattern = r"^[1-9][0-9]{3}\s?[a-zA-Z]{2}$"
    if valid(zip_code, pattern):
        return True
    return False


def validate_server_input(option, options):
    if option in options:
        return True
    return False
