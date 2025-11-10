"""
Инициализация проекта.
"""
import os
from pathlib import Path

import nltk
import requests
from dotenv import load_dotenv
from sqlalchemy import inspect

from src.container import container
from src.orm import models
from src.orm.database import BaseModel

_ = models  # Защита от удаления линтером.


def drop_tables():
    engine = container.db_engine()
    BaseModel.metadata.drop_all(engine)
    print("✅ Таблицы удалены")


def create_tables():
    engine = container.db_engine()
    BaseModel.metadata.create_all(engine)
    print("✅ Таблицы созданы")


def check_tables():
    engine = container.db_engine()

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected = set(BaseModel.metadata.tables.keys())
    missing = expected - set(tables)
    if missing:
        print(f"⚠️ Отсутствуют таблицы: {missing}")
    else:
        print("✅ Все таблицы успешно созданы:")
        for table in tables:
            print(f" - {table}")


def load_dictionaries():
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)


def load_umls_dictionaries():
    """
    Скачивает словарь UMLS в виде ZIP-файла и преобразует его в SQLite3 базу данных.

    По сути делает "Installation", который описан в документации pymedtermino2.

    Документация pymedtermino2: https://owlready2.readthedocs.io/en/latest/pymedtermino2.html
    """

    def download(zip_path: Path):
        api_key = os.environ["UMLS_API_KEY"]
        url = f"https://uts-ws.nlm.nih.gov/download?url=https://download.nlm.nih.gov/umls/kss/2025AA/umls-2025AA-full.zip&apiKey={api_key}"
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)

    def convert_to_sqlite3(zip_path: Path, sqlite_path: Path):
        from owlready2.pymedtermino2.umls import default_world, import_umls
        default_world.set_backend(filename=sqlite_path)
        # Доступные варианты - взял из сорцов owlready2:
        # ['SRC', 'SNOMEDCT_US', 'ICD10', 'ICPC', 'MDR', 'LNC', 'MSH', 'AIR', 'ALT', 'AOD', 'AOT', 'ATC', 'BI', 'CCC', 'CCPSS', 'CCS', 'CCS_10', 'CDT', 'CHV', 'COSTAR', 'CPM', 'CPT', 'CSP', 'CST', 'CVX', 'DDB', 'DRUGBANK', 'DSM-5', 'DXP', 'FMA', 'GO', 'GS', 'HCDT', 'HCPCS', 'HCPT', 'HGNC', 'HL7V2.5', 'HL7V3.0', 'HPO', 'ICD10AE', 'ICD10AM', 'ICD10AMAE', 'ICD10CM', 'ICD10PCS', 'ICD9CM', 'ICF', 'ICF-CY', 'ICNP', 'ICPC2EENG', 'ICPC2ICD10ENG', 'ICPC2P', 'JABL', 'LCH', 'LCH_NW', 'MCM', 'MED-RT', 'MEDCIN', 'MEDLINEPLUS', 'MMSL', 'MMX', 'MTH', 'MTHCMSFRF', 'MTHHH', 'MTHICD9', 'MTHICPC2EAE', 'MTHICPC2ICD10AE', 'MTHMST', 'MTHSPL', 'MVX', 'NANDA-I', 'NCBI', 'NCI', 'NCI_BRIDG', 'NCI_BioC', 'NCI_CDC', 'NCI_CDISC', 'NCI_CDISC-GLOSS', 'NCI_CRCH', 'NCI_CTCAE', 'NCI_CTCAE_3', 'NCI_CTCAE_5', 'NCI_CTEP-SDC', 'NCI_CTRP', 'NCI_CareLex', 'NCI_DCP', 'NCI_DICOM', 'NCI_DTP', 'NCI_FDA', 'NCI_GAIA', 'NCI_GENC', 'NCI_ICH', 'NCI_JAX', 'NCI_KEGG', 'NCI_NCI-GLOSS', 'NCI_NCI-HGNC', 'NCI_NCI-HL7', 'NCI_NCPDP', 'NCI_NICHD', 'NCI_PI-RADS', 'NCI_PID', 'NCI_RENI', 'NCI_UCUM', 'NCI_ZFin', 'NDDF', 'NDFRT', 'NDFRT_FDASPL', 'NDFRT_FMTSME', 'NEU', 'NIC', 'NOC', 'NUCCPT', 'OMIM', 'OMS', 'PCDS', 'PDQ', 'PNDS', 'PPAC', 'PSY', 'QMR', 'RAM', 'RCD', 'RCDAE', 'RCDSA', 'RCDSY', 'RXNORM', 'SNM', 'SNMI', 'SNOMEDCT_VET', 'SOP', 'SPN', 'ULT', 'UMD', 'USP', 'USPMG', 'UWDA', 'VANDF', 'WHO']
        # MSH = MeSH
        import_umls(zip_path, terminologies=["ICD10", "SNOMEDCT_US", "CUI", "WHO", "MSH"])
        default_world.save()

    output_dir = Path("resources/dictionaries/umls")
    zip_path = output_dir / "umls-full.zip"
    sqlite_path = output_dir / "pym.sqlite3"

    if zip_path.exists():
        print(f"📥 UMLS уже скачан, пропускаю")
    else:
        print(f"📥 Скачивание UMLS ...")
        download(zip_path)
        print(f"✅ Файл скачан: {zip_path}")

    if sqlite_path.exists():
        print(f"📂 UMLS уже преобразован, пропускаю")
    else:
        print("📂 Преобразование UMLS...")
        convert_to_sqlite3(zip_path, sqlite_path)
        print(f"✅ Преобразование завершено")


if __name__ == "__main__":
    load_dotenv()
    assert os.environ["APP_ENV"] == "production"

    drop_tables()
    create_tables()
    check_tables()
    load_dictionaries()
    load_umls_dictionaries()
