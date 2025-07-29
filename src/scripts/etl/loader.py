from src.library.endpoints.mikro import Mikro
from src.logger.custom_logger import SingletonLogger
import requests

class Loader:

    def __init__(self):
        self._endpoints = Mikro()
        self._logger = SingletonLogger.get_logger()
        self._header: dict[str, str] = {"Content-Type": "application/json"}

    def post_mikro_api_up(self, mikro_api_up_json: dict) -> None:
        url: str = self._endpoints.login_mikro
        headers: dict = self._header
        payload: dict = mikro_api_up_json
        resp: requests.models.Response = requests.post(url=url, data=payload, headers=headers)

        if resp.status_code != 200:
            self._logger.error(f"Statü Kodu: {resp.status_code} - Mikro'ya login olunamadı :/ -> {resp.text} - {resp.content}")
        else:
            self._logger.info(f"Statü Kodu: {resp.status_code} - Login işlemi başarılı !")

    def post_siparis_kaydet(self, siparis_kaydet_json: dict) -> None:
        url: str = self._endpoints.siparis_kaydet_v2
        headers: dict = self._header
        payload: dict = siparis_kaydet_json
        resp: requests.models.Response = requests.post(url=url, data=payload, headers=headers)

        if resp.status_code != 200:
            self._logger.error(f"Statü Kodu: {resp.status_code} - Sipariş oluşturulamadı :/ -> {resp.text} - {resp.content}")
        else:
            self._logger.info(f"Statü Kodu: {resp.status_code} - Sipariş oluşturuldu !")
