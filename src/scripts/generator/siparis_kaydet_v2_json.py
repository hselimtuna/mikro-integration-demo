from src.logger.custom_logger import SingletonLogger
from typing import List, Dict, Any
import json
from datetime import datetime

class SiparisKaydetV2JSON:

    def __init__(self, api_key: str = None, firma_kodu: str = None, kullanici_kodu: str = None, sifre: str = None):
        self._logger = SingletonLogger.get_logger()

        self._api_key: str = api_key
        self._firma_kod: str = firma_kodu
        self._kullanici_kodu: str = kullanici_kodu
        self._sifre: str = sifre
        self._seriler_no : int = 0

        self._current_year: str = datetime.today().strftime("%Y")

    def prepare_final_siparis_kaydet_v2_json(self, final_order_items: list[dict[str, any]], md5_hash_pass: str) -> dict:

        mikro_json = self._generate_json(final_order_items=final_order_items,
                                         md5_hash_pass=md5_hash_pass)

        if self._validate_json_structure(mikro_json):
            mikro_json = self._generate_json_string(final_order_items=final_order_items,
                                                    md5_hash_pass=md5_hash_pass)

            self._logger.info(f"Mikro'ya sipariş kaydetmek için JSON oluşturuldu")
        return mikro_json

    def _create_satirlar_from_order_items(self, final_order_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        satirlar = []

        for order_item in final_order_items:
            satir = {
                "sip_tarih": order_item.get('orderDate', ''),
                "seriler": f"ARTEK{self._seriler_no}",
                "sip_birim_pntr": 0,
                "sip_cins": 0,
                "sip_evrakno_seri": order_item.get('orderCode', ''),
                "sip_musteri_kod": order_item.get('customerCode', ''),
                "sip_stok_kod": order_item.get('productCode', ''),
                "sip_b_fiyat": float(order_item.get('price', 0)),
                "sip_miktar": int(order_item.get('quantity', 0)),
                "sip_tutar": float(order_item.get('totalPrice', 0)),
                "sip_vergi_pntr": 0,
                "sip_depono": 1,
                "sip_vergisiz_fl": False,
                "sip_stok_sormerk": "",
                "user_tablo": [
                    {
                        "aciklama": ""
                    }
                ]
            }
            satirlar.append(satir)

        self._seriler_no += 1
        return satirlar

    @staticmethod
    def _create_evrak_aciklamalari(order_code: str = None) -> List[Dict[str, str]]:
        return [
            {
                "aciklama": f"Sipariş: {order_code}" if order_code else "Sipariş"
            }
        ]

    def _generate_json(self, final_order_items: List[Dict[str, Any]], md5_hash_pass: str) -> Dict[str, Any]:

        if not final_order_items:
            self._logger.warning("Sipariş için JSON oluşturulurken herhangi bir sipariş saptanamadı")
            return {}

        order_code = final_order_items[0].get('orderCode', '') if final_order_items else ''
        satirlar = self._create_satirlar_from_order_items(final_order_items)
        evrak_aciklamalari = self._create_evrak_aciklamalari(order_code)

        json_structure = {
            "Mikro": {
                "FirmaKodu": self._firma_kod,
                "CalismaYili": self._current_year,
                "KullaniciKodu": self._kullanici_kodu,
                "Sifre": md5_hash_pass,
                "ApiKey": self._api_key,
                "evraklar": [
                    {
                        "evrak_aciklamalari": evrak_aciklamalari,
                        "satirlar": satirlar
                    }
                ]
            }
        }

        self._logger.info(f"Sipariş kaydet için {len(satirlar)} kadar ürün içeren JSON hazırlanıyor...")
        return json_structure

    def _generate_json_string(self, final_order_items: List[Dict[str, Any]], md5_hash_pass: str, indent: int = 2) -> str:

        json_dict = self._generate_json(final_order_items, md5_hash_pass)
        self._logger.info(f"Sipariş kaydet JSON, Mikro API formatına göre düzenlendi ")
        return json.dumps(json_dict, ensure_ascii=False, indent=indent)

    def add_additional_evrak(self, json_structure: Dict[str, Any],
                             additional_order_items: List[Dict[str, Any]]) -> Dict[str, Any]:

        if not additional_order_items:
            return json_structure

        order_code = additional_order_items[0].get('orderCode', '') if additional_order_items else ''
        new_satirlar = self._create_satirlar_from_order_items(additional_order_items)
        new_evrak_aciklamalari = self._create_evrak_aciklamalari(order_code)

        new_evrak = {
            "evrak_aciklamalari": new_evrak_aciklamalari,
            "satirlar": new_satirlar
        }

        json_structure["Mikro"]["evraklar"].append(new_evrak)

        self._logger.info(f"Yeni evrak, {len(new_satirlar)} kadar ürün için hazırlandı")
        return json_structure

    def _validate_json_structure(self, json_structure: Dict[str, Any]) -> bool:

        try:
            mikro = json_structure.get("Mikro", {})
            required_fields = ["FirmaKodu", "CalismaYili", "KullaniciKodu", "Sifre", "ApiKey", "evraklar"]

            for field in required_fields:
                if field not in mikro:
                    self._logger.error(f"Sipariş Kaydet V2 için eksik kısımlar: {field}")
                    return False

            evraklar = mikro.get("evraklar", [])
            if not isinstance(evraklar, list) or len(evraklar) == 0:
                self._logger.error("Sipariş Kaydet V2 için 'Evraklar' kısmı boş olamaz")
                return False

            for i, evrak in enumerate(evraklar):
                if "satirlar" not in evrak or "evrak_aciklamalari" not in evrak:
                    self._logger.error(f"Sipariş Kaydet V2 'Evraklar' için {i}.  satırdan eksik alanlar testpit edildi")
                    return False

            self._logger.info("JSON yapısı Mikro validasyon kurallarına uygun !")
            return True

        except Exception as e:
            self._logger.error(f"JSON validasyonu hatası: {str(e)}")
            return False