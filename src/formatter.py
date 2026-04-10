"""Modul formatting output final compiled."""

from __future__ import annotations

from typing import Iterable


def build_compiled_output(articles: Iterable[str]) -> str:
    """Susun artikel sesuai format compiled_output.txt yang ditentukan."""
    markers = ["111", "222", "333", "444", "555", "666", "777", "888", "999", "101010"]
    article_list = list(articles)

    if len(article_list) != 10:
        raise ValueError(f"Compiled output butuh tepat 10 artikel, didapat {len(article_list)}.")

    sections: list[str] = []
    for marker, article in zip(markers, article_list):
        sections.append(f"-###-\n{marker}\n-$$$-\n{article}")

    return "\n\n".join(sections) + "\n"
