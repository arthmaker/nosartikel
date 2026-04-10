"""Modul integrasi OpenAI Responses API."""

from __future__ import annotations

from openai import OpenAI


class ArticleGenerator:
    """Membungkus pemanggilan Responses API agar terpisah dari orchestrator."""

    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_batch(self, prompt: str) -> str:
        """Generate 2 artikel sekaligus dari 1 prompt batch."""
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        text = getattr(response, "output_text", "")
        if not text:
            raise RuntimeError("Responses API tidak mengembalikan output_text.")
        return text
