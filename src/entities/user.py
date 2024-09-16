from enum import Enum


class User:
    class Role(Enum):
        SUPER_ADMIN = "super_admin"
        SYSTEM_ADMIN = "system_admin"
        CONSULTANT = "consultant"

    def __init__(self, id, username, password, role, reset_password, last_login):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.reset_password = reset_password
        self.last_login = last_login

    def __str__(self) -> str:
        return f"{self.id} {self.username} ({self.role})"
