
from dataclasses import asdict, dataclass


@dataclass
class Record:
    page_title: str
    guide_section: str
    key_concept: str
    main_symbol: str
    example_response: str
    source_url: str

    def to_dict(self) -> dict:
        return asdict(self)
