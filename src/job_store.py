"""Penyimpanan state job berbasis file lokal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import JOBS_DIR


class JobStore:
    """Manajemen file status dan output per job."""

    def __init__(self, base_dir: Path = JOBS_DIR) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _job_dir(self, job_id: str) -> Path:
        return self.base_dir / job_id

    def _status_path(self, job_id: str) -> Path:
        return self._job_dir(job_id) / "status.json"

    def _compiled_path(self, job_id: str) -> Path:
        return self._job_dir(job_id) / "compiled_output.txt"

    def init_job(self, job_id: str) -> None:
        self._job_dir(job_id).mkdir(parents=True, exist_ok=True)

    def update_status(self, job_id: str, payload: dict[str, Any]) -> None:
        path = self._status_path(job_id)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def read_status(self, job_id: str) -> dict[str, Any] | None:
        path = self._status_path(job_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def write_article(self, job_id: str, index: int, html: str) -> None:
        article_path = self._job_dir(job_id) / f"article_{index:02d}.html"
        article_path.write_text(html, encoding="utf-8")

    def write_compiled_output(self, job_id: str, content: str) -> None:
        self._compiled_path(job_id).write_text(content, encoding="utf-8")

    def read_compiled_output(self, job_id: str) -> str | None:
        path = self._compiled_path(job_id)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def compiled_path(self, job_id: str) -> Path:
        return self._compiled_path(job_id)
