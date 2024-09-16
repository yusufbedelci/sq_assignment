import logging
from config import Config
from utils import rsa_encrypt, string_to_datetime


class AppLogger:
    def __init__(self, config: Config, log_file="app.log", level=logging.DEBUG):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.login_attempts = 0
        self.config = config

        if not self.logger.hasHandlers():
            c_handler = logging.StreamHandler()
            f_handler = logging.FileHandler(log_file, mode="a")

            c_format = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%m/%d/%Y, %H:%M:%S",
            )
            f_format = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%m/%d/%Y, %H:%M:%S",
            )

            c_handler.setFormatter(c_format)
            f_handler.setFormatter(f_format)

            # Add handlers to the logger
            self.logger.addHandler(c_handler)
            self.logger.addHandler(f_handler)

    def log_activity(self, user, descr_activity, additional_info, suspicious_level):
        if user is not None:
            message = f"User: {user.username}, Role: ({user.role}), Performed activity: {descr_activity}, Info: {additional_info}"
        else:
            message = f"Activity: {descr_activity}, Info: {additional_info}"

        # self.logger.info(rsa_encrypt(message,self.config.public_key))
        if suspicious_level == True:
            self.logger.critical(message)
        else:
            self.logger.info(message)

    def get_logs(self):
        log_file = self.logger.handlers[1].baseFilename
        logs = []
        try:
            with open(log_file, "r") as file:
                for line in file.readlines():
                    values = [val.strip() for val in line.split("|")]
                    logs.append(values)
        except FileNotFoundError:
            pass
        return logs

    def get_critical_logs(self, last_login):
        critical_logs = []
        for log in self.get_logs():
            if log[1] == "CRITICAL" and string_to_datetime(log[0]) > string_to_datetime(
                last_login
            ):
                critical_logs.append(log)
        return critical_logs
