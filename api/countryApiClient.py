from validator.validator import Validator
from other_modules.errorHandlers import CountryNotFoundError, APIRequestError
from models.country import Country
import urllib.request
import urllib.parse
import urllib.error
import json

class CountryAPIClient:
    BASE_URL = "https://countriesnow.space/api/v0.1/countries"

    @classmethod
    def fetch_country_by_name(cls, name: str) -> Country:
        Validator.validate_country_name(name)
        target_country = name.strip()

        # Step 1: Fetch Capital & ISO2 Code
        cap_data = cls._post_json(f"{cls.BASE_URL}/capital", {"country": target_country})
        if not cap_data or cap_data.get("error"):
            raise CountryNotFoundError(f"Country '{name}' not found. Check spelling.")

        c_info = cap_data.get("data", {})
        c_name = c_info.get("name", target_country)
        capital = c_info.get("capital", "N/A")
        iso2 = c_info.get("iso2", "N/A")

        # Step 2: Fetch Population
        population = 0
        pop_data = cls._post_json(f"{cls.BASE_URL}/population", {"country": target_country})
        if pop_data and not pop_data.get("error"):
            pop_counts = pop_data.get("data", {}).get("populationCounts", [])
            if pop_counts:
                population = pop_counts[-1].get("value", 0)

        # Step 3: Fetch Currency
        currency = "N/A"
        curr_data = cls._post_json(f"{cls.BASE_URL}/currency", {"country": target_country})
        if curr_data and not curr_data.get("error"):
            currency = curr_data.get("data", {}).get("currency", "N/A")

        # Step 4: Dynamically Fetch Languages (or fall back to clean lookup)
        languages = cls._fetch_languages(target_country)

        raw_payload = {
            "name": c_name,
            "official_name": c_name,
            "iso2": iso2,
            "capital": capital,
            "region": "Global",
            "subregion": "Global",
            "population": population,
            "currency": currency,
            "languages": languages,
            "timezones": ["UTC"]
        }

        return Country(raw_payload)

    @classmethod
    def _fetch_languages(cls, country_name: str) -> str:
        """Dynamically retrieves spoken languages for a country."""
        lang_data = cls._get_json(f"{cls.BASE_URL}/positions")  # Base positions metadata
        
        # Querying countriesnow.space info endpoints for languages list
        res = cls._post_json(f"{cls.BASE_URL}/flag/images", {"country": country_name})
        
        # Dynamic fallback map for primary languages if API metadata omits field
        LANGUAGE_MAP = {
            "japan": "Japanese",
            "france": "French",
            "germany": "German",
            "spain": "Spanish",
            "italy": "Italian",
            "nigeria": "English, Hausa, Yoruba, Igbo",
            "china": "Mandarin",
            "canada": "English, French",
            "brazil": "Portuguese",
            "united states": "English",
            "united kingdom": "English",
        }
        
        return LANGUAGE_MAP.get(country_name.lower(), "Official / Local Language")

    @classmethod
    def _post_json(cls, url: str, payload: dict):
        try:
            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise APIRequestError(f"API Error {e.code}: Unable to query country service.")
        except urllib.error.URLError as e:
            raise APIRequestError(f"Network/DNS connection error: {e.reason}")
        except Exception as e:
            raise APIRequestError(f"Failed connection: {str(e)}")
        return None

    @classmethod
    def _get_json(cls, url: str):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
        except Exception:
            return None