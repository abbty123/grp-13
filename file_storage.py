"""JSON file storage for saved country planning artifacts."""

import json
from datetime import datetime, timezone
from pathlib import Path


class CountryFileStorage:
    """Persist favourites, comparisons, checklists, and relocation guides."""

    EMPTY_STORE = {
        "favourite_countries": [],
        "comparison_results": [],
        "travel_checklists": [],
        "relocation_guides": [],
    }

    def __init__(self, file_path="country_profiles.json"):
        self.file_path = Path(file_path)

    def _read(self):
        if not self.file_path.exists():
            return {key: list(value) for key, value in self.EMPTY_STORE.items()}

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(
                f"Unable to read country profile file: {self.file_path}"
            ) from error

        if not isinstance(data, dict):
            raise ValueError("Country profile file must contain a JSON object.")

        store = {key: list(value) for key, value in self.EMPTY_STORE.items()}
        for key in store:
            if key in data:
                if not isinstance(data[key], list):
                    raise ValueError(f"'{key}' must be a JSON list.")
                store[key] = data[key]
        return store

    def _write(self, store):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(store, file, indent=2, ensure_ascii=False)
                file.write("\n")
            temporary_path.replace(self.file_path)
        except OSError as error:
            raise OSError(
                f"Unable to write country profile file: {self.file_path}"
            ) from error

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).isoformat()

    def _save_artifact(self, collection, value, country_names=None):
        store = self._read()
        record = {
            "id": len(store[collection]) + 1,
            "saved_at": self._timestamp(),
            "countries": country_names or [],
            "content": value,
        }
        store[collection].append(record)
        self._write(store)
        return record

    def save_favourite_country(self, country):
        """Save a country profile once and return the stored profile."""
        store = self._read()
        country_name = country.get("name") if isinstance(country, dict) else country
        if not country_name:
            raise ValueError("A country name is required.")

        for saved in store["favourite_countries"]:
            saved_name = saved.get("name") if isinstance(saved, dict) else saved
            if str(saved_name).casefold() == str(country_name).casefold():
                return saved

        profile = dict(country) if isinstance(country, dict) else {"name": country}
        profile["saved_at"] = self._timestamp()
        store["favourite_countries"].append(profile)
        self._write(store)
        return profile

    def get_favourite_countries(self):
        return self._read()["favourite_countries"]

    get_favorite_countries = get_favourite_countries

    def remove_favourite_country(self, country_name):
        store = self._read()
        original = len(store["favourite_countries"])
        store["favourite_countries"] = [
            country for country in store["favourite_countries"]
            if country.get("name", "").casefold() != country_name.casefold()
        ]
        if len(store["favourite_countries"]) == original:
            return False
        self._write(store)
        return True

    def save_comparison_result(self, comparison):
        countries = [
            comparison.get("country1", {}).get("name"),
            comparison.get("country2", {}).get("name"),
        ]
        return self._save_artifact("comparison_results", comparison, countries)

    def get_comparison_results(self):
        return self._read()["comparison_results"]

    def save_travel_checklist(self, country_name, checklist):
        return self._save_artifact("travel_checklists", checklist, [country_name])

    def get_travel_checklists(self):
        return self._read()["travel_checklists"]

    def save_relocation_guide(self, country_name, guide):
        return self._save_artifact("relocation_guides", guide, [country_name])

    def get_relocation_guides(self):
        return self._read()["relocation_guides"]

    def get_saved(self, artifact_type):
        collection = f"{artifact_type}s"
        if collection not in self.EMPTY_STORE:
            raise ValueError(
                "artifact_type must be one of: comparison_result, "
                "travel_checklist, relocation_guide"
            )
        return self._read()[collection]
