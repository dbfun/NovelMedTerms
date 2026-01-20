from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import pearsonr, kendalltau
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.helper import disable_logging, enable_logging
from src.orm.models import Dictionary


class VocabularyCoverage():
    """
    Генерация графика "Количество терминов в PubMed и их покрытие словарями"
    """

    def __init__(self, session: Session, dpi: int, dictionaries: list[Dictionary], path_generator):
        self.session = session
        self.dpi = dpi
        self.dictionaries = dictionaries
        self.path_generator = path_generator

    def handle(self) -> list[Path]:
        """
        Запуск генерации
        """
        results = self._fetch_results()

        # Генерация имен файлов
        output_file_path = self.path_generator("Количество извлеченных терминов их покрытие словарями.png")
        output_file_path_facet = self.path_generator("Динамика покрытия извлеченных терминов словарями.png")

        self._generate_chart(results, output_file_path)
        self._generate_chart_facet(results, output_file_path_facet)

        return [output_file_path]

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
                "year": int(row.year),
                "total_count": row.total_count,
                "in_dict": {}
            }
            for table_alias, dict_name in dict_column_to_dict_name_map.items():
                # Создаем словарь в формате "название словаря": "количество терминов"
                result["in_dict"][dict_name] = row[table_alias]

            ret.append(result)

        return ret

    def _generate_chart(self, results: list[dict], output_file_path: Path) -> None:
        # Пример results - с разбивкой по годам:
        # [{'year': 2005, 'total_count': 71, 'in_dict': {'CUI': 55, 'MeSH': 45, 'SNOMED CT': 54, 'DrugBank': 11, 'GO': 26, 'HPO': 40, 'ICD10': 33, 'NCI': 49, 'WHO': 26}}, ... ]

        disable_logging()

        years = [d["year"] for d in results]
        total = [d["total_count"] for d in results]

        plt.figure(figsize=(12, 6))
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

    def _generate_chart_facet(self, results: list[dict], output_file_path: Path) -> None:
        disable_logging()

        df = self._prepare_df(results)

        g = sns.FacetGrid(
            df,
            col="dict_name",
            col_wrap=3,
            height=3.5,
            sharey=False
        )

        # Основная линия (проценты по годам)
        g.map_dataframe(
            sns.scatterplot,
            x="year",
            y="percent",
            marker="o"
        )

        g.set_axis_labels("Год", "Покрытие, %")
        g.set_titles("{col_name}")

        # Добавляем регрессию и статистику
        self._add_trend_and_stats(g, df)

        plt.tight_layout()
        plt.savefig(output_file_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        enable_logging()

    def _prepare_df(self, results: list[dict]) -> pd.DataFrame:
        rows = []

        for result in results:
            year = int(result["year"])
            total = result["total_count"]

            if total == 0:
                continue

            for dict_name, term_count in result["in_dict"].items():
                percent = term_count / total * 100
                rows.append({
                    "year": year,
                    "dict_name": dict_name,
                    "percent": percent,
                })

        df = pd.DataFrame(rows)
        return df

    def _add_trend_and_stats(self, g: sns.FacetGrid, df: pd.DataFrame) -> None:
        for ax, dict_name in zip(g.axes.flatten(), g.col_names):
            df_dict = df[df["dict_name"] == dict_name]

            if len(df_dict) < 2:
                continue

            # Линейная регрессия: percent ~ year
            X = sm.add_constant(df_dict["year"])
            y = df_dict["percent"]
            model = sm.OLS(y, X).fit()

            slope = model.params["year"]
            intercept = model.params["const"]

            # Корреляция Пирсона
            r, _ = pearsonr(df_dict["year"], df_dict["percent"])

            # Манн–Кендалл
            tau, p_value = kendalltau(df_dict["year"], df_dict["percent"])

            # Цвет по значимости
            color = "red" if p_value < 0.05 else "gray"

            # Линия регрессии
            years_sorted = df_dict["year"].sort_values()
            ax.plot(
                years_sorted,
                intercept + slope * years_sorted,
                color=color,
                linewidth=2
            )

            # Текст со статистикой
            ax.text(
                0.05,
                0.95,
                f"y={slope:.3f}x+{intercept:.2f}\n"
                f"r={r:.2f}\n"
                f"τ={tau:.2f}\n"
                f"p={p_value:.3f}",
                transform=ax.transAxes,
                verticalalignment="top",
                fontsize=8,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    alpha=0.6
                ),
                color=color
            )
