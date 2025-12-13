from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import pearsonr, kendalltau
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from src.helper import disable_logging, enable_logging
from src.orm.models import Dictionary


class PosModelByYear():
    """
    Динамика распределения POS-структур по годам, кроме униграмм.
    """

    def __init__(self, session: Session, dpi: int, dictionaries: list[Dictionary], path_generator):
        self.session = session
        self.dpi = dpi
        self.dictionaries = dictionaries
        self.path_generator = path_generator

    def handle(self, n_top: int) -> list[Path]:
        """
        Запуск генерации

        Args:
            n_top: ТОП-n POS-структур (количество популярных структурных моделей на графике)
            output_file_1: путь к файлу для сохранения результатов
        """

        # Получение данных
        total_pos_models_by_year = self._fetch_total_pos_models_by_year()
        top_pos_models = self._fetch_top_pos_models(n_top)
        pos_models_by_year = self._fetch_pos_models_by_year(top_pos_models)

        # Генерация имен файлов
        file_pos_model_by_year_abs = self.path_generator("pos_model_by_year_abs.png")
        file_pos_model_by_year_rel = self.path_generator("pos_model_by_year_rel.png")
        file_pos_model_by_year_facet = self.path_generator("pos_model_by_year_facet.png")

        # Создание графиков
        self._generate_chart_pos_model_by_year_abs(
            pos_models_by_year,
            total_pos_models_by_year,
            "Динамика распределения POS-структур по годам, кроме униграмм",
            file_pos_model_by_year_abs
        )
        self._generate_chart_pos_model_by_year_rel(
            pos_models_by_year,
            total_pos_models_by_year,
            "Доля POS-структур по годам, кроме униграмм",
            file_pos_model_by_year_rel
        )

        self._generate_chart_pos_model_by_year_facet(
            pos_models_by_year,
            total_pos_models_by_year,
            "Динамика POS-структур по годам, кроме униграмм",
            file_pos_model_by_year_facet
        )

        return [file_pos_model_by_year_abs, file_pos_model_by_year_rel, file_pos_model_by_year_facet]

    def _fetch_total_pos_models_by_year(self) -> list:
        params, joins_sql, where_sql = Dictionary.filter_not_in_dict(self.dictionaries)

        # Финальный SQL
        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM a.pubdate) AS year,       -- Год
                COUNT(*)                     AS count       -- Количество
            FROM terms t
                JOIN article_term_annotations ann ON t.id = ann.term_id
                JOIN articles a ON a.id = ann.article_id
                {joins_sql}
            WHERE 1=1 
                {where_sql}
            GROUP BY year
        """)

        # Оставлено для отладки
        # print(sql, params, sep="\n")

        return self.session.execute(sql, params).mappings().all()

    def _fetch_top_pos_models(self, n_top: int) -> list:
        params, joins_sql, where_sql = Dictionary.filter_not_in_dict(self.dictionaries)
        params.update({"n_top": n_top})

        # Финальный SQL
        sql = f"""
            SELECT pos_model, COUNT(*) AS count
            FROM terms t
                {joins_sql}
            WHERE word_count > 1
                {where_sql}
            GROUP BY pos_model
            ORDER BY COUNT(*) DESC
            LIMIT :n_top
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        return self.session.execute(text(sql), params).mappings().all()

    def _fetch_pos_models_by_year(self, top_pos_models: list) -> list:
        params, joins_sql, where_sql = Dictionary.filter_not_in_dict(self.dictionaries)
        params.update({"top_pos_models": [it["pos_model"] for it in top_pos_models]})

        # Финальный SQL
        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM a.pubdate) AS year,       -- Год
                t.pos_model                  AS pos_model,  -- Схема
                COUNT(*)                     AS count       -- Количество
            FROM terms t
                JOIN article_term_annotations ann ON t.id = ann.term_id
                JOIN articles a ON a.id = ann.article_id
                {joins_sql}
            WHERE t.pos_model IN :top_pos_models
                {where_sql}
            GROUP BY year, pos_model
        """).bindparams(bindparam("top_pos_models", expanding=True))

        # Оставлено для отладки
        # print(sql, params, sep="\n")

        return self.session.execute(sql, params).mappings().all()

    def _generate_chart_pos_model_by_year_abs(self, pos_models_by_year: list, total_pos_models_by_year: list,
                                              title: str, output_file_path: Path) -> None:
        disable_logging()

        # DataFrame с POS-моделями
        df = pd.DataFrame(pos_models_by_year)
        df["year"] = df["year"].astype(int)

        # Pivot table
        df_pivot = df.pivot_table(index="year", columns="pos_model", values="count", fill_value=0)

        # Сортировка POS-моделей по сумме всех значений (по убыванию)
        sorted_cols = df_pivot.sum(axis=0).sort_values(ascending=False).index
        df_pivot = df_pivot[sorted_cols]

        # --- total_pos_models_by_year ---
        df_total = pd.DataFrame(total_pos_models_by_year)
        df_total["year"] = df_total["year"].astype(int)
        df_total = df_total.set_index("year").sort_index()

        # Построение stacked area chart
        ax = df_pivot.plot(kind="area", stacked=True, figsize=(12, 6))

        # Добавление линии TOTAL
        ax.plot(df_total.index, df_total["count"], linewidth=2.5, color="gray", label="Итого по году")

        # Установка подписей и позиций делений (меток) на оси OX
        ax.set_xticks(df_pivot.index.union(df_total.index))
        ax.set_xticklabels(ax.get_xticks().astype(int))

        # Расширение пределов OY, чтобы линия TOTAL не вышла за график
        max_area_value = df_pivot.sum(axis=1).max()
        max_total_value = df_total["count"].max()
        ax.set_ylim(0, max(max_area_value, max_total_value) * 1.05)

        # Названия
        plt.title(title)
        plt.xlabel("Год")
        plt.ylabel("Количество")

        # Легенда
        plt.legend(title="POS-структура / Итого", bbox_to_anchor=(1.05, 1), loc="upper left")

        # Сохранение
        plt.tight_layout()
        plt.savefig(output_file_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        enable_logging()

    def _generate_chart_pos_model_by_year_rel(self, pos_models_by_year: list, total_pos_models_by_year: list,
                                              title: str, output_file_path: Path):
        disable_logging()

        # Создание DataFrames
        df_pos = pd.DataFrame(pos_models_by_year)
        df_total = pd.DataFrame(total_pos_models_by_year)

        # Преобразование year в int
        df_pos["year"] = df_pos["year"].astype(int)
        df_total["year"] = df_total["year"].astype(int)

        # Pivot table: строки - годы, колонки - POS-модели
        df_pivot = df_pos.pivot_table(index="year", columns="pos_model", values="count", fill_value=0)

        # Объединение с total для расчета процентов
        df_pivot = df_pivot.join(df_total.set_index("year"))

        # Деление на total и перевод в проценты
        df_percent = df_pivot.div(df_pivot["count"], axis=0) * 100
        df_percent = df_percent.drop(columns="count")  # убираем колонку total

        # Сортировка POS-модели по сумме всех значений (по убыванию)
        sorted_cols = df_percent.sum(axis=0).sort_values(ascending=False).index
        df_percent = df_percent[sorted_cols]

        # Построение графика с линиями для каждой POS-модели
        ax = df_percent.plot(kind="line", figsize=(12, 6))

        # Настройка оси X на целые годы
        ax.set_xticks(df_percent.index)
        ax.set_xticklabels(df_percent.index.astype(int))

        plt.title(title)
        plt.xlabel("Год")
        plt.ylabel("Доля, %")
        plt.legend(title="POS-модель", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True)

        # Финальные действия и сохранение
        plt.tight_layout()
        plt.savefig(output_file_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        enable_logging()

    def _generate_chart_pos_model_by_year_facet(self, pos_models_by_year: list, total_pos_models_by_year: list,
                                                title: str, output_file_path: Path):
        """
        Динамика POS-структур по годам, кроме униграмм

        Коэффициент корреляции Пирсона (r)
        ----------------------------------

        Показывает линейную зависимость между двумя переменными.
            * r = 0.85 - сильная положительная линейная связь
            * r = -0.4 - умеренная отрицательная линейная связь

        Коэффициент Манна-Кендалла (τ, tau)
        -----------------------------------

        Непараметрический тест тренда во времени.

            * τ=1 - идеальный возрастающий тренд
            * τ=−1 - идеальный убывающий тренд
            * τ=0 - тренд отсутствует

        p-value для теста Манна–Кендалла показывает, насколько тренд статистически значим.

        * p < 0.05 - тренд значимый
        * p >= 0.05 - тренда нет.
        """
        disable_logging()

        # Подготовка данных
        df = pd.DataFrame(pos_models_by_year)
        df["year"] = df["year"].astype(int)
        df["count"] = df["count"].astype(int)

        total_df = pd.DataFrame(total_pos_models_by_year)
        total_df["year"] = total_df["year"].astype(int)
        total_df["count"] = total_df["count"].astype(int)

        # Объединяем с общим количеством, чтобы посчитать %
        df = df.merge(total_df, on="year", suffixes=("", "_total"))
        # Расчет процентов
        df["relative"] = df["count"] / df["count_total"] * 100

        # Оставлено для отладки
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(df)

        # Список всех POS-моделей (топовые уже отфильтрованы)
        top_models = df["pos_model"].unique().tolist()

        # Small multiples с Seaborn
        g = sns.FacetGrid(df, col="pos_model", col_wrap=5, height=3.5, sharey=False)
        g.map_dataframe(sns.scatterplot, x="year", y="relative")

        # Добавляем регрессию и статистику для каждой модели
        for ax, model in zip(g.axes.flatten(), top_models):
            df_model = df[df["pos_model"] == model]
            if len(df_model) < 2:
                continue  # мало данных для регрессии

            # Линейная регрессия: relative ~ year
            X = sm.add_constant(df_model["year"])
            y = df_model["relative"]
            model_fit = sm.OLS(y, X).fit()
            slope = model_fit.params["year"]
            intercept = model_fit.params["const"]

            # Коэффициент корреляции Пирсона
            r, _ = pearsonr(df_model["year"], df_model["relative"])

            # Тест Манна–Кендалла
            tau, p_value = kendalltau(df_model["year"], df_model["relative"])

            # Цвет линии и текста по значимости
            color = "red" if p_value < 0.05 else "gray"

            # Добавляем линию регрессии
            ax.plot(df_model["year"], intercept + slope * df_model["year"], color=color)

            # Подписываем параметры на графике (с p-value)
            ax.text(
                0.05, 0.95,
                f"y={slope:.4f}x+{intercept:.4f}\n"
                f"r={r:.2f}\n"
                f"τ={tau:.2f}\n"
                f"p={p_value:.3f}",
                transform=ax.transAxes,
                verticalalignment="top",
                fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.5),
                color=color
            )

        g.figure.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.subplots_adjust(top=0.90)
        plt.savefig(output_file_path, dpi=self.dpi)
        plt.close()

        enable_logging()
