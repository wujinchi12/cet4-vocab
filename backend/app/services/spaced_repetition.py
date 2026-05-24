from datetime import datetime, timedelta


def calculate_next_review(status: str, correct_count: int) -> tuple[str, datetime | None]:
    if status == "new":
        return ("learning", datetime.utcnow() + timedelta(days=1))
    elif status == "learning":
        if correct_count >= 3:
            return ("mastered", datetime.utcnow() + timedelta(days=7))
        return ("learning", datetime.utcnow() + timedelta(days=1))
    elif status == "mastered":
        return ("mastered", datetime.utcnow() + timedelta(days=7))
    return ("new", None)


def handle_wrong_answer(status: str) -> tuple[str, datetime | None]:
    return ("new", None)
