import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Dict, List
import requests
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from dotenv import load_dotenv
import os
from datetime import datetime
import re
import logging
import sys
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='recipe_agent.log'
)

class RecipeAgent:
    def __init__(self):
        load_dotenv()
        self.setup_apis()
        self.setup_ingredient_parser()
        self.setup_cuisines()
        self.setup_dietary_preferences()

    def setup_apis(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")  # Fixed environment variable name
        self.model_name = "gpt-3.5-turbo"
        self.spoonacular_key = os.getenv("SPOONACULAR_API_KEY")
        self.spoonacular_base_url = "https://api.spoonacular.com/recipes"

        if not self.openai_key or not self.spoonacular_key:
            raise ValueError("Missing required API keys in .env file")

        try:
            self.gpt_agent = Agent(model=OpenAIChat(model=self.model_name))
            logging.info("GPT Agent initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing GPT agent: {e}")
            self.gpt_agent = None

    def setup_cuisines(self):
        self.cuisines = {
            "Indian": ["Biryani", "Curry", "Tandoori", "Dosa"],
            "Italian": ["Pasta", "Pizza", "Risotto", "Lasagna"],
            "Mexican": ["Tacos", "Enchiladas", "Guacamole", "Quesadillas"],
            "Japanese": ["Sushi", "Ramen", "Tempura", "Udon"]
        }

    def setup_dietary_preferences(self):
        self.dietary_options = {
            "Vegetarian": "vegetarian",
            "Vegan": "vegan",
            "Gluten-Free": "gluten free",
            "Dairy-Free": "dairy free"
        }

    def setup_ingredient_parser(self):
        self.ingredient_patterns = {
            'quantity': r'(\d+(?:/\d+)?(?:\s*-\s*\d+(?:/\d+)?)?)',
            'unit': r'(cup|tbsp|tsp|oz|g|kg|ml|l|pound|ounce|gram|liter)',
            'prep': r'(chopped|diced|minced|sliced|grated)'
        }

    def parse_ingredients(self, ingredients_input: str) -> List[str]:
        text = re.sub(r'\b(how to make|recipe for|i need|please)\b', '', ingredients_input, flags=re.IGNORECASE)
        text = re.sub(r'[^a-zA-Z0-9,/. ]', '', text).lower()  # Fixed regex to retain fractions and decimals
        return [ing.strip() for ing in text.split(',') if ing.strip()]

    def search_recipes(self, query: str = None, ingredients: List[str] = None, cuisine: str = None, diet: str = None) -> List[Dict]:
        try:
            params = {
                "apiKey": self.spoonacular_key,
                "number": 5,
                "instructionsRequired": True,
                "addRecipeInformation": True
            }

            if query:
                params["query"] = query
            if ingredients:
                params["includeIngredients"] = ",".join(ingredients)
                params["ranking"] = 1
            if cuisine:
                params["cuisine"] = cuisine
            if diet:
                params["diet"] = diet

            response = requests.get(f"{self.spoonacular_base_url}/complexSearch", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            return data.get("results", [])
        except requests.RequestException as e:
            logging.error(f"API request error: {e}")
            return []

    def get_recipe_details(self, recipe_id: int) -> Dict:
        try:
            params = {"apiKey": self.spoonacular_key}
            response = requests.get(
                f"{self.spoonacular_base_url}/{recipe_id}/information",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Details error for {recipe_id}: {e}")
            return {}

class RecipeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Recipe Master 2.0")
        self.root.geometry("1200x800")
        self.agent = RecipeAgent()
        self.current_recipes = []
        self.setup_gui()

    def setup_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_search_tab()

    def setup_search_tab(self):
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Recipe Search")

        self.search_entry = ttk.Entry(search_frame, width=60)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(search_frame, text="Search Recipes", command=self.execute_search).pack(pady=5)

        self.results_area = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD)
        self.results_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def execute_search(self):
        query = self.search_entry.get().strip()

        try:
            results = self.agent.search_recipes(query=query)
            self.current_recipes = [self.agent.get_recipe_details(recipe['id']) for recipe in results if 'id' in recipe]

            self.display_results(self.current_recipes)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def display_results(self, recipes: List[Dict]):
        self.results_area.config(state=tk.NORMAL)
        self.results_area.delete(1.0, tk.END)

        for idx, recipe in enumerate(recipes):
            self.results_area.insert(tk.END, f"Recipe {idx+1}: {recipe.get('title', 'Unknown')}\n", "title")

            self.results_area.insert(tk.END, f"\n⏱ Ready in {recipe.get('readyInMinutes', 'N/A')} minutes\n")

            self.results_area.insert(tk.END, "📝 Ingredients:\n", "subheader")
            for ing in recipe.get('extendedIngredients', []):
                self.results_area.insert(tk.END, f"• {ing.get('original', 'N/A')}\n")

            self.results_area.insert(tk.END, "\n👩🍳 Instructions:\n", "subheader")
            for instruction in recipe.get('analyzedInstructions', []):
                for step in instruction.get('steps', []):
                    self.results_area.insert(tk.END, f"{step.get('number', '?')}. {step.get('step', 'No instructions')}\n")

            if 'nutrition' in recipe and isinstance(recipe['nutrition'], dict):
                self.results_area.insert(tk.END, "\n📊 Nutrition:\n", "subheader")
                nutrients = {n['name']: n['amount'] for n in recipe['nutrition'].get('nutrients', [])}
                self.results_area.insert(tk.END, f"Calories: {nutrients.get('Calories', 'N/A')} | Protein: {nutrients.get('Protein', 'N/A')}g\n")

            self.results_area.insert(tk.END, "\n" + "="*100 + "\n\n")

        self.results_area.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = RecipeGUI()
        app.run()
    except Exception:
        error_msg = traceback.format_exc()
        logging.error(f"Critical error: {error_msg}")
        sys.exit("Application failed. See logs.")
