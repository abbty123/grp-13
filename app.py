"""Streamlit application for country research, comparison, and planning."""

from pathlib import Path

import streamlit as st

from ai import (
    build_checklist_prompt,
    build_country_prompt,
    build_relocation_prompt,
    generate_before_you_travel,
    generate_country_guide,
)
from country_api_module.country_data import get_country, list_countries
from country_comparator import CountryComparator
from file_storage import CountryFileStorage


st.set_page_config(
    page_title="Country Compass",
    page_icon="🌍",
    layout="wide",
)

STORAGE_PATH = Path(__file__).with_name("country_profiles.json")


@st.cache_resource
def get_storage():
    return CountryFileStorage(STORAGE_PATH)


def country_selector(label, key):
    return st.selectbox(label, list_countries(), key=key)


def render_profile(country):
    st.subheader(f"{country['flag']} {country['name']}")
    st.write(country["description"])
    columns = st.columns(3)
    facts = [
        ("Capital", country["capital"]),
        ("Region", f"{country['region']} | {country['subregion']}"),
        ("Population", country["population"]),
        ("Currency", country["currency"]),
        ("Language", country["language"]),
        ("Timezone", country["timezone"]),
    ]
    for index, (label, value) in enumerate(facts):
        columns[index % 3].metric(label, value)

    st.write(f"**Climate:** {country['climate']}  |  **Safety:** {country['safety']}")
    st.write(f"**Highlights:** {', '.join(country['highlights'])}")


def render_home(storage):
    st.title("Country Compass")
    st.caption("Explore country profiles, compare options, and save practical plans.")
    selected_name = country_selector("Choose a country", "home_country")
    country = get_country(selected_name)
    render_profile(country)
    if st.button("Save to favourites", type="primary"):
        storage.save_favourite_country(country)
        st.success(f"{country['name']} is saved to your favourites.")


def build_local_comparison(country1, country2):
    comparator = CountryComparator()
    return {
        "country1": country1,
        "country2": country2,
        "timezone_difference": comparator.calculate_timezone_difference(
            country1["timezone"], country2["timezone"]
        ),
    }


def render_comparison(storage):
    st.title("Compare Countries")
    first, second = st.columns(2)
    with first:
        first_name = country_selector("First country", "comparison_first")
    with second:
        second_name = country_selector("Second country", "comparison_second")

    if first_name == second_name:
        st.warning("Choose two different countries to compare.")
        return
    comparison = build_local_comparison(get_country(first_name), get_country(second_name))
    left, right = st.columns(2)
    with left:
        render_profile(comparison["country1"])
    with right:
        render_profile(comparison["country2"])
    st.info(
        f"Timezone difference ({second_name} compared with {first_name}): "
        f"{comparison['timezone_difference']}"
    )
    if st.button("Save comparison"):
        storage.save_comparison_result(comparison)
        st.success("Comparison saved.")


def render_guidance(storage):
    st.title("Planning Studio")
    country_name = country_selector("Target country", "guide_country")
    guide_type = st.radio(
        "Plan type", ["Travel guide", "Travel checklist", "Relocation guide"],
        horizontal=True,
    )
    country = get_country(country_name)

    if guide_type == "Travel checklist":
        checklist = generate_before_you_travel(country_name)
        for item in checklist:
            st.checkbox(item, key=f"checklist_{country_name}_{item}")
        with st.expander("View checklist prompt"):
            st.code(build_checklist_prompt(country_name))
        if st.button("Save checklist"):
            storage.save_travel_checklist(country_name, checklist)
            st.success("Checklist saved.")
        return

    selected_type = "relocation" if guide_type == "Relocation guide" else "travel"
    if st.button("Generate guidance", type="primary"):
        with st.spinner("Preparing country-specific guidance..."):
            guide = generate_country_guide(country_name, selected_type)
        st.session_state["current_guide"] = guide
        st.session_state["current_guide_country"] = country_name
        st.session_state["current_guide_type"] = selected_type

    guide = st.session_state.get("current_guide")
    if guide:
        st.markdown(guide)
        with st.expander("View source prompt"):
            prompt = (
                build_relocation_prompt(country_name)
                if selected_type == "relocation"
                else build_country_prompt(country_name, selected_type)
            )
            st.code(prompt)
        if selected_type == "relocation" and st.button("Save guide"):
            storage.save_relocation_guide(country_name, guide)
            st.success("Relocation guide saved.")
    else:
        st.write(country["description"])


def render_saved(storage):
    st.title("Saved Plans")
    favourites = storage.get_favourite_countries()
    comparisons = storage.get_comparison_results()
    checklists = storage.get_travel_checklists()
    guides = storage.get_relocation_guides()
    st.metric("Favourite countries", len(favourites))
    tabs = st.tabs(["Favourites", "Comparisons", "Checklists", "Relocation guides"])
    with tabs[0]:
        for country in favourites:
            st.write(f"{country.get('flag', '')} **{country['name']}** - {country.get('description', '')}")
    with tabs[1]:
        for item in comparisons:
            first = item["content"]["country1"]["name"]
            second = item["content"]["country2"]["name"]
            st.write(f"**{first} vs {second}** | {item['saved_at']}")
    with tabs[2]:
        for item in checklists:
            st.write(f"**{item['countries'][0]}** | {item['saved_at']}")
            st.write(item["content"])
    with tabs[3]:
        for item in guides:
            st.write(f"**{item['countries'][0]}** | {item['saved_at']}")
            st.markdown(item["content"])


def main():
    storage = get_storage()
    st.sidebar.title("Country Compass")
    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Compare", "Planning Studio", "Saved Plans"],
    )
    if page == "Home":
        render_home(storage)
    elif page == "Compare":
        render_comparison(storage)
    elif page == "Planning Studio":
        render_guidance(storage)
    else:
        render_saved(storage)


if __name__ == "__main__":
    main()