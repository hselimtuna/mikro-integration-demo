import logging
from threading import Lock

class SingletonLogger:
    _instance = None
    _lock = Lock()

    def __new__(cls, engine=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._logger = logging.getLogger("CustomLogger")
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s', "%Y-%m-%d %H:%M:%S")

        if not self._logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

    @classmethod
    def get_logger(cls, engine=None):
        return cls(engine)._logger