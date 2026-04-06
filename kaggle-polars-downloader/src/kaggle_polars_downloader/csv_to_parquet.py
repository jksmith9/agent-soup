from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a CSV file to Parquet with Polars."
    )
    parser.add_argument("input_csv", help="Path to the input CSV file.")
    parser.add_argument(
        "output_parquet",
        nargs="?",
        help="Optional output path. Defaults to the same name with a .parquet extension.",
    )
    return parser.parse_args()


def default_output_path(input_csv: Path) -> Path:
    return input_csv.with_suffix(".parquet")


def read_csv_with_fallback(input_path: Path) -> pl.DataFrame:
    try:
        return pl.read_csv(input_path)
    except pl.exceptions.ComputeError:
        # Some files mix integer-like and float-like values in the same column.
        # Full-file schema inference prevents early rows from locking the wrong dtype.
        return pl.read_csv(input_path, infer_schema_length=None)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_csv).expanduser().resolve()
    output_path = (
        Path(args.output_parquet).expanduser().resolve()
        if args.output_parquet
        else default_output_path(input_path)
    )

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".csv":
        raise SystemExit(f"Expected a .csv file, got: {input_path.name}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame = read_csv_with_fallback(input_path)
    frame.write_parquet(output_path)

    print(f"Converted {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
