import sys
from unittest.mock import patch

import yaml

from factories.workflow_factories import ConfigFactory
from workflow import Workflow


class TestWorkflow:
    """
    Тестирование workflow.py
    """

    def test_load_workflow_from_file(self, tmp_path):
        """
        Проверка корректности заполнения конфигурации из YAML-файла
        """
        cfg = ConfigFactory(experiment__directory=str(tmp_path))

        # Создаем тестовый файл workflow.yml
        path = tmp_path / "workflow.yml"
        print(path)
        path.write_text(yaml.safe_dump(cfg.model_dump(), allow_unicode=True), encoding="utf-8")

        # Создаем объект Workflow
        with patch.object(sys, "argv", ["prog", str(path)]):
            app = Workflow()

        # Проверяем конфигурацию
        assert cfg == app.cfg

    def test_workflow_run(self, tmp_path):
        """
        Проверка, что при выполнении workflow.py идет запуск модулей - на примере модуля PytestModule::handle()
        """
        with patch("workflow.Workflow._load_workflow_from_file"), \
                patch("src.modules.pytest.pytest_module.PytestModule.handle") as mock_handle:
            # Создаем объект Workflow
            app = Workflow()
            app.cfg = ConfigFactory(experiment__directory=str(tmp_path))
            app.run()

        # Проверяем, что был вызван PytestModule.handle()
        mock_handle.assert_called_once()
