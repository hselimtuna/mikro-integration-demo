from src.logger.custom_logger import SingletonLogger
from datetime import datetime
import json

class MikroApiUp:

    def __init__(self, api_key: str = None, firma_kodu: str = None, kullanici_kodu: str = None):
        self._logger = SingletonLogger.get_logger()

        self._api_key: str = api_key
        self._firma_kod: str = firma_kodu
        self._kullanici_kodu: str = kullanici_kodu
        self._current_year: str = datetime.today().strftime("%Y")

    def prepare_login_json(self, md5_hash_pass: str, indent: int = 2):

        json_structure= {
            "ApiKey": self._api_key,
            "FirmaKodu": self._firma_kod,
            "CalismaYili": self._current_year,
            "KullaniciKodu": self._kullanici_kodu,
            "Sifre": md5_hash_pass,
            "FirmaNo": 0,
            "SubeNo": 0
        }

        self._logger.info(f"Mikro'ya login olmak için JSON hazırlandı")
        return json.dumps(json_structure, ensure_ascii=False, indent=indent)
