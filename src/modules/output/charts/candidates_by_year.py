import csv
from pathlib import Path

import matplotlib.pyplot as plt
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.helper import disable_logging, enable_logging, all_years_range


class CandidatesByYear():
    """
    Траектория появления терминов-кандидатов по годам.
    """

    def __init__(self, session: Session, dpi: int, path_generator):
        self.session = session
        self.dpi = dpi
        self.path_generator = path_generator

    def handle(self) -> list[Path]:
        """
        Запуск генерации

        Returns:
            Список файлов
        """

        # Получение результатов
        results = self._fetch_results()

        # Все года исследований
        all_years = all_years_range(self.session)

        # Каталог для хранения результатов
        candidates_dir = self.path_generator("Траектория появления терминов-кандидатов")
        candidates_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        meta_description = []

        for term in results:
            # Генерация имен файлов
            filename = str(term['id']) + ".png"
            output_file_path = candidates_dir / filename
            output_files.append(output_file_path)

            # Создание графиков
            self._generate_chart(term, all_years, output_file_path)
            meta_description.append({
                **term,
                'filename': filename
            })

        self._save_meta(meta_description, candidates_dir / 'meta.csv')

        return output_files

    def _fetch_results(self) -> list[dict]:
        params = {}
        sql = f"""
            SELECT
            t.id, t.term_text, t.word_count,
            c.first_year, c.first_stable_year, c.last_year, c.max_consecutive, c.growth, c.total_mentions, c.counts_per_year
            FROM candidates c
            JOIN public.terms t ON t.id = c.term_id
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        return self.session.execute(text(sql), params).mappings().all()

    def _generate_chart(self, term: dict, all_years: range, output_file_path: Path) -> None:
        disable_logging()

        # Подготовка временного ряда
        years = list(all_years)
        counts = [term['counts_per_year'].get(str(y), 0) for y in years]

        # Построение графика
        plt.figure()
        plt.plot(years, counts, marker='o')

        self._draw_points(term)

        y_min = 0
        y_max = max(counts)
        plt.yticks(range(y_min, y_max + 1))

        plt.xticks(years[::2])

        plt.xlabel('Год')
        plt.ylabel('Количество упоминаний')
        plt.title(f'{term["term_text"]}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_file_path, dpi=self.dpi)
        plt.close()

        enable_logging()

    def _draw_points(self, term: dict):
        if term['first_year'] == term['first_stable_year']:
            plt.axvspan(
                term['first_year'] - 0.5,
                term['first_year'] + 0.5,
                color='yellow',
                alpha=0.2,
                label='Появление термина + минимальная устойчивость'
            )
            return

        plt.axvspan(
            term['first_year'] - 0.5,
            term['first_year'] + 0.5,
            color='green',
            alpha=0.2,
            label='Появление термина'
        )

        plt.axvspan(
            term['first_stable_year'] - 0.5,
            term['first_stable_year'] + 0.5,
            color='red',
            alpha=0.2,
            label='Минимальная устойчивость'
        )

    def _save_meta(self, meta_description: list[dict], csv_file: Path) -> None:
        columns = [
            'id',
            'filename',
            'term_text',
            'word_count',
            'first_year',
            'first_stable_year',
            'last_year',
            'max_consecutive',
            'growth',
            'total_mentions',
        ]

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Заголовок
            writer.writerow(columns)

            for item in meta_description:
                writer.writerow([item[col] for col in columns])
