from datetime import date

import pytest

from nldate import parse

REFERENCE = date(2026, 11, 11)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2025/12/04", date(2025, 12, 4)),
        ("2025/12/3", date(2025, 12, 3)),
        ("2025/1/3", date(2025, 1, 3)),
        ("2025-1-3", date(2025, 1, 3)),
        ("Dec 3, 2025", date(2025, 12, 3)),
        ("Dec. 1, 2025", date(2025, 12, 1)),
        ("3 December 2025", date(2025, 12, 3)),
        ("December 3rd 2025", date(2025, 12, 3)),
        ("in two weeks", date(2026, 11, 25)),
        ("three days ago", date(2026, 11, 8)),
        ("one month from today", date(2026, 12, 11)),
        ("two years from tomorrow", date(2028, 11, 12)),
        ("10 days before next Friday", date(2026, 11, 3)),
        ("1 month after January 31, 2024", date(2024, 2, 29)),
    ],
)
def test_common_formats(expression: str, expected: date) -> None:
    assert parse(expression, today=REFERENCE) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "2025/13/01",
        "2025/02/30",
        "2025-00-15",
        "February 29, 2025",
    ],
)
def test_invalid_formats(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, today=REFERENCE)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("the day after tomorrow", date(2026, 11, 13)),
        ("the day before yesterday", date(2026, 11, 9)),
        ("day after tomorrow", date(2026, 11, 13)),
        ("day before yesterday", date(2026, 11, 9)),
        ("THE DAY AFTER TOMORROW", date(2026, 11, 13)),
    ],
)
def test_extended_relative_days(expression: str, expected: date) -> None:
    assert parse(expression, today=REFERENCE) == expected
