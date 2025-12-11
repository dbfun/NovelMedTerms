import logging

from src.modules.module import ModuleInfo
from src.modules.output.charts.pos_model_by_year import PosModelByYear
from src.modules.output.charts.vocabulary_coverage import VocabularyCoverage
from src.modules.output.charts.wordcloud_image import WordcloudImage
from src.modules.output.output import Output


class ChartsOutput(Output):
    """
    Модуль для графического вывода результатов.
    """

    def __init__(self, dpi: int, dictionaries: list[str]):
        """
        Args:
            dpi: DPI для вывода графиков
            dictionaries: список словарей
        """
        self.dpi = dpi
        self.dictionaries = set(dictionaries)
        self.logger = logging.getLogger(ChartsOutput.info().name())

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="output", type="charts")

    def handle(self) -> None:
        """Запуск генерации графиков"""
        from src.container import container

        self._create_experiment_dir()

        with container.db_session() as session:
            dictionaries = self._load_dictionaries(session, self.dictionaries)

            # Генерация графика "Эволюция терминов в PubMed и их покрытие"
            output_file = self._generate_output_file_path("vocabulary_coverage.png")
            chart1 = VocabularyCoverage(session, self.dpi, dictionaries)
            chart1.handle(output_file)
            self.logger.info(f"Результаты сохранены в файл {output_file}")

            # Генерация облака слов.
            output_file = self._generate_output_file_path("wordcloud.png")
            chart2 = WordcloudImage(session, self.dpi, dictionaries)
            chart2.handle(2, 200, output_file)
            self.logger.info(f"Результаты сохранены в файл {output_file}")

            # Генерация графика "Динамика распределения POS-структур по годам, кроме униграмм"
            chart3 = PosModelByYear(session, self.dpi, dictionaries, self._generate_output_file_path)
            output_files = chart3.handle(10)
            output_files = ", ".join([str(file) for file in output_files])
            self.logger.info(f"Результаты сохранены в файлы {output_files}")
