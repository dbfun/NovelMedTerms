from typing import TypedDict, List

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

from src.modules.module import ModuleInfo
from src.modules.ner.ner import TermDto
from src.modules.ner.transformer.transformer import Transformer


class DistilBertEntity(TypedDict):
    start: int
    end: int
    word: str
    entity_group: str
    score: float


class TransformerBiomedicalNerAll(Transformer):
    """
    Модуль для извлечения медицинских терминов с помощью трансформера.

    Карточка трансформера.
    ----------------------

    * Название: biomedical-ner-all
    * Архитектура: DistilBert (DistilBertForTokenClassification)
    * Особенности: настроена на заранее определенный список меток
    * Оценка выделения: 4/5
    * Оценка скорости: 1 сек
    * [HuggingFace](https://huggingface.co/d4data/biomedical-ner-all)
    * [Colab](https://colab.research.google.com/drive/1c9iFoqyMr2JjXBJaFR8na-ph3RSEMFy8#scrollTo=wpMJy2lzryaU)
    """

    def __init__(self, article_fields: list, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            article_fields: список полей из статьи для извлечения именованных сущностей.
            stopwords: список путей к файлам со списками стоп-слов.
        """

        super().__init__(article_fields, stopwords)
        tokenizer = AutoTokenizer.from_pretrained('d4data/biomedical-ner-all')
        model = AutoModelForTokenClassification.from_pretrained('d4data/biomedical-ner-all')
        self.pipe = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy='max')

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module='ner', type='transformer-biomedical-ner-all')

    def _extract_terms_from_text(self, text: str) -> list[TermDto]:
        ret: list[TermDto] = []

        # Пример entities:
        # [
        #     {'entity_group': 'Biological_structure', 'score': np.float32(0.99993896), 'word': 'lung', 'start': 27, 'end': 31}
        # ]

        entities: List[DistilBertEntity] = self.pipe(text)

        for ent in entities:
            self._add_term_if_valid(ret, ent, text)

        return ret

    def _add_term_if_valid(self, ret: list[TermDto], ent: DistilBertEntity, text: str):
        surface_form = text[ent['start']:ent['end']].strip()

        # Ранний пропуск, если является стоп-словом.
        if surface_form.lower() in self.stop_words:
            return

        term_feature = self._term_feature(surface_form)

        if self._should_skip(term_feature):
            return

        dto = TermDto(
            text=term_feature.lemmas,
            word_count=term_feature.word_count,
            start_pos=ent['start'],
            end_pos=ent['end'],
            surface_form=surface_form,
            pos_model=term_feature.pos_model,
            label=ent['entity_group'],
        )

        ret.append(dto)
