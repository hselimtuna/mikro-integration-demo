from dotenv import load_dotenv
import os
from src.logger.custom_logger import SingletonLogger

class Configs:

    def __init__(self):
        self._host: str = ""
        self._port: int = 0
        self._database: str = ""
        self._user: str = ""
        self._password: str = ""
        self._db_config: dict[str, str] = {}

        self._firma_kodu: str = ""
        self._kullanici_kodu: str = ""
        self._api_key: str = ""
        self._mikro_config: dict[str, any] = {}

        self._logger = SingletonLogger.get_logger()

    def db_config(self) -> dict[str, any]:

        load_dotenv()

        self._host: str = os.getenv("DB_HOST")
        self._port: int = os.getenv("DB_PORT")
        self._database: str = os.getenv("DB_NAME")
        self._user: str = os.getenv("DB_USER")
        self._password: str = os.getenv("DB_PASS")

        self._db_config: dict[str, any] = {
            "host": self._host,
            "port": self._port,
            "database": self._database,
            "user": self._user,
            "password": self._password
        }

        return self._db_config

    def mikro_config(self) -> dict[str, str]:

        load_dotenv()

        self._firma_kodu: str = os.getenv("FIRMA_KODU")
        self._kullanici_kodu: str = os.getenv("KULLANICI_KODU")
        self._api_key: str = os.getenv("API_KEY")

        self._mikro_config: dict[str, str] = {
            "firma_kodu": self._firma_kodu,
            "kullanici_kodu": self._kullanici_kodu,
            "api_key": self._api_key
        }

        return self._mikro_config