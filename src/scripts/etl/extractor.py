from typing import Optional

from src.scripts.db.handler.handler import DatabaseHandler
from src.logger.custom_logger import SingletonLogger

class Extractor(DatabaseHandler):

    def __init__(self, connector):
        super().__init__(connector)
        self._logger = SingletonLogger().get_logger()
        self.order_id: str = ""
        self.createdAt: str = ""
        self.customer_id: str = ""
        self.customer_code: str = ""
        self.formatted_order_items: list[dict[str, any]] = []
        self._db_handler = DatabaseHandler(connector=connector)

    def get_latest_order_from_orders_table(self) -> Optional[str]:
        orders_data: dict[str, any] = self._db_handler.execute_select(table_name="Orders")

        if orders_data:
            latest_order: dict[str, any] = orders_data[-1]
            latest_order_json: str = self._db_handler.to_json(latest_order)

            return latest_order_json

    def fetch_from_latest_order(self, latest_order: dict[str, any]) -> tuple[str, str, str]:
        self.order_id: str = latest_order.get("Id")
        self.createdAt: str = latest_order.get("CreatedAt")
        self.customer_id: str = latest_order.get("CustomerId")
        return self.order_id, self.createdAt, self.customer_id

    def fetch_customer_code_from_latest_users(self, customer_id: str) -> str:
        customer_data: list[dict] = self._db_handler.execute_select(
        table_name="Users",
        where_clause="Id = :customer_id",
        params={"customer_id": customer_id})

        if customer_data:
            customer: dict[str, any] = customer_data[0]
            customer_json: dict[str, any] = self._db_handler.to_json(customer)
            self.customer_code: str = customer_json.get("Code")
        return self.customer_code

    def get_latest_order_item_from_order_items_table(self, order_id: str) -> None:

        order_item_data: list[dict] = self._db_handler.execute_select(
            table_name="OrderItems",
            where_clause="OrderId = :order_id",
            params={"order_id": order_id}
        )

        if order_item_data:
            for order_item in order_item_data:
                self.formatted_order_items.append({"productId": order_item.get("ProductId"),
                                                    "quantity": order_item.get("Quantity"),
                                                    "price": order_item.get("Price"),
                                                    "orderId": order_item.get("OrderId")})

    def fetch_product_code_from_products_table(self) -> list[dict[str, any]]:
        for order_item in self.formatted_order_items:
            products_data: list[dict] = self._db_handler.execute_select(
                table_name="Products",
                where_clause="Id = :product_id",
                params={"product_id": order_item.get("productId")}
            )

            if products_data:
                product: dict[str, any] = products_data[0]
                product_code: str = product.get("Code")
                order_item["productCode"] = product_code

        return self.formatted_order_items
