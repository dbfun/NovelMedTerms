from pathlib import Path

import matplotlib.pyplot as plt
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.helper import disable_logging, enable_logging
from src.orm.models import Dictionary


class VocabularyCoverage():
    """
    Генерация графика "Эволюция терминов в PubMed и их покрытие"
    """

    def __init__(self, session: Session, dpi: int, dictionaries: list[Dictionary]):
        self.session = session
        self.dpi = dpi
        self.dictionaries = dictionaries

    def handle(self, output_file_path: Path) -> None:
        """
        Запуск генерации

        Args:
            output_file_path: путь к файлу для сохранения результатов
        """
        results = self._fetch_results()
        self._generate_chart(results, output_file_path)

    def _fetch_results(self) -> list[dict]:
        """
        Получение данных из БД для построения диаграммы.
        """
        params = {}
        select_fields = []
        join_tables = []
        dict_column_to_dict_name_map = {}

        # Проходим по списку словарей и подготавливаем части SQL для постановки в финальный запрос.
        for idx, dictionary in enumerate(self.dictionaries):
            # Для множественного объединения таблиц используем алиасы.
            table_alias = f"ref_{idx}"

            # Параметр для dictionary_id
            param_name = f"dict_id_{idx}"
            params[param_name] = dictionary.id

            dict_column = f"in_{idx}"
            select_fields.append(
                f"SUM(CASE WHEN {table_alias}.id IS NULL THEN 0 ELSE 1 END) AS {dict_column}"
            )
            # Также сохраняем связку колонки и названия словаря для дальнейшего его восстановления.
            # Передавать в SQL название словаря как название колонки не безопасно,
            # поэтому используется такой путь.
            dict_column_to_dict_name_map[dict_column] = dictionary.name

            join_tables.append(
                f"""
                LEFT JOIN term_dictionary_ref {table_alias}
                       ON {table_alias}.term_id = t.id
                      AND {table_alias}.dictionary_id = :{param_name}""")

        joins_sql = "\n".join(join_tables)
        fields_sql = ",\n        ".join(select_fields)

        # Финальный SQL
        sql = f"""
        SELECT
            EXTRACT(YEAR FROM a.pubdate) AS year,
            COUNT(*)                     AS total_count,
            {fields_sql}
        FROM terms t
            JOIN article_term_annotations ann ON t.id = ann.term_id
            JOIN articles a ON a.id = ann.article_id
            {joins_sql}
        GROUP BY year
        ORDER BY year;
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        rows = self.session.execute(text(sql), params).mappings().all()
        ret = []

        # Делаем маппинг данных на структуру, подходящую для построения диаграммы.
        for row in rows:
            result = {
                "year": row.year,
                "total_count": row.total_count,
                "in_dict": {}
            }
            for table_alias, dict_name in dict_column_to_dict_name_map.items():
                # Создаем словарь в формате "название словаря": "количество терминов"
                result["in_dict"][dict_name] = row[table_alias]

                ret.append(result)

            ret.append(result)

        return ret

    def _generate_chart(self, results: list[dict], output_file_path: Path) -> None:
        disable_logging()

        years = [d["year"] for d in results]
        total = [d["total_count"] for d in results]

        plt.figure(figsize=(12, 6))
        plt.title("Эволюция терминов в PubMed и их покрытие словарями")
        plt.xticks(years)

        # Левая ось: общее количество терминов
        ax1 = plt.gca()
        ax1.plot(years, total, label="Общее количество извлеченных терминов", color="gray", linestyle="-", linewidth=2)
        ax1.set_xlabel("Год")
        ax1.set_ylabel("Количество терминов")
        ax1.tick_params(axis="y")

        # Правая ось: доля терминов в словарях
        ax2 = ax1.twinx()
        ax2.set_ylabel("Процент покрытия", color="black")
        ax2.tick_params(axis="y", labelcolor="black")

        # Трансформируем результаты в набор значений по словарям
        cnt_by_dict = {}

        for result in results:
            # Пример структуры result:
            # {'year': Decimal('2015'), 'total_count': 2417, 'in_dict': {'MeSH': 1495, 'SNOMED CT': 1595}}

            for dict_name, term_count in result["in_dict"].items():
                # Если еще нет данных по словарю, создаем список
                if dict_name not in cnt_by_dict:
                    cnt_by_dict[dict_name] = []
                # Добавляем значение в список
                percent = term_count / result["total_count"] * 100
                cnt_by_dict[dict_name].append(percent)

        for dict_name, cnt_list in cnt_by_dict.items():
            ax2.plot(years, cnt_list, label=f"Доля терминов в {dict_name}", linestyle="--", linewidth=2)

        # Объединение легенд двух осей
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        plt.legend(
            lines_1 + lines_2,
            labels_1 + labels_2,
            loc="upper center",  # точка привязки легенды
            bbox_to_anchor=(0.5, -0.15),  # смещение вниз относительно графика
            ncol=3  # количество колонок в легенде
        )

        # Финальные действия и сохранение
        plt.tight_layout()
        plt.savefig(output_file_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        enable_logging()
