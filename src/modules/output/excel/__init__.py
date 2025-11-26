import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.modules.module import ModuleInfo
from src.modules.output.output import Output
from src.orm.models import Dictionary


class ExcelOutput(Output):
    """
    Модуль для сохранения результатов в Excel.
    """

    def __init__(self, dictionaries: list[str]):
        """
        Args:
            dictionaries: список словарей
        """
        self.dictionaries = dictionaries
        self.logger = logging.getLogger(ExcelOutput.info().name())

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="output", type="excel")

    def handle(self) -> None:
        """Запуск генерации Excel"""
        from src.container import container

        with container.db_session() as session:
            dictionaries = self._load_dictionaries(session, self.dictionaries)

            results = self._load_statistics(session, dictionaries)

            self._generate_excel(results)

    def _load_statistics(self, session: Session, dictionaries: list[Dictionary]):
        """
        Статистика терминов по годам и словарям.

        Args:
            session: сессия SQLAlchemy
            dictionaries: список словарей

        Returns:
            Собранная статистика по годам и словарям
        """

        params = {}
        select_fields = []
        join_tables = []
        group_fields = []
        dict_column_to_dict_name_map = {}

        # Проходим по списку словарей и подготавливаем части SQL для постановки в финальный запрос.
        for idx, dictionary in enumerate(dictionaries):
            # Для множественного объединения таблиц используем алиасы.
            table_alias = f"ref_{idx}"

            # Параметр для dictionary_id
            param_name = f"dict_id_{idx}"
            params[param_name] = dictionary.id

            dict_column = f"in_{idx}"
            select_fields.append(
                f"CASE WHEN {table_alias}.id IS NULL THEN '' ELSE {table_alias}.ref_id END AS {dict_column}"
            )
            # Также сохраняем связку колонки и названия словаря для дальнейшего его восстановления.
            # Передавать в SQL название словаря как название колонки не безопасно,
            # поэтому используется такой путь.
            dict_column_to_dict_name_map[dict_column] = dictionary.name

            join_tables.append(
                f"""
                LEFT JOIN term_dictionary_ref {table_alias}
                       ON {table_alias}.term_id = t.id
                      AND {table_alias}.dictionary_id = :{param_name}
                """
            )

            group_fields.append(dict_column)

        joins_sql = "\n".join(join_tables)
        fields_sql = ",\n        ".join(select_fields)
        group_sql = ", ".join(group_fields)

        # Финальный SQL
        sql = f"""
        SELECT
            t.term_text,
            t.word_count,
            EXTRACT(YEAR FROM a.pubdate) AS year,
            COUNT(*) AS count,
            {fields_sql}
        FROM terms t
        JOIN article_term_annotations ann ON t.id = ann.term_id
        JOIN articles a ON a.id = ann.article_id
        {joins_sql}
        GROUP BY t.term_text, t.word_count, year, {group_sql}
        ORDER BY t.term_text, year;
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        rows = session.execute(text(sql), params).mappings().all()
        ret = []

        # Делаем маппинг данных на структуру, подходящую для использования в Excel.
        for row in rows:
            result = {
                "Term": row.term_text,
                "Word count": row.word_count,
                "Year": row.year,
                "Count": row.count,
            }
            for table_alias, dict_name in dict_column_to_dict_name_map.items():
                # Восстанавливаем название словаря.
                result[dict_name] = row[table_alias]

            ret.append(result)

        return ret

    def _generate_excel(self, results: list[dict]) -> None:
        """
        Генерация Excel из результатов.

        Args:
            results: результаты для записи в файл
        """
        if not results:
            self.logger.warning("Нет данных для записи в Excel")
            return

        # Превращаем результаты в DataFrame
        df = pd.DataFrame(results)

        # Сохраняем
        self._create_experiment_dir()
        excel_file = self._generate_output_file_path("statistics.xlsx")
        df.to_excel(excel_file, index=False)

        self.logger.info(f"Результаты сохранены в файл {excel_file}")
