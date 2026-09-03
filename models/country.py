from other_modules.errorHandlers import APIRequestError

class Country:
    def __init__(self, raw_data: dict):
        try:
            self.name = raw_data.get("name", "Unknown")
            self.official_name = raw_data.get("official_name", self.name)
            self.cca2 = raw_data.get("iso2", "N/A")
            self.capital = raw_data.get("capital", "N/A")
            self.region = raw_data.get("region", "N/A")
            self.subregion = raw_data.get("subregion", "N/A")
            self.population = raw_data.get("population", 0)
            self.currency = raw_data.get("currency", "N/A")
            self.languages = raw_data.get("languages", "N/A")
            
            timezones = raw_data.get("timezones", [])
            self.timezones = timezones if isinstance(timezones, list) and timezones else ["UTC"]
            
            self.flag_emoji = raw_data.get("flag", "🏳️")
            self.flag_png = raw_data.get("flags", {}).get("png", "")
        except Exception as e:
            raise APIRequestError(f"Error parsing country data: {str(e)}")

    def to_dict(self) -> dict:
        """Helper method to serialize the object for LocalStorage saving."""
        return {
            "name": self.name,
            "official_name": self.official_name,
            "cca2": self.cca2,
            "capital": self.capital,
            "region": self.region,
            "subregion": self.subregion,
            "population": self.population,
            "currency": self.currency,
            "languages": self.languages,
            "timezones": self.timezones,
            "flag": self.flag_emoji,
            "flag_png": self.flag_png
        }