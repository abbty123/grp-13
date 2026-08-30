"""
Country Comparison Module
Group 13 - Member 3
Country Relocation & Culture Guide
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests


class CountryNotFoundError(Exception):
    """Raised when a country cannot be found."""
    pass


class CountryComparator:
    BASE_URL = "https://restcountries.com/v3.1/name/"

    def get_country(self, country_name):
        """
        Fetch country information from REST Countries API.
        Returns a simplified dictionary.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}{country_name}",
                params={"fullText": "true"},
                timeout=10
            )

            if response.status_code == 404:
                raise CountryNotFoundError(
                    f"Country '{country_name}' was not found."
                )

            response.raise_for_status()
            data = response.json()[0]

            currencies = data.get("currencies", {})
            currency_names = [
                currency.get("name", code)
                for code, currency in currencies.items()
            ]

            languages = list(data.get("languages", {}).values())

            return {
                "name": data.get("name", {}).get("common", "N/A"),
                "capital": ", ".join(data.get("capital", ["N/A"])),
                "currency": ", ".join(currency_names) or "N/A",
                "languages": ", ".join(languages) or "N/A",
                "population": data.get("population", 0),
                "region": data.get("region", "N/A"),
                "flag": data.get("flag", ""),
                "timezones": data.get("timezones", [])
            }

        except requests.exceptions.RequestException as error:
            raise ConnectionError(
                "Unable to connect to the country information service."
            ) from error

    def calculate_timezone_difference(self, timezone1, timezone2):
        """
        Calculate the current difference between two UTC offset timezones.
        Example: UTC+01:00 and UTC-05:00
        """
        try:
            def utc_offset_to_minutes(tz):
                if not tz.startswith("UTC"):
                    return None

                offset = tz[3:]

                if offset == "":
                    return 0

                sign = 1 if offset[0] == "+" else -1
                hours, minutes = offset[1:].split(":")
                return sign * (int(hours) * 60 + int(minutes))

            offset1 = utc_offset_to_minutes(timezone1)
            offset2 = utc_offset_to_minutes(timezone2)

            if offset1 is None or offset2 is None:
                return "Unable to calculate"

            difference = offset2 - offset1
            sign = "+" if difference >= 0 else "-"
            difference = abs(difference)

            hours = difference // 60
            minutes = difference % 60

            if minutes == 0:
                return f"{sign}{hours} hour(s)"

            return f"{sign}{hours} hour(s) {minutes} minute(s)"

        except (ValueError, IndexError):
            return "Unable to calculate"

    def compare_countries(self, country1_name, country2_name):
        """
        Fetch and compare two countries.
        """
        country1 = self.get_country(country1_name)
        country2 = self.get_country(country2_name)

        timezone_difference = "N/A"

        if country1["timezones"] and country2["timezones"]:
            timezone_difference = self.calculate_timezone_difference(
                country1["timezones"][0],
                country2["timezones"][0]
            )

        return {
            "country1": country1,
            "country2": country2,
            "timezone_difference": timezone_difference
        }

    def display_comparison(self, comparison):
        """Display comparison results in the terminal."""
        country1 = comparison["country1"]
        country2 = comparison["country2"]

        print("\n" + "=" * 75)
        print(
            f"{country1['flag']} {country1['name']}  VS  "
            f"{country2['flag']} {country2['name']}"
        )
        print("=" * 75)

        rows = [
            ("Capital", country1["capital"], country2["capital"]),
            ("Currency", country1["currency"], country2["currency"]),
            ("Languages", country1["languages"], country2["languages"]),
            ("Population", f"{country1['population']:,}",
             f"{country2['population']:,}"),
            ("Region", country1["region"], country2["region"]),
            ("Timezone", ", ".join(country1["timezones"]),
             ", ".join(country2["timezones"])),
        ]

        for label, value1, value2 in rows:
            print(f"\n{label}:")
            print(f"  {country1['name']}: {value1}")
            print(f"  {country2['name']}: {value2}")

        print("\nTimezone Difference:")
        print(
            f"  {country2['name']} compared with "
            f"{country1['name']}: "
            f"{comparison['timezone_difference']}"
        )
        print("=" * 75)


if __name__ == "__main__":
    comparator = CountryComparator()

    try:
        country1 = input("Enter the first country: ").strip()
        country2 = input("Enter the second country: ").strip()

        comparison = comparator.compare_countries(
            country1,
            country2
        )

        comparator.display_comparison(comparison)

    except CountryNotFoundError as error:
        print(f"Error: {error}")

    except ConnectionError as error:
        print(f"Error: {error}")

    except Exception as error:
        print(f"An unexpected error occurred: {error}")
