from datetime import datetime
import logging
from config import Config
from utils import datetime_to_string, string_to_datetime, rsa_encrypt, rsa_decrypt
import base64
from pathlib import Path


class AppLogger:
    def __init__(self, config: Config, log_file="app.log", level=logging.DEBUG):
        self.login_attempts = 0
        self.config = config
        self.dir_path = Path(__file__).resolve().parent
        self.log_file = self.dir_path / log_file

    def write(self, log_line):
        with self.log_file.open("a") as file:
            file.write(log_line + "\n")

    def log_activity(self, user, descr_activity, additional_info, suspicious_level):
        current_datetime = datetime_to_string(datetime.now())
        level_name = "CRITICAL" if suspicious_level else "INFO"
        if user is not None:
            message = f"User: {user.username}, Role: ({user.role}), Performed activity: {descr_activity}, Info: {additional_info}"
        else:
            message = f"Activity: {descr_activity}, Info: {additional_info}"

        if "|" in message:
            message = message.replace("|", "%7C")

        log_line = rsa_encrypt(
            f"{current_datetime}|{level_name}|{message}|{suspicious_level}",
            self.config.public_key,
        )
        encrypted_log_b64 = base64.b64encode(log_line).decode()
        self.write(encrypted_log_b64)

    def get_logs(self):
        logs = []
        try:
            with self.log_file.open("r") as file:
                for line in file.readlines():
                    line = base64.b64decode(line)
                    line = rsa_decrypt(line, self.config.private_key)
                    values = [val.replace("%7C", "|").strip() for val in line.split("|")]
                    logs.append(values)
        except FileNotFoundError:
            pass
        return logs

    def get_critical_logs(self, last_login):
        critical_logs = []
        for log in self.get_logs():
            if log[1] == "CRITICAL" and string_to_datetime(log[0]) > string_to_datetime(last_login):
                critical_logs.append(log)
        return critical_logs

    def get_logs_sorted(self, last_login):
        all_logs = reversed(self.get_logs())
        labeled_logs = []
        for log in all_logs:
            if log[1] == "CRITICAL" and string_to_datetime(log[0]) > string_to_datetime(last_login):
                labeled_logs.append(["unread", log])
            else:
                labeled_logs.append(["read", log])

        return labeled_logs
