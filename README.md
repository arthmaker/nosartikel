# nosartikel (MVP + Dashboard Flask)

Tool ini memiliki dua mode penggunaan:

1. **Mode Dashboard (Flask + HTML/JS)** untuk input judul dari browser, melihat progress, copy output, dan download hasil.
2. **Mode CLI (legacy)** yang tetap dipertahankan (`python src/main.py`).

Fondasi generator lama tetap dipakai: OpenAI Responses API, prompt template, retry parse 1 kali, validasi 10 judul non-kosong, dan format output marker tetap sama.

## Struktur Proyek

- `.github/workflows/generate-articles.yml` — workflow manual GitHub Actions (mode CLI).
- `app.py` — backend Flask untuk dashboard.
- `templates/index.html` — halaman dashboard.
- `static/style.css` — styling dashboard.
- `static/app.js` — logic frontend (upload txt, generate, polling status, copy, download, reset).
- `src/job_store.py` — penyimpanan state/output job berbasis file.
- `jobs/` — output per job dashboard (`status.json`, artikel, compiled output).
- `prompts/article_prompt.txt` — template prompt utama dengan placeholder judul.
- `inputs/titles.txt` — input judul mode CLI (tepat 10 judul, satu judul per baris).
- `output_articles/` — folder output mode CLI.
- `src/config.py` — konfigurasi path, model, dan rule bisnis.
- `src/main.py` — entry point mode CLI.
- `src/generator.py` — pemanggilan OpenAI Responses API.
- `src/parser.py` — parsing dan validasi HTML hasil model.
- `src/formatter.py` — formatter `compiled_output.txt`.
- `requirements.txt` — dependency Python.

## Prasyarat

- Python 3.11+
- OpenAI API key aktif

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variable:

```bash
export OPENAI_API_KEY="your_api_key"
```

---

## Menjalankan Dashboard (Flask)

Jalankan dari root project:

```bash
python app.py
```

Buka browser ke:

- `http://127.0.0.1:5000/`

### Fitur Dashboard

- Isi 10 judul manual.
- Upload file `.txt` (1 judul/baris) untuk auto-fill 10 input pertama non-kosong.
- Klik **Generate** untuk membuat job.
- Progress bar tampil 20/40/60/80/100 sesuai batch 1-5.
- Status batch aktif tampil (`Batch x/5`).
- Setelah selesai, hasil `compiled_output.txt` tampil di textarea.
- Tombol **Copy** untuk menyalin output.
- Tombol **Download** untuk unduh hasil final `.txt`.
- Tombol **Reset** untuk reset form dan state UI.

### API Dashboard

- `GET /` → render dashboard.
- `POST /api/generate` → mulai job baru.
  - Payload JSON:
    ```json
    {"titles": ["judul 1", "judul 2", "...", "judul 10"]}
    ```
- `GET /api/status/<job_id>` → status progres job.
- `GET /api/result/<job_id>` → hasil final jika job selesai.
- `GET /api/download/<job_id>` → download `compiled_output.txt`.

### Struktur Output Job Dashboard

Disimpan di `jobs/<job_id>/`:

- `status.json`
- `article_01.html` sampai `article_10.html`
- `compiled_output.txt`

---

## Menjalankan Mode CLI (Legacy Tetap Aktif)

1. Pastikan `inputs/titles.txt` berisi tepat 10 judul non-kosong (satu baris per judul).
2. Jalankan:

```bash
python src/main.py
```

Output CLI:

- `output_articles/article_01.html` sampai `output_articles/article_10.html`
- `output_articles/compiled_output.txt`

## Format Input Judul (CLI)

File: `inputs/titles.txt`

- Tepat 10 baris non-kosong.
- 1 baris = 1 judul artikel.
- Jika jumlah bukan 10, proses berhenti dengan error jelas.

## Format `compiled_output.txt` (Tetap)

Format output final tetap sama:

```text
-###-
111
-$$$-
[artikel 1]

-###-
222
-$$$-
[artikel 2]

-###-
333
-$$$-
[artikel 3]

-###-
444
-$$$-
[artikel 4]

-###-
555
-$$$-
[artikel 5]

-###-
666
-$$$-
[artikel 6]

-###-
777
-$$$-
[artikel 7]

-###-
888
-$$$-
[artikel 8]

-###-
999
-$$$-
[artikel 9]

-###-
101010
-$$$-
[artikel 10]
```

---

## GitHub Actions (Tetap Dipertahankan)

Workflow lama tetap ada: `.github/workflows/generate-articles.yml`

Langkah pakai:

1. Tambahkan secret repository: `OPENAI_API_KEY`.
2. Buka tab **Actions**.
3. Pilih workflow **Generate Articles**.
4. Klik **Run workflow**.
5. Download artifact `output-articles`.

## Catatan MVP

- Tidak menggunakan database.
- Tidak menggunakan websocket/Celery/Redis.
- Tidak mengekspos API key ke frontend.
- Logika inti tetap di backend Python dan reuse modul generator lama.
