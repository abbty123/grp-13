import os

from country_api_module.country_data import get_country

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
        f"Create a concise, actionable 'Before You Travel' checklist for {country['name']}.\n\n"
        f"Use only these country facts: {format_country_data(country)}\n\n"
        "Organize the checklist under Documents and entry, Health and safety, "
        "Money and communication, Transport and accommodation, and Packing. "
        "Use checkbox-style items, flag facts that must be verified with official sources, "
        "and do not invent prices, laws, or visa eligibility."
    )


def format_country_data(country):
    """Return the shared country facts used by every guidance prompt."""
    return (
        f"official_name={country['official_name']}; capital={country['capital']}; "
        f"region={country['region']}; subregion={country['subregion']}; "
        f"population={country['population']}; currency={country['currency']}; "
        f"language={country['language']}; timezone={country['timezone']}; "
        f"best_time={country['best_time']}; safety={country['safety']}; "
        f"climate={country['climate']}; visa_note={country['visa_note']}; "
        f"highlights={', '.join(country['highlights'])}; "
        f"description={country['description']}"
    )


def build_relocation_prompt(country_name):
    country = get_country(country_name)
    if not country:
        return "Please select a valid country name."

    return (
        f"Create a practical relocation guide for {country['name']} using only these facts:\n"
        f"{format_country_data(country)}\n\n"
        "Cover the first 90 days, entry and immigration questions to verify, housing and "
        "transport considerations, language and cultural preparation, budgeting categories, "
        "health and safety, and a prioritized arrival checklist. Clearly label assumptions "
        "and items requiring official local verification. Do not invent legal requirements, "
        "costs, employers, schools, or neighborhoods."
    )
