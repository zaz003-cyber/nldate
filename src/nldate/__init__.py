import re
from datetime import date, timedelta

from .offsets import add_months

MONTH_NAMES = [
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
]
MONTHS = {name: i for i, name in enumerate(MONTH_NAMES, 1)}
MONTHS.update({name[:3]: i for i, name in enumerate(MONTH_NAMES, 1)})
MONTH_PATTERN = "|".join(sorted(MONTHS, key=len, reverse=True))

DAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
DAYS = {name: i for i, name in enumerate(DAY_NAMES)}
DAYS.update({name[:3]: i for i, name in enumerate(DAY_NAMES)})

ONES = {
    "zero": 0,
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
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "a": 1,
    "an": 1,
}
TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
UNIT = r"days?|weeks?|months?|years?"
AMOUNT = rf"(.+?)\s+({UNIT})"


def number_value(text: str) -> int:
    text = text.strip().replace("-", " ")
    if text.isdigit():
        return int(text)
    if text in ONES:
        return ONES[text]
    if text in TENS:
        return TENS[text]
    words = text.split()
    if len(words) == 2 and words[0] in TENS and words[1] in ONES:
        return TENS[words[0]] + ONES[words[1]]
    raise ValueError(f"Invalid number: {text}")


def shift(base: date, amount: str, sign: int) -> date:
    months = 0
    days = 0
    parts = re.split(r"\s*(?:,|\band\b)\s*", amount)

    if not parts or any(not part for part in parts):
        raise ValueError(f"Invalid duration: {amount}")

    for part in parts:
        match = re.fullmatch(AMOUNT, part)
        if not match:
            raise ValueError(f"Invalid duration: {amount}")

        count = number_value(match.group(1))
        unit = match.group(2)

        if unit.startswith("year"):
            months += count * 12
        elif unit.startswith("month"):
            months += count
        elif unit.startswith("week"):
            days += count * 7
        else:
            days += count

    result = add_months(base, sign * months)
    return result + timedelta(days=sign * days)


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    expression = re.sub(r"\s+", " ", s.strip().lower())

    if not expression:
        raise ValueError("Empty date expression")

    simple = {
        "today": 0,
        "now": 0,
        "tomorrow": 1,
        "yesterday": -1,
        "day after tomorrow": 2,
        "day before yesterday": -2,
    }
    if expression in simple:
        return today + timedelta(days=simple[expression])

    # Year-first numeric dates.
    match = re.fullmatch(
        r"(\d{4})([-/.])(\d{1,2})\2(\d{1,2})",
        expression,
    )
    if match:
        year, _, month, day = match.groups()
        return date(int(year), int(month), int(day))

    # Compact YYYYMMDD.
    match = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", expression)
    if match:
        return date(*(int(value) for value in match.groups()))

    # US numeric month/day/year.
    match = re.fullmatch(
        r"(\d{1,2})([-/.])(\d{1,2})\2(\d{4})",
        expression,
    )
    if match:
        month, _, day, year = match.groups()
        return date(int(year), int(month), int(day))

    # Month-first English dates, including Dec. 1, 2025.
    match = re.fullmatch(
        rf"({MONTH_PATTERN})\.?\s+"
        r"(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:,?\s+(\d{4}))?",
        expression,
    )
    if match:
        month, day, year = match.groups()
        return date(int(year) if year else today.year, MONTHS[month], int(day))

    # Day-first English dates.
    match = re.fullmatch(
        rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+"
        rf"(?:of\s+)?({MONTH_PATTERN})\.?"
        r"(?:,?\s+(\d{4}))?",
        expression,
    )
    if match:
        day, month, year = match.groups()
        return date(int(year) if year else today.year, MONTHS[month], int(day))

    # Relative weekday expressions.
    match = re.fullmatch(r"(next|last|this)\s+([a-z]+)", expression)
    if match and match.group(2) in DAYS:
        direction, weekday = match.groups()
        current = today.weekday()
        target = DAYS[weekday]

        if direction == "next":
            delta = (target - current) % 7 or 7
        elif direction == "last":
            delta = -((current - target) % 7 or 7)
        else:
            delta = target - current

        return today + timedelta(days=delta)

    # Standalone weekdays: upcoming occurrence.
    if expression in DAYS:
        delta = (DAYS[expression] - today.weekday()) % 7
        return today + timedelta(days=delta)

    # Next / last week, month, year.
    match = re.fullmatch(
        r"(next|last|this)\s+(day|week|month|year)",
        expression,
    )
    if match:
        direction, unit = match.groups()
        sign = {"next": 1, "last": -1, "this": 0}[direction]
        if unit == "day":
            return today + timedelta(days=sign)
        if unit == "week":
            return today + timedelta(weeks=sign)
        return add_months(today, sign * (12 if unit == "year" else 1))

    # Expressions with explicit reference dates.
    match = re.fullmatch(
        r"(.+?)\s+(before|after|from)\s+(.+)",
        expression,
    )
    if match:
        amount, direction, reference = match.groups()
        base = parse(reference, today=today)
        return shift(base, amount, -1 if direction == "before" else 1)

    # In N days / months / years.
    if expression.startswith("in "):
        return shift(today, expression[3:], 1)

    # N days ago, N days later, N days hence.
    match = re.fullmatch(r"(.+?)\s+(ago|later|hence)", expression)
    if match:
        amount, direction = match.groups()
        return shift(today, amount, -1 if direction == "ago" else 1)

    raise ValueError(f"Unrecognized date: {s}")
