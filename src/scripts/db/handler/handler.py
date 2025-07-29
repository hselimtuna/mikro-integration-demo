from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from src.logger.custom_logger import SingletonLogger
from typing import List, Dict, Any, Optional
import re

class DatabaseHandler:

    def __init__(self, connector):
        self._connector = connector
        self._logger = SingletonLogger().get_logger()

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        try:
            with self._connector.get_engine().connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                columns = list(result.keys())
                rows = []

                for row in result:
                    row_dict = {}
                    for i, value in enumerate(row):
                        if value is not None:
                            if hasattr(value, 'isoformat'):
                                row_dict[columns[i]] = value.isoformat()
                            elif hasattr(value, '__str__') and not isinstance(value, (int, float, bool, str)):
                                row_dict[columns[i]] = str(value)
                            else:
                                row_dict[columns[i]] = value
                        else:
                            row_dict[columns[i]] = None

                    rows.append(row_dict)

                return rows

        except SQLAlchemyError as e:
            self._logger.error(f"SQL sorgu hatası: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Genel hata: {e}")
            raise

    def _format_table_name(self, table_name: str) -> str:
        if any(c.isupper() for c in table_name):
            return f'"{table_name}"'
        return table_name

    def execute_select(self, table_name: str, columns: List[str] = None,
                       where_clause: str = None, params: Dict = None) -> List[Dict[str, Any]]:
        if columns:
            formatted_columns = [self._format_table_name(col) if any(c.isupper() for c in col) else col for col in
                                 columns]
            columns_str = ", ".join(formatted_columns)
        else:
            columns_str = "*"

        formatted_table_name = self._format_table_name(table_name)
        query = f"SELECT {columns_str} FROM {formatted_table_name}"

        if where_clause:
            def format_identifier(match):
                identifier = match.group(0)
                if any(c.isupper() for c in identifier):
                    return f'"{identifier}"'
                return identifier

            formatted_where = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', format_identifier, where_clause)
            query += f" WHERE {formatted_where}"

        return self.execute_query(query, params)

    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> bool:
        try:
            columns = list(data.keys())
            formatted_columns = [self._format_table_name(col) if any(c.isupper() for c in col) else col for col in
                                 columns]
            placeholders = [f":{col}" for col in columns]
            formatted_table_name = self._format_table_name(table_name)

            query = f"""
            INSERT INTO {formatted_table_name} ({', '.join(formatted_columns)}) 
            VALUES ({', '.join(placeholders)})
            """

            with self._connector.get_engine().connect() as conn:
                with conn.begin():
                    conn.execute(text(query), data)

            self._logger.info(f"Insert başarılı: {table_name}")
            return True

        except SQLAlchemyError as e:
            self._logger.error(f"Insert hatası: {e}")
            return False

    def execute_update(self, table_name: str, data: Dict[str, Any], where_clause: str, params: Dict = None) -> bool:
        try:
            columns = list(data.keys())
            formatted_columns = [self._format_table_name(col) if any(c.isupper() for c in col) else col for col in
                                 columns]
            set_clause = ", ".join([f"{col} = :{key}" for col, key in zip(formatted_columns, columns)])
            formatted_table_name = self._format_table_name(table_name)
            query = f"UPDATE {formatted_table_name} SET {set_clause} WHERE {where_clause}"

            all_params = data.copy()
            if params:
                all_params.update(params)

            with self._connector.get_engine().connect() as conn:
                with conn.begin():
                    result = conn.execute(text(query), all_params)

            self._logger.info(f"Update başarılı: {table_name}, {result.rowcount} satır güncellendi")
            return True

        except SQLAlchemyError as e:
            self._logger.error(f"Update hatası: {e}")
            return False

    def execute_delete(self, table_name: str, where_clause: str, params: Dict = None) -> bool:
        try:
            formatted_table_name = self._format_table_name(table_name)
            query = f"DELETE FROM {formatted_table_name} WHERE {where_clause}"

            with self._connector.get_engine().connect() as conn:
                with conn.begin():
                    result = conn.execute(text(query), params or {})

            self._logger.info(f"Delete başarılı: {table_name}, {result.rowcount} satır silindi")
            return True

        except SQLAlchemyError as e:
            self._logger.error(f"Delete hatası: {e}")
            return False

    def to_json(self, data: List[Dict[str, Any]]) -> list[dict[str, Any]]:
        try:
            return data
        except Exception as e:
            self._logger.error(f"SQL sorgu çıktısını JSON'a dönüştürme hatası: {e}")
            raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = :table_name
        ORDER BY ordinal_position
        """

        return self.execute_query(query, {"table_name": table_name})

    def get_all_tables(self, schema: str = None) -> List[Dict[str, Any]]:
        if schema:
            query = """
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = :schema
            ORDER BY table_schema, table_name
            """
            return self.execute_query(query, {"schema": schema})

        else:
            query = """
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
            """
            return self.execute_query(query)

    def check_table_exists(self, table_name: str, schema: str = 'public') -> bool:
        query = """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_name = :table_name AND table_schema = :schema
        """

        result = self.execute_query(query, {"table_name": table_name, "schema": schema})
        return result[0]['count'] > 0

    def get_table_count(self, table_name: str) -> int:
        formatted_table_name = self._format_table_name(table_name)
        query = f"SELECT COUNT(*) as count FROM {formatted_table_name}"
        result = self.execute_query(query)
        return result[0]['count']