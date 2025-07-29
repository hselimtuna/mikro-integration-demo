from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.logger.custom_logger import SingletonLogger

class DatabaseConnector:

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls, host=None, port=None, database=None, user=None, password=None):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host=None, port=None, database=None, user=None, password=None):
        if self._initialized:
            return

        if not all([host, port, database, user, password]):
            raise ValueError("Tüm veritabanı bağlantı parametreleri gerekli")

        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._logger = SingletonLogger().get_logger()

        connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        try:
            self._engine = create_engine(
                connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

            self._session_factory = sessionmaker(bind=self._engine)

            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            self._initialized = True
            self._logger.info(f"Veritabanı bağlantısı başarılı: {host}:{port}/{database}")

        except SQLAlchemyError as e:
            self._logger.error(f"Veritabanı bağlantı hatası: {e}")
            raise

    def get_engine(self):
        if not self._initialized:
            raise RuntimeError("Connector initialize edilmemiş")
        return self._engine

    def get_session(self):
        if not self._initialized:
            raise RuntimeError("Connector initialize edilmemiş")
        return self._session_factory()

    def test_connection(self):
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self._logger.info(f"PostgreSQL versiyon: {version}")
                return True
        except SQLAlchemyError as e:
            self._logger.error(f"Bağlantı testi başarısız: {e}")
            return False

    def close(self):
        if self._engine:
            self._engine.dispose()
            self._logger.info("Veritabanı bağlantıları kapatıldı")