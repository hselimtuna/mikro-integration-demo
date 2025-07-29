from dataclasses import dataclass

@dataclass()
class Mikro:

    login_mikro: str = "http://localhost:8084/Api/APIMethods/APILogin"
    siparis_kaydet_v2: str = "http://localhost:8084/api/APIMethods/SiparisKaydetV2"