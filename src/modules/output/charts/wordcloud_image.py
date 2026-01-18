from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from sqlalchemy import text
from sqlalchemy.orm import Session
from wordcloud import WordCloud

from src.helper import disable_logging, enable_logging
from src.orm.models import Dictionary


class WordcloudImage():
    """
    Генерация облака слов.
    """

    def __init__(self, session: Session, dpi: int, dictionaries: list[Dictionary], path_generator):
        self.session = session
        self.dpi = dpi
        self.dictionaries = dictionaries
        self.path_generator = path_generator

    def handle(self, min_word_count: int, max_terms: int) -> list[Path]:
        """
        Запуск генерации

        Args:
            min_word_count: минимальное количества слов в термине
            max_terms: максимальное количество терминов в облаке слов
        Returns:
            Список файлов
        """

        # Генерация имен файлов
        wordcloud_img_file = self.path_generator("Облако терминов.png")
        wordcloud_csv_file = self.path_generator("Облако терминов.csv")

        # Получение результатов
        results = self._fetch_results(min_word_count, max_terms)

        # WordCloud имеет дефолтное значение max_words=200, поэтому передаем реальное значение для
        # случая, когда терминов более 200.
        self._generate_chart(results, max_terms, wordcloud_img_file)

        # Не передаем max_words, это не нужно
        self._generate_csv(results, wordcloud_csv_file)

        return [wordcloud_img_file, wordcloud_csv_file]

    def _fetch_results(self, min_word_count: int, max_terms: int) -> list:
        """
        Получение данных из БД для построения облака слов.
        """
        params, joins_sql, where_sql = Dictionary.filter_not_in_dict(self.dictionaries)
        params.update({
            "min_word_count": min_word_count,
            "max_terms": max_terms,
        })

        # Финальный SQL
        sql = f"""
            SELECT term_text, count(*) as count
            FROM terms t
                JOIN article_term_annotations ann on t.id = ann.term_id
                JOIN articles a on a.id = ann.article_id
                {joins_sql}
            WHERE
                word_count >= :min_word_count
                {where_sql}
            GROUP BY term_text
            ORDER BY count DESC, term_text
            LIMIT :max_terms
        """

        # Оставлено для отладки
        # print(text(sql), params, sep="\n")

        return self.session.execute(text(sql), params).mappings().all()

    def _generate_chart(self, results: list, max_terms: int, output_file_path: Path) -> None:
        freqs = {}

        for result in results:
            # Структура result: {'term_text': 'tomography ct', 'count': 82}
            freqs[result["term_text"]] = result["count"]

        disable_logging()

        wc = WordCloud(width=1200, height=900, background_color="white", max_words=max_terms).generate_from_frequencies(
            freqs)
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(output_file_path, dpi=self.dpi)
        plt.close()

        enable_logging()

    def _generate_csv(self, results: list, output_file_path: Path) -> None:
        df = pd.DataFrame(results)
        df.sort_values("count", ascending=False).to_csv(
            output_file_path,
            index=False,
            encoding="utf-8"
        )
