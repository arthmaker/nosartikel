"""Modul parsing output model menjadi 2 artikel HTML."""

from __future__ import annotations

import re

CODE_BLOCK_RE = re.compile(r"```(?:html)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_two_html_articles(raw_text: str) -> list[str]:
    """Ekstrak tepat dua blok kode HTML dari output model."""
    blocks = [block.strip() for block in CODE_BLOCK_RE.findall(raw_text)]
    if len(blocks) != 2:
        raise ValueError(
            f"Gagal parsing: expected 2 code blocks, didapat {len(blocks)} blok."
        )
    return blocks


def validate_article_html(article_html: str) -> None:
    """Validasi minimal struktur artikel."""
    content = article_html.strip()
    if not content:
        raise ValueError("Artikel kosong.")

    lowered = content.lower()
    if "<h2" not in lowered:
        raise ValueError("Artikel tidak mengandung tag <h2>.")
    if "<p" not in lowered:
        raise ValueError("Artikel tidak mengandung tag <p>.")
