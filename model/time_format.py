from datetime import datetime


class TimeFormat:
    ZULU = "%H:%M %m/%d/%y %p"

    @staticmethod
    def now() -> str:
        return datetime.now().strftime(TimeFormat.ZULU)
