# Авто-тесты

В разработке
используется [TDD-подход](https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0_%D1%87%D0%B5%D1%80%D0%B5%D0%B7_%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5):
сначала тесты, затем - код. Таким образом создаются тесты, которые можно запускать автоматически.

Для изоляции от внешних зависимостей используются моки из
библиотеки [unittest.mock](https://docs.python.org/3/library/unittest.mock.html).

Из библиотеки [pytest](https://docs.pytest.org/en/stable/) используется:

* `pytest.fixture` - для создания фикстур и подмены рабочей БД на тестовую - см. [conftest.py](tests/conftest.py);
* `pytest.mark.parametrize` - для создания параметризованных тестов.

Библиотека [factory_boy](https://factoryboy.readthedocs.io/en/stable/) используется для создания ORM-моделей для
тестирования.
