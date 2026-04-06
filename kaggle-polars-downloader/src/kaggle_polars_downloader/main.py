from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import polars as pl

TABULAR_SUFFIXES = {".csv", ".tsv", ".parquet", ".jsonl", ".ndjson", ".json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a Kaggle dataset and inspect it with Polars."
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default=os.getenv("KAGGLE_DATASET"),
        help="Kaggle dataset slug, for example zynicide/wine-reviews.",
    )
    parser.add_argument(
        "--file",
        default=os.getenv("KAGGLE_FILE") or None,
        help="Optional file inside the dataset to load with Polars.",
    )
    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directory where Kaggle files should be downloaded and extracted.",
    )
    parser.add_argument(
        "--parquet-dir",
        default="data/parquet",
        help="Directory where converted Parquet files should be written.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of rows to print from the selected file.",
    )
    parser.add_argument(
        "--convert-parquet",
        action="store_true",
        help="Save the loaded dataset as a Parquet file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete any existing local copy before downloading again.",
    )
    args = parser.parse_args()
    if not args.dataset:
        parser.error("Provide a dataset slug or set KAGGLE_DATASET in .env.")
    return args


def dataset_folder_name(dataset: str) -> str:
    return dataset.replace("/", "__")


def download_dataset(dataset: str, destination: Path, force: bool) -> None:
    from kaggle.api.kaggle_api_extended import KaggleApi

    if force and destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(
        dataset=dataset,
        path=str(destination),
        unzip=True,
        force=force,
        quiet=False,
    )


def discover_tabular_files(dataset_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in dataset_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in TABULAR_SUFFIXES
    )


def resolve_selected_file(dataset_dir: Path, files: list[Path], requested: str | None) -> Path:
    if not files:
        raise FileNotFoundError(f"No supported tabular files found in {dataset_dir}.")

    if not requested:
        return files[0]

    exact_matches = [
        path
        for path in files
        if path.name == requested or path.relative_to(dataset_dir).as_posix() == requested
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        raise ValueError(f"Multiple files matched '{requested}'. Use the relative path.")

    raise FileNotFoundError(f"Could not find '{requested}' in {dataset_dir}.")


def read_with_polars(path: Path, limit: int) -> pl.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pl.read_csv(path, n_rows=limit)
    if suffix == ".tsv":
        return pl.read_csv(path, separator="\t", n_rows=limit)
    if suffix == ".parquet":
        return pl.read_parquet(path).head(limit)
    if suffix in {".jsonl", ".ndjson"}:
        return pl.read_ndjson(path).head(limit)
    if suffix == ".json":
        return pl.read_json(path).head(limit)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def read_full_with_polars(path: Path) -> pl.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pl.read_csv(path)
    if suffix == ".tsv":
        return pl.read_csv(path, separator="\t")
    if suffix == ".parquet":
        return pl.read_parquet(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pl.read_ndjson(path)
    if suffix == ".json":
        return pl.read_json(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def maybe_write_parquet(frame: pl.DataFrame, source_file: Path, parquet_root: Path) -> Path:
    parquet_root.mkdir(parents=True, exist_ok=True)
    output_path = parquet_root / f"{source_file.stem}.parquet"
    frame.write_parquet(output_path)
    return output_path


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.data_dir) / dataset_folder_name(args.dataset)

    print(f"Downloading Kaggle dataset: {args.dataset}")
    download_dataset(args.dataset, dataset_dir, args.force)

    files = discover_tabular_files(dataset_dir)
    if not files:
        raise SystemExit(
            f"Download finished, but no supported tabular files were found in {dataset_dir}."
        )

    print("\nTabular files found:")
    for file_path in files:
        print(f"- {file_path.relative_to(dataset_dir).as_posix()}")

    selected_file = resolve_selected_file(dataset_dir, files, args.file)
    print(f"\nLoading with Polars: {selected_file.relative_to(dataset_dir).as_posix()}")

    preview = read_with_polars(selected_file, args.limit)
    print("\nPreview:")
    print(preview)

    if args.convert_parquet:
        full_frame = read_full_with_polars(selected_file)
        parquet_path = maybe_write_parquet(
            full_frame,
            selected_file,
            Path(args.parquet_dir) / dataset_folder_name(args.dataset),
        )
        print(f"\nWrote Parquet copy to: {parquet_path}")


if __name__ == "__main__":
    main()
