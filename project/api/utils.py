from typing import Tuple
import calendar
from datetime import date

def get_start_and_end_dates_from_year_and_month(year:int, month:int) -> Tuple[date,date]:
    last_day = calendar.monthrange(year, month)[1]
    return (
        date(year=year, month=month, day=1),
        date(year=year, month=month, day=last_day),
    )