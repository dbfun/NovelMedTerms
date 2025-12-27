from typing import TypedDict, List

from gliner import GLiNER

from src.modules.module import ModuleInfo
from src.modules.ner.ner import TermDto
from src.modules.ner.transformer.transformer import Transformer


class GlinerEntity(TypedDict):
    start: int
    end: int
    text: str
    label: str
    score: float


class TransformerGlinerBiomedBiLargeV1(Transformer):
    """
    Модуль для извлечения медицинских терминов с помощью трансформера.

    Карточка трансформера.
    ----------------------

    * Название: GLiNER-BioMed
    * Архитектура: GLiNER
    * Особенности: есть small и large модели
    * Оценка выделения: 5/5
    * Оценка скорости: 8 сек
    * [HuggingFace](https://huggingface.co/Ihor/gliner-biomed-large-v1.0)
    * [Colab](https://colab.research.google.com/drive/1fQfBIRLOVrnvgfbRfo8ylpmeKtKiA6Aj#scrollTo=13WHlnTXBg4k)
    """

    def __init__(self, labels: list, article_fields: list, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            labels: список меток для извлечения, например ['Disease', 'Drug', 'Anatomy', 'Medical device']
            article_fields: список полей из статьи для извлечения именованных сущностей.
            stopwords: список путей к файлам со списками стоп-слов.
        """

        # Список полей
        if not labels:
            raise ValueError('Список меток не может быть пустым')

        super().__init__(article_fields, stopwords)
        self.model = GLiNER.from_pretrained('Ihor/gliner-biomed-bi-large-v1.0')
        self.labels = labels

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module='ner', type='transformer-gliner-biomed-bi-large-v1.0')

    def _extract_terms_from_text(self, text: str) -> list[TermDto]:
        ret: list[TermDto] = []

        # Пример entities:
        # [
        #     {'start': 0, 'end': 14, 'text': 'Calcifications', 'label': 'Pathological condition', 'score': 0.8707718849182129}
        # ]
        entities: List[GlinerEntity] = self.model.predict_entities(text, self.labels, threshold=0.5)

        for ent in entities:
            self._add_term_if_valid(ret, ent, text)

        return ret

    def _add_term_if_valid(self, ret: list[TermDto], ent: GlinerEntity, text: str):
        surface_form=text[ent['start']:ent['end']].strip()

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
            label=ent['label'],
        )

        ret.append(dto)
