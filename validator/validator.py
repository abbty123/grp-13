from other_modules.errorHandlers import InvalidInputError
import re
class Validator:
    @staticmethod
    def validate_country_name(name: str):
        # Regex: Letters, spaces, hyphens, min 2 chars
        pattern = r"^[a-zA-Z\s\-]{2,60}$"
        if not re.match(pattern, name.strip()):
            raise InvalidInputError("Country name must contain only letters, spaces, or hyphens (min 2 chars).")

    @staticmethod
    def parse_utc_offset(tz_str: str) -> float:
        # Regex: Parses formats like UTC, UTC+01:00, UTC-05:30
        pattern = r"^UTC(?:([+-])(\d{2}):(\d{2}))?$"
        match = re.match(pattern, tz_str)
        if not match:
            return 0.0
        
        sign, hours, minutes = match.groups()
        if not sign:
            return 0.0
        
        offset = float(hours) + (float(minutes) / 60.0)
        return offset if sign == "+" else -offset