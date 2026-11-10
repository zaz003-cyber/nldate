import calendar
from datetime import date


def add_months(base: date, months: int) -> date:
    index = base.year * 12 + base.month - 1 + months
    year, month_zero = divmod(index, 12)
    month = month_zero + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def parse_offset(expression: str, today: date, parse_base) -> date | None:
    import re
    from datetime import timedelta

    numbers = {
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

    match = re.fullmatch(
        r"(.+?) (ago|before|after|from|later|hence)(?: (.+))?",
        expression,
    )

    if match:
        amounts, direction, base_text = match.groups()
    elif expression.startswith("in "):
        amounts = expression[3:]
        direction = "after"
        base_text = None
    else:
        return None

    base = parse_base(base_text, today=today) if base_text else today
    total_months = 0
    total_days = 0

    for piece in re.split(r"\s+and\s+", amounts):
        part = re.fullmatch(
            r"(\d+|[a-z]+) (days?|weeks?|months?|years?)",
            piece,
        )
        if not part:
            return None

        count_text, unit = part.groups()
        count = int(count_text) if count_text.isdigit() else numbers.get(count_text)
        if count is None:
            return None

        if unit.startswith("year"):
            total_months += count * 12
        elif unit.startswith("month"):
            total_months += count
        elif unit.startswith("week"):
            total_days += count * 7
        else:
            total_days += count

    sign = -1 if direction in ("ago", "before") else 1
    shifted = add_months(base, sign * total_months)
    return shifted + timedelta(days=sign * total_days)
