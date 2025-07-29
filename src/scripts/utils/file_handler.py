from src.logger.custom_logger import SingletonLogger

class FileHandler:

    def __init__(self):

        self._latest_order_file_name = "docs/latest_order_code.txt"
        self._logger = SingletonLogger.get_logger()

    def get_last_order_code_from_txt(self) -> str:

        order_code_in_doc: str = ""

        with open(file=self._latest_order_file_name, mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                if "En son oluşturulan sipariş kodu:" in line:
                    order_code_in_doc: str = line.split(":")[1]
                    self._logger.info(f"En son işlem gören sipariş kodu belgeden okundu: {order_code_in_doc}")

        return order_code_in_doc

    def write_last_order_to_txt(self, last_order_code: str) -> None:

        with open(file=self._latest_order_file_name, mode="w", encoding="utf-8") as f:
            f.write(f"En son oluşturulan sipariş kodu:{last_order_code}")

        self._logger.info(f"En son işlem gören sipariş kodu yeniden .txt dosyasında güncellendi.")