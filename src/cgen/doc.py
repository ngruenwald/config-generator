from typing import Union
from dataclasses import dataclass


@dataclass
class DocEntry:
    xpath: str
    description: str
    required: bool
    default: Union[float, str, int]


def create_render_data(docs: list[DocEntry]) -> dict:
    sections = {}
    for d in docs:
        s = d.xpath.split("/")
        if len(s) < 2:
            if s[0] not in sections.keys():
                sections[s[0]] = []
            sections[s[0]].append(d)
        else:
            if s[1] not in sections.keys():
                sections[s[1]] = []
            sections[s[1]].append(d)
    return dict(sections=sections)
