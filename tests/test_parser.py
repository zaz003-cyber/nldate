from datetime import date

import pytest

from nldate import parse

REFERENCE = date(2026, 11, 11)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("today", date(2026, 11, 11)),
        ("tomorrow", date(2026, 11, 12)),
        ("yesterday", date(2026, 11, 10)),
        ("in 3 days", date(2026, 11, 14)),
        ("5 days ago", date(2026, 11, 6)),
        ("next Tuesday", date(2026, 11, 17)),
        ("last Monday", date(2026, 11, 9)),
        ("December 1st, 2025", date(2025, 12, 1)),
        ("5 days before December 1st, 2025", date(2025, 11, 26)),
        ("two weeks from tomorrow", date(2026, 11, 26)),
    ],
)
def test_supported_dates(expression: str, expected: date) -> None:
    assert parse(expression, today=REFERENCE) == expected


@pytest.mark.parametrize("expression", ["", "hello world", "not a date"])
def test_invalid_dates(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, today=REFERENCE)
