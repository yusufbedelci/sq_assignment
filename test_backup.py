import sqlite3
from config import Config
from main import load_private_key, load_public_key
from backups import Backups
import time
from managers.user_manager import UserManager
from entities.user import User


config = Config(sqlite3.connect("data.db"), load_public_key(), load_private_key())

# Create a backup
_backups = Backups(config)

# Create a backup
_backups.create()

_user_manager = UserManager(config)
user = User(
    id=1,
    username="consultant_0",
    password="Admin_123?",
    role=User.Role.CONSULTANT,
    reset_password=False,
)
_user_manager.delete_user(user)

# # freeze for 2 seconds
time.sleep(10)
# # List backups
backupslist = _backups.list()

# # Restore a backup
_backups.restore(backupslist[0])
