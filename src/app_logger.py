import logging
from logging.handlers import RotatingFileHandler
from config import Config
from utils import rsa_encrypt


class AppLogger:
    def __init__(self, config: Config, log_file="app.log", level=logging.DEBUG):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.login_attempts = 0
        self.config = config

        if not self.logger.hasHandlers():
            c_handler = logging.StreamHandler()
            f_handler = RotatingFileHandler(
                log_file, maxBytes=2000, backupCount=5, mode="a"
            )

            c_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            f_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            c_handler.setFormatter(c_format)
            f_handler.setFormatter(f_format)

            # Add handlers to the logger
            self.logger.addHandler(c_handler)
            self.logger.addHandler(f_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_activity(self, user, descr_activity, additional_info, suspicious_level):
        if user is not None:
            message = f"{user.username} ({user.role}) performed activity: {descr_activity} info: {additional_info} suspicous: {suspicious_level}"
        else:
            message = f"{descr_activity} info: {additional_info} suspicous: {suspicious_level}"

            # self.logger.info(rsa_encrypt(message,self.config.public_key))
        self.logger.info(message)
