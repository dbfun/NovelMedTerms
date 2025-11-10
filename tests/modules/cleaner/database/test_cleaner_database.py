from src.modules.cleaner.database import CleanerDatabase
from src.orm.models import Article


class TestCleanerDatabase:

    def test_handle(self, valid_article, db_session):
        """Проверка, что модуль очищает БД от данных ORM-модели"""

        # Подготовка: создаем тестовую статью
        db_session.add(valid_article)
        db_session.commit()

        assert 1 == db_session.query(Article).count()

        # Запуск модуля
        module = CleanerDatabase(["Article"])
        module.handle()

        assert 0 == db_session.query(Article).count()
