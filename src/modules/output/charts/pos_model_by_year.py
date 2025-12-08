from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from src.helper import disable_logging, enable_logging


class PosModelByYear():
    """
    Динамика распределения POS-структур по годам, кроме униграмм.
    """

    def __init__(self, session: Session, path_generator):
        self.session = session
        self.path_generator = path_generator

    def handle(self, n_top: int) -> list[Path]:
        """
        Запуск генерации

        Args:
            n_top: TOP-n POS-структур (количество популярных структурных моделей на графике)
            output_file_1: путь к файлу для сохранения результатов
        """

        # Получение данных
        total_pos_models_by_year = self._fetch_total_pos_models_by_year()
        top_pos_models = self._fetch_top_pos_models(n_top)
        pos_models_by_year = self._fetch_pos_models_by_year(top_pos_models)

        # Генерация имен файлов
        file_pos_model_by_year_abs = self.path_generator("pos_model_by_year_abs.png")
        file_pos_model_by_year_rel = self.path_generator("pos_model_by_year_rel.png")

        # Создание графиков
        self._generate_chart_pos_model_by_year_abs(
            pos_models_by_year,
            "Динамика распределения POS-структур по годам, кроме униграмм",
            file_pos_model_by_year_abs
        )
        self._generate_chart_pos_model_by_year_rel(
            total_pos_models_by_year,
            pos_models_by_year,
            "Доля POS-структур по годам, кроме униграмм",
            file_pos_model_by_year_rel
        )

        return [file_pos_model_by_year_abs, file_pos_model_by_year_rel]

    def _fetch_total_pos_models_by_year(self) -> list:
        params = {}
        # Финальный SQL
        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM a.pubdate) AS year,       -- Год
                COUNT(*)                     AS count       -- Количество
            FROM terms t
                JOIN article_term_annotations ann ON t.id = ann.term_id
                JOIN articles a ON a.id = ann.article_id
            GROUP BY year
        """)

        # Оставлено для отладки
        # print(sql, params, sep="\n")

        return self.session.execute(sql, params).mappings().all()

    def _fetch_top_pos_models(self, n_top: int) -> list:
        params = {"n_top": n_top}
        # Финальный SQL
        sql = f"""
            SELECT pos_model, COUNT(*) AS count
            FROM terms
            WHERE word_count > 1
            GROUP BY pos_model
            ORDER BY COUNT(*) DESC
            LIMIT :n_top
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        return self.session.execute(text(sql), params).mappings().all()

    def _fetch_pos_models_by_year(self, top_pos_models: list) -> list:
        params = {
            "top_pos_models": [it["pos_model"] for it in top_pos_models]
        }

        # Финальный SQL
        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM a.pubdate) AS year,       -- Год
                t.pos_model                  AS pos_model,  -- Схема
                COUNT(*)                     AS count       -- Количество
            FROM terms t
                JOIN article_term_annotations ann ON t.id = ann.term_id
                JOIN articles a ON a.id = ann.article_id
            WHERE t.pos_model IN :top_pos_models
            GROUP BY year, pos_model
        """).bindparams(bindparam("top_pos_models", expanding=True))

        # Оставлено для отладки
        # print(sql, params, sep="\n")

        return self.session.execute(sql, params).mappings().all()

    def _generate_chart_pos_model_by_year_abs(self, pos_models_by_year: list, title: str,
                                              output_file_path: Path) -> None:
        disable_logging()

        # DataFrame
        df = pd.DataFrame(pos_models_by_year)

        # Перевод года в int
        df["year"] = df["year"].astype(int)

        # Pivot table
        df_pivot = df.pivot_table(index="year", columns="pos_model", values="count", fill_value=0)

        # Сортировка POS-моделей по сумме всех значений (по убыванию)
        sorted_cols = df_pivot.sum(axis=0).sort_values(ascending=False).index
        df_pivot = df_pivot[sorted_cols]

        # Построение графика
        ax = df_pivot.plot(kind="area", stacked=True, figsize=(12, 6))

        # Настройка оси X на целые годы
        ax.set_xticks(df_pivot.index)
        ax.set_xticklabels(df_pivot.index.astype(int))

        plt.title(title)
        plt.xlabel("Год")
        plt.ylabel("Количество")
        plt.legend(title="POS-модель", bbox_to_anchor=(1.05, 1), loc="upper left")

        # Финальные действия и сохранение
        plt.tight_layout()
        plt.savefig(output_file_path, dpi=300, bbox_inches="tight")
        plt.close()

        enable_logging()

    def _generate_chart_pos_model_by_year_rel(self, total_pos_models_by_year: list, pos_models_by_year: list,
                                              title: str, output_file_path: Path):
        disable_logging()

        # Создаём DataFrames
        df_pos = pd.DataFrame(pos_models_by_year)
        df_total = pd.DataFrame(total_pos_models_by_year)

        # Преобразуем year в int
        df_pos["year"] = df_pos["year"].astype(int)
        df_total["year"] = df_total["year"].astype(int)

        # Pivot table: строки - годы, колонки - POS-модели
        df_pivot = df_pos.pivot_table(index="year", columns="pos_model", values="count", fill_value=0)

        # Объединяем с total для расчета процентов
        df_pivot = df_pivot.join(df_total.set_index("year"))

        # Делим на total и переводим в проценты
        df_percent = df_pivot.div(df_pivot["count"], axis=0) * 100
        df_percent = df_percent.drop(columns="count")  # убираем колонку total

        # Сортируем POS-модели по сумме всех значений (по убыванию)
        sorted_cols = df_percent.sum(axis=0).sort_values(ascending=False).index
        df_percent = df_percent[sorted_cols]

        # Строим график с линиями для каждой POS-модели
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
        plt.savefig(output_file_path, dpi=300, bbox_inches="tight")
        plt.close()

        enable_logging()
