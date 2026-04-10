"""Konfigurasi utama aplikasi generator artikel."""

from __future__ import annotations

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_TEMPLATE_PATH = BASE_DIR / "prompts" / "article_prompt.txt"
TITLES_PATH = BASE_DIR / "inputs" / "titles.txt"
OUTPUT_DIR = BASE_DIR / "output_articles"
COMPILED_OUTPUT_PATH = OUTPUT_DIR / "compiled_output.txt"
JOBS_DIR = BASE_DIR / "jobs"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"

# Business rules
EXPECTED_TITLES_COUNT = 10
BATCH_SIZE = 2
TOTAL_BATCHES = EXPECTED_TITLES_COUNT // BATCH_SIZE
MAX_PARSE_RETRY = 1
