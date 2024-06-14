from enum import Enum


class Member:
    class Gender(Enum):
        MALE = "M"
        FEMALE = "F"

    def __init__(
        self,
        id,
        registration_date,
        first_name,
        last_name,
        age,
        gender,
        weight,
        address,
        email,
        phone_number,
        membership_id
    ):
        self.id = id
        self.registration_date = registration_date
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.weight = weight
        self.address = address
        self.email = email
        self.phone_number = phone_number
        self.membership_id = membership_id
