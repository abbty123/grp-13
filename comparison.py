# comparison.py
"""
Member 4 - Country Comparison + Timezone
Group 13: Country Relocation & Culture Guide
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def calculate_timezone_difference(timezone1, timezone2):
    """Calculate the current time difference between two IANA timezones."""

    if not timezone1 or not timezone2:
        raise ValueError("Both timezone values are required.")

    try:
        zone1 = ZoneInfo(timezone1)
        zone2 = ZoneInfo(timezone2)
    except ZoneInfoNotFoundError:
        raise ValueError("One or both timezone names are invalid.")

    now = datetime.now().astimezone()

    time1 = now.astimezone(zone1)
    time2 = now.astimezone(zone2)

    difference = time2.utcoffset() - time1.utcoffset()
    total_seconds = int(difference.total_seconds())

    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    if minutes:
        return f"{sign}{hours} hours {minutes} minutes"

    return f"{sign}{hours} hours"


def _format_currency(currency):
    """Convert currency data into readable text."""

    if not currency:
        return "Not available"

    if isinstance(currency, dict):
        currencies = []

        for code, details in currency.items():
            if isinstance(details, dict):
                name = details.get("name", code)
                symbol = details.get("symbol")

                if symbol:
                    currencies.append(f"{name} ({code}, {symbol})")
                else:
                    currencies.append(f"{name} ({code})")
            else:
                currencies.append(str(code))

        return ", ".join(currencies) if currencies else "Not available"

    return str(currency)


def _format_languages(languages):
    """Convert language data into readable text."""

    if not languages:
        return "Not available"

    if isinstance(languages, dict):
        return ", ".join(str(language) for language in languages.values())

    if isinstance(languages, list):
        return ", ".join(str(language) for language in languages)

    return str(languages)


def _get_timezone(country):
    """Safely obtain the first timezone from a country dictionary."""

    timezones = country.get("timezone", country.get("timezones"))

    if not timezones:
        return None

    if isinstance(timezones, list):
        return timezones[0] if timezones else None

    return str(timezones)


def compare_countries(country1, country2):
    """Compare two country dictionaries and return the comparison."""

    if not isinstance(country1, dict) or not isinstance(country2, dict):
        raise TypeError("Both countries must be dictionaries.")

    name1 = country1.get("name", "Unknown country")
    name2 = country2.get("name", "Unknown country")

    capital1 = country1.get("capital", "Not available")
    capital2 = country2.get("capital", "Not available")

    population1 = country1.get("population", "Not available")
    population2 = country2.get("population", "Not available")

    region1 = country1.get("region", "Not available")
    region2 = country2.get("region", "Not available")

    currency1 = _format_currency(country1.get("currency"))
    currency2 = _format_currency(country2.get("currency"))

    languages1 = _format_languages(country1.get("languages"))
    languages2 = _format_languages(country2.get("languages"))

    timezone1 = _get_timezone(country1)
    timezone2 = _get_timezone(country2)

    try:
        if timezone1 and timezone2:
            timezone_difference = calculate_timezone_difference(
                timezone1, timezone2
            )
        else:
            timezone_difference = "Not available"
    except ValueError:
        timezone_difference = "Not available"

    return {
        "country1": {
            "name": name1,
            "capital": capital1,
            "population": population1,
            "region": region1,
            "currency": currency1,
            "languages": languages1,
            "timezone": timezone1 or "Not available"
        },
        "country2": {
            "name": name2,
            "capital": capital2,
            "population": population2,
            "region": region2,
            "currency": currency2,
            "languages": languages2,
            "timezone": timezone2 or "Not available"
        },
        "timezone_difference": timezone_difference
    }
