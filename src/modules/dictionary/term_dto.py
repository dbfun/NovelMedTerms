from dataclasses import dataclass


@dataclass
class TermDTO:
    """
    Data Transfer Object для терминов из словаря
    """
    ref_id: str
