import spacy
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from zshot import PipelineConfig
from zshot.linker import LinkerSMXM
from zshot.utils.data_models import Entity

from src.modules.module import ModuleInfo
from src.modules.ner.ner import TermDto
from src.modules.ner.transformer.transformer import Transformer


class TransformerOpenBioner(Transformer):
    """
    Модуль для извлечения медицинских терминов с помощью трансформера.

    Карточка трансформера.
    ----------------------

    * Название: OpenBioNER
    * Архитектура: BERT
    * Особенности: необходимо описывать сущности для извлечения (zshot)
    * Оценка выделения: 5/5
    * Оценка скорости: 25 сек
    * [HuggingFace](https://huggingface.co/disi-unibo-nlp/openbioner-base)
    * [Colab](https://colab.research.google.com/drive/1tqWKjX91PWttiMC6eHqZDSNefjSM3T4R#scrollTo=QkiWfpjj-ZRe)
    """

    def __init__(self, article_fields: list, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            article_fields: список полей из статьи для извлечения именованных сущностей.
            stopwords: список путей к файлам со списками стоп-слов.
        """

        super().__init__(article_fields, stopwords)

        # Список меток с описанием для извлечения по методике zero-shot.
        entities = self._fetch_entities()

        self.nlp = spacy.blank('en')
        nlp_config = PipelineConfig(
            linker=LinkerSMXM(model_name='disi-unibo-nlp/openbioner-base'),
            entities=entities,
            # Можно поменять на 'cuda'.
            device='cpu'
        )
        self.nlp.add_pipe('zshot', config=nlp_config, last=True)

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module='ner', type='transformer-open-bioner')

    def _extract_terms_from_text(self, text: str) -> list[TermDto]:
        ret: list[TermDto] = []

        doc: Doc = self.nlp(text)

        span: Span
        for span in doc.ents:
            self._add_term_if_valid(ret, span, text)

        self.logger.debug('Terms extracted')

        return ret

    def _add_term_if_valid(self, ret: list[TermDto], span: Span, text: str):
        # Есть проблема с NER: в конце может идти знак
        surface_form = text[span.start_char:span.end_char].strip(":,.; ")

        # Ранний пропуск, если является стоп-словом.
        if surface_form.lower() in self.stop_words:
            return

        term_feature = self._term_feature(surface_form)

        if self._should_skip(term_feature):
            return

        dto = TermDto(
            text=term_feature.lemmas,
            word_count=term_feature.word_count,
            start_pos=span.start_char,
            end_pos=span.end_char,
            surface_form=surface_form,
            pos_model=term_feature.pos_model,
            label=span.label_,
        )

        ret.append(dto)

    def _fetch_entities(self) -> list[Entity]:
        return [
            Entity(name='DISEASE',
                   description='A disease is a medical condition that disrupts normal bodily functions or structures, affecting various organs or systems, and leading to symptoms like muscle weakness, fatigue, stiffness, or cognitive impairment. Diseases can impact muscles, the nervous system, heart, eyes, and more, and may be chronic or acute, such as diabetes, cardiovascular or neurological disorders, and cancer-related conditions like lymphoblastic leukemia or lymphoma.',
                   vocabulary=None),
            Entity(name='DRUG',
                   description='A drug is a pharmacologically active substance used for the prevention, diagnosis, treatment, or relief of diseases and medical conditions. Drugs may include prescription medications, over-the-counter medicines, biologics, and therapeutic compounds with specific mechanisms of action.',
                   vocabulary=None),
            Entity(name='ANAT',
                   description='Anatomical structures of the body at different levels of organization, including organs, tissues, cells, and body parts. Examples include the heart, liver, skin, neurons, blood vessels, and anatomical regions.',
                   vocabulary=None),
            Entity(name='DEVICE',
                   description='Medical and laboratory devices used for diagnosis, monitoring, treatment, or research. Examples include implants, imaging equipment, surgical instruments, and diagnostic tools.',
                   vocabulary=None),
            Entity(name='LABPROC',
                   description='Laboratory procedures and tests used to analyze biological samples. Examples include blood tests, PCR, imaging assays, staining methods, and biochemical analyses.',
                   vocabulary=None),
            Entity(name='MEDPROC',
                   description='Medical procedures and interventions performed on patients for diagnostic or therapeutic purposes, including surgeries, therapies, injections, and clinical treatments.',
                   vocabulary=None),
            Entity(name='SCIPROC',
                   description='Scientific and experimental processes or methods used in research. This includes experimental protocols, analytical techniques, and methodological approaches in scientific studies.',
                   vocabulary=None),
            Entity(name='FINDING',
                   description='Clinical or experimental observations identified during examination, testing, or analysis. Findings may include symptoms, signs, imaging results, or abnormal measurements.',
                   vocabulary=None),
            Entity(name='PHYS',
                   description='Physiological processes and functions that occur within living organisms, including circulation, respiration, digestion, metabolism, and neural signaling.',
                   vocabulary=None),
            Entity(name='DISO',
                   description='Diseases, disorders, and pathological conditions that disrupt normal biological functions. This includes acute and chronic illnesses affecting physical or mental health.',
                   vocabulary=None),
            Entity(name='LIVB',
                   description='Living beings including microorganisms such as bacteria, viruses, fungi, and parasites. These entities may cause infectious diseases, participate in symbiosis, or be used as model organisms in biomedical and biological research.',
                   vocabulary=None),
            Entity(name='CHEMICAL',
                   description='Chemicals are substances that are composed of one or more elements, typically consisting of atoms bonded together by chemical bonds. They can be naturally occurring, such as vitamins or sterols, or synthesized, like alkylcarbazoles or tetrachlorodibenzo-p-dioxins (TCDD). Chemicals can also be modified or combined to form new compounds, such as esters or polymers.',
                   vocabulary=None),
            Entity(name='GENE',
                   description='Genes and genetic elements represented by DNA sequences that encode functional products such as proteins or RNA. These entities are responsible for heredity, regulation, and biological traits.',
                   vocabulary=None),
        ]
