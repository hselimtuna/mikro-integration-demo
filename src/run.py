from src.config.conf_parser import Configs
from src.logger.custom_logger import SingletonLogger
from src.scripts.db.connector.connector import DatabaseConnector
from src.scripts.etl.extractor import Extractor
from src.scripts.etl.transformer import Transformer
from src.scripts.generator.md5_hashed_password import MD5HashedPassword
from src.scripts.generator.siparis_kaydet_v2_json import SiparisKaydetV2JSON
from src.scripts.generator.mikro_api_up_v2_json import MikroApiUp
from src.scripts.etl.loader import Loader
from src.scripts.utils.file_handler import FileHandler
import time

class Run:

    def __init__(self):
        self._configs = Configs()
        self._db_config: dict[str, any] = self._configs.db_config()
        db_conn = DatabaseConnector(**self._db_config)
        self._mikro_config: dict[str, str] = self._configs.mikro_config()
        self._siparis_kaydet_v2_generator = SiparisKaydetV2JSON(**self._mikro_config)
        self._login_mikro = MikroApiUp(**self._mikro_config)
        self._extractor = Extractor(db_conn)
        self._transformer = Transformer()
        self._password_generator = MD5HashedPassword(self._mikro_config.get("kullanici_kodu"))
        self._loader = Loader()
        self._logger = SingletonLogger.get_logger()
        self._file_handler = FileHandler()

    def run_program(self):

        while True:

            try:
                latest_order_json: dict[str, any] = self._extractor.get_latest_order_from_orders_table()

                order_code_in_doc: str = self._file_handler.get_last_order_code_from_txt()

                if latest_order_json.get("Code") != order_code_in_doc:

                    order_id, created_at, customer_id = (self._extractor.
                                                         fetch_from_latest_order(latest_order=latest_order_json))

                    customer_code: str = (self._extractor.
                                          fetch_customer_code_from_latest_users(customer_id=customer_id))

                    self._extractor.get_latest_order_item_from_order_items_table(order_id=order_id)
                    order_items: list[dict] = self._extractor.fetch_product_code_from_products_table()

                    final_order_items: list[dict[str, any]] = self._transformer.prepare_final_order_items(
                        order_items=order_items,
                        latest_order_json=latest_order_json,
                        customer_code=customer_code
                    )

                    md5_hash_pass: str = self._password_generator.get_hashed_password()

                    mikro_api_up_json: dict = self._login_mikro.prepare_login_json(md5_hash_pass=md5_hash_pass)
                    self._loader.post_mikro_api_up(mikro_api_up_json=mikro_api_up_json)

                    siparis_kaydet_v2_json: dict = self._siparis_kaydet_v2_generator.prepare_final_siparis_kaydet_v2_json(
                        final_order_items=final_order_items, md5_hash_pass=md5_hash_pass)
                    self._loader.post_siparis_kaydet(siparis_kaydet_json=siparis_kaydet_v2_json)

                    self._file_handler.write_last_order_to_txt(last_order_code=latest_order_json.get("Code"))
                    time.sleep(120)

            except:
                time.sleep(120)

            else:
                self._logger.info(f"Yeni bir sipariş bulunmamaktadır...")
                time.sleep(120)