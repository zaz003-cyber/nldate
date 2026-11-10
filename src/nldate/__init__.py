import re
from datetime import date, timedelta

from .offsets import parse_offset

WEEKDAYS = {
    name: i
    for i, name in enumerate(
        ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    )
}

MONTHS = {
    name: i
    for i, name in enumerate(
        [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ],
        start=1,
    )
}

NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    expression = s.strip().lower()

    if expression == "today":
        return today
    if expression == "tomorrow":
        return today + timedelta(days=1)
    if expression == "yesterday":
        return today - timedelta(days=1)

    # Absolute dates: December 1st, 2025
    match = re.fullmatch(
        r"([a-z]+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})",
        expression,
    )
    if match and match.group(1) in MONTHS:
        month = MONTHS[match.group(1)]
        return date(int(match.group(3)), month, int(match.group(2)))

    # Relative weekdays
    match = re.fullmatch(
        r"(next|last) (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        expression,
    )
    if match:
        direction, weekday = match.groups()
        target = WEEKDAYS[weekday]
        current = today.weekday()

        if direction == "next":
            days = (target - current) % 7 or 7
            return today + timedelta(days=days)

        days = (current - target) % 7 or 7
        return today - timedelta(days=days)

    # Relative offsets: 5 days ago, two weeks from tomorrow
    match = re.fullmatch(
        r"(?:in )?(\d+|[a-z]+) (days?|weeks?) "
        r"(ago|before|after|from|later|hence)(?: (.+))?",
        expression,
    )
    if match:
        count_text, unit, direction, base_text = match.groups()

        if count_text.isdigit():
            count = int(count_text)
        elif count_text in NUMBERS:
            count = NUMBERS[count_text]
        else:
            raise ValueError(f"Unknown number: {count_text}")

        days = count * (7 if unit.startswith("week") else 1)

        if base_text:
            base = parse(base_text, today=today)
        else:
            base = today

        if direction in ("ago", "before"):
            days = -days

        return base + timedelta(days=days)

    # Short relative forms: in 3 days
    match = re.fullmatch(r"in (\d+) (days?|weeks?)", expression)
    if match:
        days = int(match.group(1))
        if match.group(2).startswith("week"):
            days *= 7
        return today + timedelta(days=days)

    # ISO date format
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", expression):
        return date.fromisoformat(expression)

    result = parse_offset(expression, today, parse)
    if result is not None:
        return result

    raise ValueError(f"Unrecognized date: {s}")
