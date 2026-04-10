"""Flask dashboard untuk menjalankan generator artikel MVP."""

from __future__ import annotations

import threading
import uuid
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

from src.config import (
    BATCH_SIZE,
    EXPECTED_TITLES_COUNT,
    MAX_PARSE_RETRY,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    PROMPT_TEMPLATE_PATH,
    TOTAL_BATCHES,
)
from src.formatter import build_compiled_output
from src.generator import ArticleGenerator
from src.job_store import JobStore
from src.parser import extract_two_html_articles, validate_article_html

app = Flask(__name__)
job_store = JobStore()




def make_batches(titles: list[str]) -> list[tuple[str, str]]:
    return [(titles[i], titles[i + 1]) for i in range(0, len(titles), BATCH_SIZE)]


def render_prompt(template: str, title_1: str, title_2: str) -> str:
    return template.replace("{{TITLE_1}}", title_1).replace("{{TITLE_2}}", title_2)

def _normalize_titles(raw_titles: list[str]) -> list[str]:
    titles = [title.strip() for title in raw_titles if title and title.strip()]
    if len(titles) != EXPECTED_TITLES_COUNT:
        raise ValueError(
            f"Harus tepat {EXPECTED_TITLES_COUNT} judul non-kosong, saat ini {len(titles)}."
        )
    return titles


def _progress_for_batch(batch_index: int) -> int:
    return int((batch_index / TOTAL_BATCHES) * 100)


def _generate_job(job_id: str, titles: list[str]) -> None:
    status: dict[str, Any] = {
        "status": "running",
        "progress_percent": 0,
        "current_batch": 0,
        "total_batches": TOTAL_BATCHES,
        "message": "Memulai proses generate...",
        "error": None,
    }
    job_store.update_status(job_id, status)

    try:
        if not OPENAI_API_KEY:
            raise EnvironmentError("OPENAI_API_KEY belum di-set pada environment variable.")

        template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
        generator = ArticleGenerator(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        batches = make_batches(titles)

        all_articles: list[str] = []

        for batch_index, (title_1, title_2) in enumerate(batches, start=1):
            prompt = render_prompt(template, title_1, title_2)
            max_attempts = MAX_PARSE_RETRY + 1

            for attempt in range(1, max_attempts + 1):
                try:
                    raw_output = generator.generate_batch(prompt)
                    articles = extract_two_html_articles(raw_output)
                    for article in articles:
                        validate_article_html(article)
                    all_articles.extend(articles)
                    break
                except Exception as exc:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            f"Batch {batch_index} gagal setelah {max_attempts} percobaan: {exc}"
                        ) from exc

            status.update(
                {
                    "status": "running",
                    "progress_percent": _progress_for_batch(batch_index),
                    "current_batch": batch_index,
                    "message": f"Batch {batch_index}/{TOTAL_BATCHES} selesai.",
                }
            )
            job_store.update_status(job_id, status)

        for idx, article in enumerate(all_articles, start=1):
            job_store.write_article(job_id, idx, article)

        compiled_output = build_compiled_output(all_articles)
        job_store.write_compiled_output(job_id, compiled_output)

        status.update(
            {
                "status": "completed",
                "progress_percent": 100,
                "current_batch": TOTAL_BATCHES,
                "message": "Semua batch selesai. Output siap.",
                "error": None,
            }
        )
        job_store.update_status(job_id, status)

    except Exception as exc:  # noqa: BLE001
        status.update(
            {
                "status": "failed",
                "message": "Generate gagal.",
                "error": str(exc),
            }
        )
        job_store.update_status(job_id, status)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.post("/api/generate")
def api_generate():
    payload = request.get_json(silent=True) or {}
    raw_titles = payload.get("titles")

    if not isinstance(raw_titles, list):
        return jsonify({"error": "Payload harus berisi field 'titles' berupa array."}), 400

    try:
        titles = _normalize_titles([str(item) for item in raw_titles])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    job_id = uuid.uuid4().hex
    job_store.init_job(job_id)

    thread = threading.Thread(target=_generate_job, args=(job_id, titles), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.get("/api/status/<job_id>")
def api_status(job_id: str):
    status = job_store.read_status(job_id)
    if status is None:
        return jsonify({"error": "Job tidak ditemukan."}), 404
    return jsonify(status)


@app.get("/api/result/<job_id>")
def api_result(job_id: str):
    status = job_store.read_status(job_id)
    if status is None:
        return jsonify({"error": "Job tidak ditemukan."}), 404

    if status.get("status") != "completed":
        return jsonify({"error": "Job belum selesai.", "status": status}), 409

    compiled_output = job_store.read_compiled_output(job_id)
    if compiled_output is None:
        return jsonify({"error": "Hasil tidak ditemukan."}), 404

    return jsonify({"job_id": job_id, "compiled_output": compiled_output})


@app.get("/api/download/<job_id>")
def api_download(job_id: str):
    status = job_store.read_status(job_id)
    if status is None:
        return jsonify({"error": "Job tidak ditemukan."}), 404

    if status.get("status") != "completed":
        return jsonify({"error": "Job belum selesai."}), 409

    file_path = job_store.compiled_path(job_id)
    if not file_path.exists():
        return jsonify({"error": "File hasil tidak ditemukan."}), 404

    return send_file(file_path, as_attachment=True, download_name=f"compiled_output_{job_id}.txt")


if __name__ == "__main__":
    app.run(debug=True)
