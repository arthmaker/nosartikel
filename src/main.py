"""Entry point generator artikel MVP."""

from __future__ import annotations

from pathlib import Path

from config import (
    BATCH_SIZE,
    COMPILED_OUTPUT_PATH,
    EXPECTED_TITLES_COUNT,
    MAX_PARSE_RETRY,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OUTPUT_DIR,
    PROMPT_TEMPLATE_PATH,
    TITLES_PATH,
)
from formatter import build_compiled_output
from generator import ArticleGenerator
from parser import extract_two_html_articles, validate_article_html


def read_titles(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    titles = [line for line in lines if line]
    if len(titles) != EXPECTED_TITLES_COUNT:
        raise ValueError(
            f"inputs/titles.txt harus berisi tepat {EXPECTED_TITLES_COUNT} judul non-kosong. "
            f"Saat ini: {len(titles)}"
        )
    return titles


def make_batches(titles: list[str]) -> list[tuple[str, str]]:
    return [(titles[i], titles[i + 1]) for i in range(0, len(titles), BATCH_SIZE)]


def render_prompt(template: str, title_1: str, title_2: str) -> str:
    return template.replace("{{TITLE_1}}", title_1).replace("{{TITLE_2}}", title_2)


def run() -> None:
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY belum di-set pada environment variable.")

    titles = read_titles(TITLES_PATH)
    batches = make_batches(titles)
    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")

    generator = ArticleGenerator(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_articles: list[str] = []

    for batch_index, (title_1, title_2) in enumerate(batches, start=1):
        prompt = render_prompt(template, title_1, title_2)
        max_attempts = MAX_PARSE_RETRY + 1

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                raw_output = generator.generate_batch(prompt)
                articles = extract_two_html_articles(raw_output)
                for article in articles:
                    validate_article_html(article)
                all_articles.extend(articles)
                break
            except Exception as exc:
                last_error = exc
                if attempt == max_attempts:
                    raise RuntimeError(
                        f"Batch {batch_index} gagal setelah {max_attempts} percobaan: {exc}"
                    ) from exc

        if last_error is not None and len(all_articles) < batch_index * BATCH_SIZE:
            raise RuntimeError(f"Batch {batch_index} gagal diproses: {last_error}")

    if len(all_articles) != EXPECTED_TITLES_COUNT:
        raise RuntimeError(
            f"Jumlah artikel final harus {EXPECTED_TITLES_COUNT}, tetapi didapat {len(all_articles)}"
        )

    for idx, article in enumerate(all_articles, start=1):
        article_path = OUTPUT_DIR / f"article_{idx:02d}.html"
        article_path.write_text(article, encoding="utf-8")

    compiled_output = build_compiled_output(all_articles)
    COMPILED_OUTPUT_PATH.write_text(compiled_output, encoding="utf-8")

    print("Selesai. 10 artikel berhasil dibuat.")
    print(f"Output individu: {OUTPUT_DIR.resolve()}")
    print(f"Output gabungan: {COMPILED_OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    run()
