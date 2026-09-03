import os

from country_data import get_country

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


def build_country_prompt(country_name, guide_type="travel"):
    country = get_country(country_name)
    if not country:
        return "Please select a valid country name."

    guide_type = (guide_type or "travel").strip().lower()
    guide_types = {
        "travel": "a travel guide",
        "study": "a study abroad guide",
        "relocation": "a relocation guide",
    }
    guide_label = guide_types.get(guide_type, "a practical guide")

    prompt = f"""
You are a helpful international travel advisor.
Using only the country data below, create {guide_label} for {country['name']}.

Country data:
- Official name: {country['official_name']}
- Capital: {country['capital']}
- Region: {country['region']}
- Subregion: {country['subregion']}
- Population: {country['population']}
- Currency: {country['currency']}
- Language: {country['language']}
- Timezone: {country['timezone']}
- Best time to visit: {country['best_time']}
- Safety: {country['safety']}
- Climate: {country['climate']}
- Visa note: {country['visa_note']}
- Highlights: {', '.join(country['highlights'])}
- Description: {country['description']}

Give useful guidance with:
1. A short overview
2. Top experiences or opportunities
3. Practical preparation tips
4. What to expect for daily life
5. Travel, study, or relocation-specific advice
6. A brief final recommendation

Keep it concise, realistic, and tailored to the country data.
""".strip()
    return prompt


def generate_country_guide(country_name, guide_type="travel", api_key=None):
    country = get_country(country_name)
    if not country:
        return "Please pick a valid country name before generating a guide."

    prompt = build_country_prompt(country_name, guide_type)

    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key and genai is not None:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            pass

    return (
        f"{country['name']} overview:\n\n"
        f"{country['description']}\n\n"
        f"Best time to visit: {country['best_time']}\n"
        f"Capital: {country['capital']}\n"
        f"Highlights: {', '.join(country['highlights'])}\n\n"
        f"Practical advice: Prepare your passport, check visa requirements, review local transport options, and plan around the climate and travel season."
    )


def generate_before_you_travel(country_name):
    country = get_country(country_name)
    if not country:
        return ["Please select a valid country. "]

    return [
        f"Confirm your passport and entry documents for {country['name']}.",
        f"Review the visa guidance: {country['visa_note']}",
        f"Check the best travel window: {country['best_time']}",
        f"Plan accommodation and local transport around {country['capital']}",
        f"Pack for the expected climate: {country['climate']}",
        "Keep emergency contact info and travel insurance details handy.",
        "Research local customs, cash usage, and any required health information.",
    ]


def build_checklist_prompt(country_name):
    country = get_country(country_name)
    if not country:
        return "Please select a valid country name."

    return (
        f"Create a concise 'Before You Travel' checklist for {country['name']} using these facts: "
        f"capital={country['capital']}, visa_note={country['visa_note']}, best_time={country['best_time']}, "
        f"climate={country['climate']}, safety={country['safety']}, language={country['language']}. "
        "Include practical items for passport, visa, packing, transport, money, and safety."
    )
