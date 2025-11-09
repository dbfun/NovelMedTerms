from src.container import container
from src.modules.cleaner.database import CleanerDatabase
from src.orm.models import Article


class TestCleanerDatabase:

    def test_handle(self, valid_article):
        """Проверка, что модуль очищает БД от данных ORM-модели"""

        with container.db_session() as session:
            # Подготовка: создаем тестовую статью
            session.add(valid_article)
            session.commit()

            assert 1 == session.query(Article).count()

            # Запуск модуля
            module = CleanerDatabase(["Article"])
            module.handle()

            assert 0 == session.query(Article).count()
