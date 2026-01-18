import logging

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.helper import all_years_range
from src.modules.module import Module, ModuleInfo
from src.orm.models import Dictionary, Candidate


class EmergingTermDetection(Module):
    """
    Модуль поиска терминов-кандидатов.
    """

    def __init__(self, min_years_present: int | str, min_growth: int | float | str, min_total_mentions: int | str,
                 dictionaries: list[str]):
        """
        Args:
            min_years_present: минимальная устойчивость - количество лет подряд с ненулевой частотой
            min_growth: минимальный рост
            min_total_mentions: минимальное количество упоминаний
            dictionaries: список словарей
        """
        self.min_years_present = int(min_years_present)
        self.min_growth = float(min_growth)
        self.min_total_mentions = int(min_total_mentions)
        self.dictionaries = set(dictionaries)
        self.logger = logging.getLogger(EmergingTermDetection.info().name())

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="candidate", type="emerging-term-detection")

    def handle(self) -> None:
        from src.container import container

        with container.db_session() as session:
            dictionaries = self._load_dictionaries(session, self.dictionaries)

            # Получение терминов по годам. Пример:
            # [{'year': Decimal('2005'), 'term_id': 52224, 'count': 1}, ...]
            terms_count_by_year_rows = self._fetch_terms_count_by_year(session, dictionaries)

            # Агрегация. Пример:
            # {52224: {'term_id': 52224, 'counts_per_year': {2005: 1, 2021: 1}}, ... }
            terms_count_by_year = self._group_by_term(terms_count_by_year_rows)

            # Все года исследований
            all_years = all_years_range(session)

            # Сохранение в БД
            self._search_and_save(session, terms_count_by_year, all_years)

    def _fetch_terms_count_by_year(self, session: Session, dictionaries) -> list[dict]:
        params, joins_sql, where_sql = Dictionary.filter_not_in_dict(dictionaries)

        # Финальный SQL
        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM a.pubdate) AS year,       -- Год
                t.id                         AS term_id,    -- Термин
                COUNT(*)                     AS count       -- Количество
            FROM terms t
                JOIN article_term_annotations ann ON t.id = ann.term_id
                JOIN articles a ON a.id = ann.article_id
                {joins_sql}
            WHERE 1=1 
                {where_sql}
            GROUP BY year, t.id
            ORDER BY year
        """)

        # Оставлено для отладки
        # print(sql, params, sep="\n")

        return session.execute(sql, params).mappings().all()

    def _group_by_term(self, terms_count_by_year_rows: list[dict]) -> dict:
        terms_data_by_term = {}

        for row in terms_count_by_year_rows:
            term_id = row['term_id']
            year = int(row['year'])
            count = int(row['count'])

            if term_id not in terms_data_by_term:
                terms_data_by_term[term_id] = {
                    'term_id': term_id,
                    'counts_per_year': {}
                }

            terms_data_by_term[term_id]['counts_per_year'][year] = count

        return terms_data_by_term

    def _search_and_save(self, session: Session, terms_count_by_year: dict, all_years: range):
        self.logger.info(f"Выбрано терминов: {len(terms_count_by_year)}")

        candidate_cnt = 0
        for term_id, data in terms_count_by_year.items():
            counts = data['counts_per_year']
            counts_filled = [counts.get(y, 0) for y in all_years]

            sorted_years = sorted(counts.keys())

            # 1. Первый год встречаемости термина.
            first_year = sorted_years[0]

            # 2. Минимальная устойчивость.
            consecutive = 0
            max_consecutive = 0
            first_stable_year = None  # "Точка изменения"
            current_start_year = None

            for year, c in zip(all_years, counts_filled):
                if c > 0:
                    if consecutive == 0:
                        current_start_year = year  # начало новой последовательности
                    consecutive += 1
                    if consecutive > max_consecutive:
                        max_consecutive = consecutive
                        first_stable_year = current_start_year  # сохраняем год начала максимальной последовательности
                else:
                    consecutive = 0
                    current_start_year = None

            # Проверка минимальной устойчивости
            if max_consecutive < self.min_years_present:
                continue

            # 3. Рост встречаемости
            first_count = counts[first_year]
            max_count = max(counts.values())
            growth = max_count / first_count if first_count > 0 else 0
            if growth < self.min_growth:
                continue

            # 4. Общее количество упоминаний
            total_mentions = sum(counts.values())

            if total_mentions < self.min_total_mentions:
                continue

            # Если все проверки пройдены, то добавляем в БД
            candidate = Candidate(
                term_id=term_id,
                first_year=first_year,
                last_year=sorted_years[-1],
                first_stable_year=first_stable_year,
                max_consecutive=max_consecutive,
                growth=growth,
                total_mentions=total_mentions,
                counts_per_year=data['counts_per_year']
            )

            stmt = insert(Candidate).values(
                term_id=candidate.term_id,
                first_year=candidate.first_year,
                last_year=candidate.last_year,
                first_stable_year=candidate.first_stable_year,
                max_consecutive=candidate.max_consecutive,
                growth=candidate.growth,
                total_mentions=candidate.total_mentions,
                counts_per_year=candidate.counts_per_year,
            ).on_conflict_do_nothing(index_elements=['term_id'])

            candidate_cnt += 1

            session.execute(stmt)

        session.commit()

        self.logger.info(f"Найдено терминов-кандидатов: {candidate_cnt}")
