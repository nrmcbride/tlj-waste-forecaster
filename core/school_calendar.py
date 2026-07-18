from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo


def get_school_status() -> str:
    """
    Returns the school status for tomorrow based on the WCPSS
    2025-2026 and 2026-2027 traditional calendars.
    Uses Eastern time to avoid Colab/server UTC clock mismatch.
    Sources:
      https://cdn.northcarolinaschools.us/printables/wake-county-schools-calendar-2025-2026.pdf
      https://cdn.northcarolinaschools.us/printables/wake-county-schools-calendar-2026-2027.pdf
    """
    eastern_now = datetime.now(ZoneInfo("America/New_York"))
    tomorrow = (eastern_now + timedelta(days=1)).date()

    # --- 2025-2026 ---
    SCHOOL_START_2526 = date(2025, 8, 25)
    SCHOOL_END_2526 = date(2026, 6, 10)

    NO_STUDENT_DAYS_2526 = {
        # Teacher Workdays
        date(2025, 8, 18), date(2025, 8, 19), date(2025, 8, 20),
        date(2025, 8, 21), date(2025, 8, 22),
        date(2025, 9, 29),
        date(2025, 10, 13), date(2025, 10, 20),
        date(2025, 11, 3),
        date(2026, 1, 26),
        date(2026, 2, 16),
        date(2026, 3, 9),
        date(2026, 4, 6),
        date(2026, 5, 1),
        date(2026, 6, 11), date(2026, 6, 15),
        # Holidays
        date(2025, 9, 1),
        date(2025, 11, 11),
        date(2025, 11, 27), date(2025, 11, 28),
        date(2026, 1, 19),
        date(2026, 5, 25),
        # Thanksgiving Break
        date(2025, 11, 26),
        # Winter Break
        date(2025, 12, 22), date(2025, 12, 23), date(2025, 12, 24),
        date(2025, 12, 25), date(2025, 12, 26), date(2025, 12, 27),
        date(2025, 12, 28), date(2025, 12, 29), date(2025, 12, 30),
        date(2025, 12, 31),
        date(2026, 1, 1), date(2026, 1, 2),
        # Spring Break
        date(2026, 3, 30), date(2026, 3, 31),
        date(2026, 4, 1), date(2026, 4, 2), date(2026, 4, 3),
    }

    # --- 2026-2027 ---
    SCHOOL_START_2627 = date(2026, 8, 24)
    SCHOOL_END_2627 = date(2027, 6, 9)

    NO_STUDENT_DAYS_2627 = {
        # Teacher Workdays
        date(2026, 8, 17), date(2026, 8, 18), date(2026, 8, 19),
        date(2026, 8, 20), date(2026, 8, 21),
        date(2026, 9, 21),
        date(2026, 10, 12),
        date(2026, 11, 3),
        date(2026, 12, 21), date(2026, 12, 22),
        date(2027, 1, 19),
        date(2027, 2, 15),
        date(2027, 3, 10),
        date(2027, 4, 5),
        date(2027, 5, 17),
        date(2027, 6, 10), date(2027, 6, 11),
        # Holidays
        date(2026, 9, 7),
        date(2026, 11, 11),
        date(2027, 1, 1),
        date(2027, 1, 18),
        date(2027, 5, 31),
        # Thanksgiving Break
        date(2026, 11, 25), date(2026, 11, 26), date(2026, 11, 27),
        # Winter Break
        date(2026, 12, 23), date(2026, 12, 24), date(2026, 12, 25),
        date(2026, 12, 26), date(2026, 12, 27), date(2026, 12, 28),
        date(2026, 12, 29), date(2026, 12, 30), date(2026, 12, 31),
        # Spring Break
        date(2027, 3, 26), date(2027, 3, 27), date(2027, 3, 28),
        date(2027, 3, 29), date(2027, 3, 30), date(2027, 3, 31),
        date(2027, 4, 1), date(2027, 4, 2),
    }

    target_date_str = tomorrow.strftime('%A, %B %d, %Y')

    if tomorrow.weekday() >= 5:
        return f"Status of Cary High ({target_date_str}): Weekend."

    elif SCHOOL_START_2526 <= tomorrow <= SCHOOL_END_2526:
        if tomorrow in NO_STUDENT_DAYS_2526:
            return f"Status of Cary High ({target_date_str}): No students in school (holiday, break, or teacher workday)."
        else:
            return f"Status of Cary High ({target_date_str}): Regular school day in session."

    elif SCHOOL_START_2627 <= tomorrow <= SCHOOL_END_2627:
        if tomorrow in NO_STUDENT_DAYS_2627:
            return f"Status of Cary High ({target_date_str}): No students in school (holiday, break, or teacher workday)."
        else:
            return f"Status of Cary High ({target_date_str}): Regular school day in session."

    else:
        return f"Status of Cary High ({target_date_str}): Outside the active school year (Summer Break)."