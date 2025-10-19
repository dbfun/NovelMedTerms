from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine


class DbConnection(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def db_url(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


sync_engine = create_engine(
    url=DbConnection().db_url,
    # echo=True,  # Запись в консоль всех запросов к БД
    # pool_size=5,
    # max_overflow=10,
)

sessionLocal = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass
