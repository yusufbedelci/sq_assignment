from config import Config
from app_logger import AppLogger
from entities.user import User


class BaseForm:
    def __init__(self, root, config, logger, sender):
        self.root = root
        self.config: Config = config
        self.logger: AppLogger = logger
        self.sender: User = sender

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
