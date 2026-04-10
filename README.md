# nosartikel (MVP)

Tool backend sederhana untuk automasi generate 10 artikel HTML menggunakan OpenAI Responses API dalam 5 batch (2 judul per batch).

## Struktur Proyek

- `.github/workflows/generate-articles.yml` — workflow manual GitHub Actions.
- `prompts/article_prompt.txt` — template prompt utama dengan placeholder judul.
- `inputs/titles.txt` — input judul (tepat 10 judul, satu judul per baris).
- `output_articles/` — folder output hasil artikel.
- `src/config.py` — konfigurasi path, model, dan rule bisnis.
- `src/main.py` — entry point orchestration.
- `src/generator.py` — pemanggilan OpenAI Responses API.
- `src/parser.py` — parsing dan validasi HTML hasil model.
- `src/formatter.py` — formatter `compiled_output.txt`.
- `requirements.txt` — dependency Python.

## Prasyarat

- Python 3.11+
- OpenAI API key aktif

## Cara Pakai Lokal

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variable API key:
   ```bash
   export OPENAI_API_KEY="your_api_key"
   ```

3. Pastikan `inputs/titles.txt` berisi tepat 10 judul non-kosong (satu baris per judul).

4. Jalankan generator dari root project:
   ```bash
   python src/main.py
   ```

## Format Input Judul

File: `inputs/titles.txt`

- Tepat 10 baris non-kosong.
- 1 baris = 1 judul artikel.
- Jika jumlah bukan 10, proses akan berhenti dengan error yang jelas.

## Output

Setelah berhasil, output ada di folder `output_articles/`:

- `article_01.html` sampai `article_10.html`
- `compiled_output.txt`

Format `compiled_output.txt` dihasilkan persis dengan pola berikut (hanya isi artikel yang berbeda):

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

## Cara Pakai via GitHub Actions

1. Tambahkan secret repository: `OPENAI_API_KEY`.
2. Buka tab **Actions** di GitHub.
3. Pilih workflow **Generate Articles**.
4. Klik **Run workflow**.
5. Setelah selesai, download artifact `output-articles` untuk mengambil hasil di folder `output_articles/`.

## Catatan MVP

- Tool hanya fokus pada alur inti: baca 10 judul, generate per batch, parse 2 artikel, validasi minimal, lalu simpan output.
- Tidak ada UI, database, Docker, atau fitur di luar scope.
