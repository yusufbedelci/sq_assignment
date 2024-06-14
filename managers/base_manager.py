from config import Config


class BaseManager:
    def __init__(self, config):
        self.config: Config = config
