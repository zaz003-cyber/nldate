from datetime import date

import pytest

from nldate import parse

REFERENCE = date(2026, 11, 11)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2025-12-01", date(2025, 12, 1)),
        ("January 15, 2024", date(2024, 1, 15)),
        ("March 1st, 2024", date(2024, 3, 1)),
        ("2 weeks ago", date(2026, 10, 28)),
        ("in 2 weeks", date(2026, 11, 25)),
        ("3 months ago", date(2026, 8, 11)),
        ("in 1 year", date(2027, 11, 11)),
        ("1 year and 2 months after yesterday", date(2028, 1, 10)),
        ("10 days after tomorrow", date(2026, 11, 22)),
        ("next Wednesday", date(2026, 11, 18)),
        ("last Wednesday", date(2026, 11, 4)),
        ("February 29, 2024", date(2024, 2, 29)),
    ],
)
def test_advanced_dates(expression: str, expected: date) -> None:
    assert parse(expression, today=REFERENCE) == expected
