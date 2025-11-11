import pytest

from mock_module import mock_module
from src.container import container
from src.modules.module import Module, ModuleInfo
from src.modules.pytest.pytest_module import PytestModule


class TestModule:

    def test_container_module(self):
        """
        Проверка создания модуля через container.module(). Формат определяется в workflow.yaml:

        - module: pytest
          type: pytest
          param1: value1
        """

        param1 = "value1"

        module = container.module(
            module="pytest",
            type="pytest",
            param1=param1,
        )

        assert isinstance(module, PytestModule), "Тип модуля не совпадает"
        assert module.param1 == param1, "Параметр не передан"
        assert hasattr(module, "handle"), "Модуль должен иметь метод handle()"

    def test_module_not_found(self):
        """
        Проверка обработки ошибки при запросе несуществующего модуля.
        """
        with pytest.raises(KeyError) as exc_info:
            container.module(module="unknown", type="unknown")

        assert "не зарегистрирован" in str(exc_info.value)

    def test_mock_module_with_context_manager(self):
        """
        Пример подмены модуля через mock_module() для TDD с вложенным вызовом.
        """

        class MockPytestModule1(Module):
            def __init__(self):
                pass

            def handle(self):
                pass

            @staticmethod
            def info() -> ModuleInfo:
                pass

        class MockPytestModule2(Module):
            def __init__(self):
                pass

            def handle(self):
                pass

            @staticmethod
            def info() -> ModuleInfo:
                pass

        # Подмена модуля
        with mock_module("pytest", "pytest", MockPytestModule1):
            # Вложенная подмена модуля
            with mock_module("pytest", "pytest", MockPytestModule2):
                module = container.module(module="pytest", type="pytest")

                assert isinstance(module, MockPytestModule2)

            module = container.module(module="pytest", type="pytest")

            assert isinstance(module, MockPytestModule1)

        # После выхода из контекста оригинальный модуль должен быть восстановлен
        module = container.module(module="pytest", type="pytest", param1="value1")
        assert isinstance(module, PytestModule)
