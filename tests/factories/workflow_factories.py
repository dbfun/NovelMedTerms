import factory

from src.workflow import Config, Experiment, Stage, Module


class ModuleFactory(factory.Factory):
    """
    Фабрика для создания Module
    """

    class Meta:
        model = Module

    module = "pytest"
    type = "pytest"
    params = {"param1": "value1"}


class StageFactory(factory.Factory):
    """
    Фабрика для создания Stage
    """

    class Meta:
        model = Stage

    name = "Этап pytest"
    modules = factory.List([
        factory.SubFactory(ModuleFactory)
    ])


class ExperimentFactory(factory.Factory):
    """
    Фабрика для создания Experiment
    """

    class Meta:
        model = Experiment

    name = "Эксперимент Pytest"
    description = "Описание"
    author = "Pytest P.P."


class ConfigFactory(factory.Factory):
    """
    Фабрика для создания Config. Тестовая конфигурация, аналог workflow.yaml
    """

    class Meta:
        model = Config

    experiment = factory.SubFactory(ExperimentFactory)
    stages = factory.List([
        factory.SubFactory(StageFactory)
    ])
