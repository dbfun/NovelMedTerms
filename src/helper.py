import logging

old_level = None


def disable_logging() -> None:
    """
    Временное отключение журналирования.
    Полезно при вызове библиотек (matplotlib.pyplot), которые избыточно журналируют.
    """
    global old_level
    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(logging.CRITICAL)


def enable_logging() -> None:
    """
    Возврат журналирования к прошлому состоянию
    """
    global old_level
    logger = logging.getLogger()
    logger.setLevel(old_level)
