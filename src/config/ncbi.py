import os


class NcbiConfig:

    @staticmethod
    def email() -> str:
        """Email адрес для запросов в PubMed. Регистрация не требуется. Нужен для идентификации запросов"""
        return os.environ.get('NCBI_EMAIL')

    @staticmethod
    def api_key() -> str:
        """
        Не обязательно. API ключ нужен для увеличения лимитов.
        Ключ можно получить тут: https://account.ncbi.nlm.nih.gov/settings/

        E-utils users are allowed 3 requests/second without an API key.
        Create an API key to increase your e-utils limit to 10 requests/second.
        """
        return os.environ.get('NCBI_API_KEY')
