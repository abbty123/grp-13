from models.RelocationGuide import RelocationGuide
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from api.countryApiClient import CountryAPIClient
from other_modules.errorHandlers import *
from other_modules.LocalStorage import LocalStorage
from other_modules.CountryComparator import CountryComparator

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Global Gateway - Travel & Relocation Assistant")
        self.geometry("850x650")
        
        self.ai_service = RelocationGuide()
        self.current_country = None
        self.c1_data = None
        self.c2_data = None

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Search & AI Guide
        self.tab_search = ttk.Frame(notebook)
        notebook.add(self.tab_search, text="Country Lookup & Guide")
        self._setup_search_tab()

        # Tab 2: Country Comparison
        self.tab_compare = ttk.Frame(notebook)
        notebook.add(self.tab_compare, text="Compare Countries")
        self._setup_compare_tab()

    # --- TAB 1 SETUP ---
    def _setup_search_tab(self):
        frame_top = ttk.Frame(self.tab_search)
        frame_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_top, text="Country Name:").pack(side="left", padx=5)
        self.ent_search = ttk.Entry(frame_top, width=25)
        self.ent_search.pack(side="left", padx=5)
        
        btn_search = ttk.Button(frame_top, text="Search", command=self._on_search)
        btn_search.pack(side="left", padx=5)

        ttk.Label(frame_top, text="Purpose:").pack(side="left", padx=(15, 5))
        self.combo_purpose = ttk.Combobox(frame_top, values=["travel", "study", "relocation"], state="readonly", width=10)
        self.combo_purpose.set("travel")
        self.combo_purpose.pack(side="left", padx=5)

        btn_ai = ttk.Button(frame_top, text="Generate AI Guide", command=self._on_generate_guide)
        btn_ai.pack(side="left", padx=5)

        self.lbl_details = ttk.Label(self.tab_search, text="Search for a country to display information.", font=("Helvetica", 10), justify="left")
        self.lbl_details.pack(anchor="w", padx=15, pady=5)

        self.txt_guide = scrolledtext.ScrolledText(self.tab_search, wrap="word", height=18)
        self.txt_guide.pack(fill="both", expand=True, padx=10, pady=5)

        btn_save = ttk.Button(self.tab_search, text="Save Profile & Guide Locally", command=self._on_save_profile)
        btn_save.pack(anchor="e", padx=10, pady=5)

    def _on_search(self):
        query = self.ent_search.get()
        try:
            country = CountryAPIClient.fetch_country_by_name(query)
            self.current_country = country
            
            info = (
                f"{country.flag_emoji} {country.name.upper()} ({country.official_name})\n"
                f"Capital: {country.capital} | Region: {country.region} ({country.subregion})\n"
                f"Population: {country.population:,} | Currencies: {country.currency}\n"
                f"Languages: {country.languages} | Timezones: {', '.join(country.timezones)}"
            )
            self.lbl_details.config(text=info)
            self.txt_guide.delete("1.0", tk.END)
            self.txt_guide.insert(tk.END, "Click 'Generate AI Guide' to get customized travel/relocation tips.")
        
        except (InvalidInputError, CountryNotFoundError, APIRequestError) as e:
            messagebox.showerror("Error", str(e))

    def _on_generate_guide(self):
        if not self.current_country:
            messagebox.showwarning("Warning", "Please search and select a country first.")
            return
        
        purpose = self.combo_purpose.get()
        self.txt_guide.delete("1.0", tk.END)
        self.txt_guide.insert(tk.END, "Generating AI Guide via Gemini API...\n")
        self.update_idletasks()

        try:
            guide = self.ai_service.generate_guide(self.current_country, purpose)
            self.txt_guide.delete("1.0", tk.END)
            self.txt_guide.insert(tk.END, guide)
        except APIRequestError as e:
            messagebox.showerror("API Error", str(e))

    def _on_save_profile(self):
        if not self.current_country:
            messagebox.showwarning("Warning", "No active country selected to save.")
            return
        
        guide_content = self.txt_guide.get("1.0", tk.END).strip()
        try:
            LocalStorage.save_profile(self.current_country, guide_content)
            messagebox.showinfo("Success", f"Profile for {self.current_country.name} saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")

    # --- TAB 2 SETUP ---
    def _setup_compare_tab(self):
        frame_inputs = ttk.Frame(self.tab_compare)
        frame_inputs.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_inputs, text="Country 1:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_c1 = ttk.Entry(frame_inputs, width=15)
        self.ent_c1.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_inputs, text="Country 2:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_c2 = ttk.Entry(frame_inputs, width=15)
        self.ent_c2.grid(row=0, column=3, padx=5, pady=5)

        btn_compare = ttk.Button(frame_inputs, text="Compare Side-by-Side", command=self._on_compare)
        btn_compare.grid(row=0, column=4, padx=10, pady=5)

        self.txt_compare = scrolledtext.ScrolledText(self.tab_compare, wrap="word", height=20)
        self.txt_compare.pack(fill="both", expand=True, padx=10, pady=5)

        btn_save_comp = ttk.Button(self.tab_compare, text="Export Comparison Report", command=self._on_save_comparison)
        btn_save_comp.pack(anchor="e", padx=10, pady=5)

    def _on_compare(self):
        c1_name = self.ent_c1.get()
        c2_name = self.ent_c2.get()

        try:
            self.c1_data = CountryAPIClient.fetch_country_by_name(c1_name)
            self.c2_data = CountryAPIClient.fetch_country_by_name(c2_name)
            
            tz_info = CountryComparator.calculate_tz_difference(self.c1_data, self.c2_data)
            checklist = CountryComparator.generate_checklist(self.c2_data)

            report = (
                f"=== COMPARISON: {self.c1_data.name} vs {self.c2_data.name} ===\n\n"
                f"METRIC\t\t{self.c1_data.name}\t\t{self.c2_data.name}\n"
                f"{'-'*60}\n"
                f"Capital:\t\t{self.c1_data.capital}\t\t{self.c2_data.capital}\n"
                f"Region:\t\t{self.c1_data.region}\t\t{self.c2_data.region}\n"
                f"Population:\t\t{self.c1_data.population:,}\t\t{self.c2_data.population:,}\n"
                f"Currency:\t\t{self.c1_data.currency}\t\t{self.c2_data.currency}\n"
                f"Languages:\t\t{self.c1_data.languages}\t\t{self.c2_data.languages}\n\n"
                f"TIMEZONE DIFFERENCE:\n{tz_info}\n\n"
                f"BEFORE YOU TRAVEL CHECKLIST ({self.c2_data.name}):\n" +
                "\n".join([f"  [ ] {item}" for item in checklist])
            )

            self.txt_compare.delete("1.0", tk.END)
            self.txt_compare.insert(tk.END, report)

        except (InvalidInputError, CountryNotFoundError, APIRequestError) as e:
            messagebox.showerror("Comparison Error", str(e))

    def _on_save_comparison(self):
        if not self.c1_data or not self.c2_data:
            messagebox.showwarning("Warning", "No active comparison to export.")
            return
        
        report_text = self.txt_compare.get("1.0", tk.END).strip()
        try:
            LocalStorage.save_comparison(self.c1_data, self.c2_data, report_text)
            messagebox.showinfo("Success", "Comparison report saved locally!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save comparison: {str(e)}")