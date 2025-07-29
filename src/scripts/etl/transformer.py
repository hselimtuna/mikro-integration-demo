from datetime import datetime

from src.logger.custom_logger import SingletonLogger
class Transformer():

    def __init__(self):
        self._logger = SingletonLogger.get_logger()

    def prepare_final_order_items(self, order_items: list[dict[str, any]],
                                  latest_order_json: dict[str, any],
                                  customer_code: str):
        order_items_step_one: list[dict[str, any]] = (
            self._delete_product_id_from_order_items(order_items=order_items))
        order_items_step_two: list[dict[str, any]] = (
            self._add_required_keys_to_order_items(latest_order_json=latest_order_json,
                                                   order_items=order_items_step_one,
                                                   customer_code=customer_code))
        order_items_step_three: list[dict[str, any]] = (
            self._transform_create_at_date_format(order_items=order_items_step_two))
        order_items_step_four: list[dict[str, any]] = (
            self._add_total_price_to_order_items(order_items=order_items_step_three))
        final_order_items: list[dict[str, any]] = (
            self._delete_order_id_from_order_items(order_items=order_items_step_four))

        return final_order_items

    @staticmethod
    def _transform_create_at_date_format(order_items: list[dict[str, any]]) -> list[dict[str, any]]:
        for order_item in order_items:
            created_at: str = order_item["orderDate"]
            dt = datetime.fromisoformat(created_at)
            formatted_dt = dt.strftime("%d.%m.%Y")
            order_item["orderDate"] = formatted_dt

        return order_items

    @staticmethod
    def _delete_product_id_from_order_items(order_items: list[dict[str, any]]) -> list[dict[str, any]]:
        for order_item in order_items:
            order_item.pop("productId", None)

        return order_items

    @staticmethod
    def _add_required_keys_to_order_items(latest_order_json: dict[str, any],
                                         order_items: list[dict[str, any]],
                                         customer_code: str) -> list[dict[str, any]]:
        latest_order_id = latest_order_json["Id"]
        order_code = latest_order_json["Code"]
        order_date = latest_order_json["OrderDate"]


        for item in order_items:
            if item["orderId"] == latest_order_id:
                item["orderCode"] = order_code
                item["orderDate"] = order_date
                item["customerCode"] = customer_code

        return order_items

    @staticmethod
    def _add_total_price_to_order_items(order_items: list[dict[str, any]]) -> list[dict[str, any]]:
        for item in order_items:
            quantity: int = int(item["quantity"])
            price: float = float(item["price"])
            total: float = float(quantity * price)
            item["totalPrice"]: float = total

        return order_items

    @staticmethod
    def _delete_order_id_from_order_items(order_items: list[dict[str, any]] ) -> list[dict[str, any]]:
        for item in order_items:
            item.pop("orderId", None)

        return order_items
