from models.country import Country
from validator.validator import Validator

class CountryComparator:
    @staticmethod
    def calculate_tz_difference(c1: Country, c2: Country) -> str:
        try:
            offset1 = Validator.parse_utc_offset(c1.timezones[0])
            offset2 = Validator.parse_utc_offset(c2.timezones[0])
            diff = offset2 - offset1
            
            sign = "+" if diff > 0 else ""
            return f"{c2.name} is {sign}{diff:g} hour(s) relative to {c1.name} (based on primary timezones)."
        except Exception:
            return "Timezone calculation unavailable."

    @staticmethod
    def generate_checklist(country: Country) -> list:
        return [
            f"Check visa requirements for {country.name} ({country.region})",
            f"Ensure passport is valid for 6+ months past departure",
            f"Exchange currency or enable international payments for {country.currency}",
            f"Acquire medical insurance & check health guidelines for {country.capital}",
            f"Download offline map & translation apps for {country.languages}"
        ]