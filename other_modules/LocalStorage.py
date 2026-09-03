import os
import json
from models.country import Country
import datetime

class LocalStorage:
    DATA_DIR = "saved_data"

    @classmethod
    def init_storage(cls):
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)

    @classmethod
    def save_profile(cls, country: Country, guide_text: str = ""):
        cls.init_storage()
        filename = os.path.join(cls.DATA_DIR, f"{country.cca2}_profile.json")
        payload = {
            "country": country.to_dict(),
            "guide": guide_text,
            "saved_at": datetime.now().isoformat()
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    @classmethod
    def save_comparison(cls, c1: Country, c2: Country, comparison_summary: str):
        cls.init_storage()
        filename = os.path.join(cls.DATA_DIR, f"Compare_{c1.cca2}_VS_{c2.cca2}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=== COUNTRY COMPARISON REPORT ===\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(comparison_summary)