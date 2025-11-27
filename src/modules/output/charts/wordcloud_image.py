from pathlib import Path

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

    def __init__(self, session: Session, dictionaries: list[Dictionary]):
        self.session = session
        self.dictionaries = dictionaries

    def handle(self, min_word_count: int, max_terms: int, output_file_path: Path) -> None:
        """
        Запуск генерации

        Args:
            min_word_count: минимальное количества слов в термине
            max_terms: максимальное количество терминов в облаке слов
            output_file_path: путь к файлу для сохранения результатов
        """
        results = self._fetch_results(min_word_count, max_terms)
        self._generate_chart(results, max_terms, output_file_path)

    def _fetch_results(self, min_word_count: int, max_terms: int) -> list:
        """
        Получение данных из БД для построения облака слов.
        """

        params = {
            "min_word_count": min_word_count,
            "max_terms": max_terms,
        }
        join_tables = []
        where_cond = []

        # Проходим по списку словарей и подготавливаем части SQL для постановки в финальный запрос.
        for idx, dictionary in enumerate(self.dictionaries):
            # Для множественного объединения таблиц используем алиасы.
            table_alias = f"ref_{idx}"

            # Параметр для dictionary_id
            param_name = f"dict_id_{idx}"
            params[param_name] = dictionary.id

            join_tables.append(
                f"""
                LEFT JOIN term_dictionary_ref {table_alias}
                       ON {table_alias}.term_id = t.id
                      AND {table_alias}.dictionary_id = :{param_name}"""
            )
            where_cond.append(f"""
                AND {table_alias}.id IS NULL""")

        joins_sql = "\n".join(join_tables)
        where_sql = "\n".join(where_cond)

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
        plt.savefig(output_file_path, dpi=300)
        plt.close()

        enable_logging()
