import csv
import sys
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from download_data import FEATURES, SOURCES, combine_archive  # noqa: E402


def make_archive(sources: tuple[str, ...] = SOURCES, row: str | None = None) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for source in sources:
            archive.writestr(f"processed.{source}.data", row or ",".join(["1"] * 14))
    return buffer.getvalue()


def test_combine_archive_adds_source_and_header() -> None:
    combined = list(csv.reader(StringIO(combine_archive(make_archive()))))

    assert combined[0] == ["source", *FEATURES]
    assert [row[0] for row in combined[1:]] == list(SOURCES)
    assert len(combined) == len(SOURCES) + 1


def test_combine_archive_rejects_missing_source_file() -> None:
    with pytest.raises(FileNotFoundError, match="processed.va.data"):
        combine_archive(make_archive(SOURCES[:-1]))


def test_combine_archive_rejects_rows_with_wrong_column_count() -> None:
    with pytest.raises(ValueError, match="Expected 14 columns"):
        combine_archive(make_archive(row="1,2,3"))
