from google import genai
from google.genai.errors import APIError
import os
from models.country import Country
from other_modules.errorHandlers import APIRequestError

class RelocationGuide:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate_guide(self, country: Country, purpose: str = "travel") -> str:
        if not self.client:
            return (
                f"[AI Guide Placeholder - API Key Missing]\n\n"
                f"Guide for {purpose.capitalize()}ing to {country.name}:\n"
                f"- Ensure passport validity for {country.name}.\n"
                f"- Prepare funds in {country.currency}.\n"
                f"- Learn basic phrases in {country.languages}.\n"
                f"- Timezone to adjust: {', '.join(country.timezones)}"
            )

        prompt = (
            f"Create a concise, structured {purpose} guide for someone planning to go to {country.name}.\n"
            f"Details: Capital: {country.capital}, Currency: {country.currency}, "
            f"Languages: {country.languages}, Region: {country.region}, Timezones: {', '.join(country.timezones)}.\n"
            f"Include 3 sections: 1. Overview & Culture, 2. Financial & Legal Prep, 3. Essential Tips."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except APIError as e:
            raise APIRequestError(f"Gemini API Error: {e.message}")
        except Exception as e:
            raise APIRequestError(f"AI Generation Failed: {str(e)}")
