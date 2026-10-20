"""Download and combine the processed UCI Heart Disease source files."""

import csv
from io import BytesIO, StringIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_URL = "https://archive.ics.uci.edu/static/public/45/heart+disease.zip"
OUTPUT_PATH = ROOT / "data/raw/heart_disease_combined.csv"
SOURCES = ("cleveland", "hungarian", "switzerland", "va")
FEATURES = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",
)


def combine_archive(archive_data: bytes) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(("source", *FEATURES))

    with ZipFile(BytesIO(archive_data)) as archive:
        names = set(archive.namelist())
        for source in SOURCES:
            member = f"processed.{source}.data"
            if member not in names:
                raise FileNotFoundError(f"Expected {member} in the UCI archive")
            contents = archive.read(member).decode("utf-8")
            for row_number, row in enumerate(csv.reader(StringIO(contents)), start=1):
                if not row:
                    continue
                if len(row) != len(FEATURES):
                    raise ValueError(
                        f"Expected {len(FEATURES)} columns in {member} row {row_number}, "
                        f"got {len(row)}"
                    )
                writer.writerow((source, *row))

    return output.getvalue()


def main() -> None:
    with urlopen(ARCHIVE_URL, timeout=30) as response:
        archive_data = response.read()
    combined_csv = combine_archive(archive_data)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(combined_csv, encoding="utf-8", newline="")
    records = sum(1 for _ in csv.reader(StringIO(combined_csv))) - 1
    print(f"Wrote {records} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
