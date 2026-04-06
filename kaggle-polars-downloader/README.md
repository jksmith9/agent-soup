# Kaggle Polars Downloader

Small `uv` project for downloading a Kaggle dataset and loading tabular files with `polars`.

## What it does

- Downloads a Kaggle dataset by slug, such as `zynicide/wine-reviews`
- Extracts it into `data/raw/<owner>__<dataset>/`
- Finds tabular files like `.csv`, `.tsv`, `.parquet`, `.jsonl`, and `.json`
- Loads one file with `polars` and prints a quick preview
- Optionally writes a `.parquet` copy into `data/parquet/`

## Setup

1. Move into the project folder:

```bash
cd kaggle-polars-downloader
```

2. Create a local env file from the example:

```bash
cp .env.example .env
```

3. Add your Kaggle credentials in one of these ways:

- Put `KAGGLE_USERNAME` and `KAGGLE_KEY` in `.env`
- Or use `~/.kaggle/kaggle.json`

4. Install dependencies with `uv`:

```bash
uv sync
```

## Usage

Run with the dataset slug directly:

```bash
uv run kaggle-polars zynicide/wine-reviews
```

Or store the slug in `.env` as `KAGGLE_DATASET` and then run:

```bash
uv run kaggle-polars
```

Pick a specific file inside the dataset and save a Parquet copy:

```bash
uv run kaggle-polars zynicide/wine-reviews --file winemag-data-130k-v2.csv --convert-parquet
```

## Notes

- `--force` clears the local extracted copy before downloading again.
- `--limit` changes the preview row count.
- If a dataset has multiple tabular files, the script lists them and uses the first one unless you pass `--file`.
