from datetime import datetime, date
from zoneinfo import ZoneInfo

def today_in_tz(tz_name: str | None, fallback_tz: str = "America/Bogota") -> date:
    tz = tz_name or fallback_tz
    try:
        return datetime.now(ZoneInfo(tz)).date()
    except Exception:
        return datetime.utcnow().date()