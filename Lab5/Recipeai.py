import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Dict, List, Optional
import requests
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from dotenv import load_dotenv
import os
from datetime import datetime
import re
import logging

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
        self.openai_key = os.getenv("OPENAI_API_KEY")
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
        text = re.sub(r'[^a-zA-Z0-9, ]', '', text).lower()
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
            return response.json().get("results", [])
        except Exception as e:
            logging.error(f"Search error: {e}")
            raise

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
        except Exception as e:
            logging.error(f"Details error for {recipe_id}: {e}")
            raise

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
        self.setup_favorites_tab()

    def setup_search_tab(self):
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Recipe Search")

        # Search Type Selection
        self.search_mode = tk.StringVar(value="howto")
        ttk.Radiobutton(search_frame, text="How to Make...", variable=self.search_mode, 
                       value="howto").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(search_frame, text="Ingredients Search", variable=self.search_mode,
                       value="ingredients").pack(anchor=tk.W, padx=5, pady=2)

        # Main Search Input
        self.search_entry = ttk.Entry(search_frame, width=60)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)

        # Filters Frame
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # Cuisine Filter
        ttk.Label(filter_frame, text="Cuisine:").pack(side=tk.LEFT)
        self.cuisine_var = tk.StringVar()
        self.cuisine_combo = ttk.Combobox(filter_frame, textvariable=self.cuisine_var,
                                        values=list(self.agent.cuisines.keys()))
        self.cuisine_combo.pack(side=tk.LEFT, padx=5)

        # Dietary Filters
        ttk.Label(filter_frame, text="Diet:").pack(side=tk.LEFT, padx=10)
        self.diet_var = tk.StringVar()
        self.diet_combo = ttk.Combobox(filter_frame, textvariable=self.diet_var,
                                      values=list(self.agent.dietary_options.keys()))
        self.diet_combo.pack(side=tk.LEFT)

        # Search Button
        ttk.Button(search_frame, text="Search Recipes", command=self.execute_search).pack(pady=5)

        # Results Display
        self.results_area = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD)
        self.results_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_area.tag_config("title", font=('Arial', 14, 'bold'), foreground='#2c3e50')
        self.results_area.tag_config("subheader", font=('Arial', 12, 'bold'), foreground='#e67e22')
        self.results_area.tag_config("favorite", foreground='blue', underline=1)

    def setup_favorites_tab(self):
        favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(favorites_frame, text="Favorites")

        # Favorites List
        self.favorites_list = tk.Listbox(favorites_frame, height=15)
        self.favorites_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons Frame
        btn_frame = ttk.Frame(favorites_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="View Recipe", command=self.view_favorite).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove", command=self.remove_favorite).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export", command=self.export_favorite).pack(side=tk.RIGHT, padx=2)

        # Favorite Details
        self.fav_details = scrolledtext.ScrolledText(favorites_frame, wrap=tk.WORD)
        self.fav_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.load_favorites()

    def execute_search(self):
        query = self.search_entry.get().strip()
        search_mode = self.search_mode.get()
        cuisine = self.cuisine_var.get()
        diet = self.agent.dietary_options.get(self.diet_var.get())

        try:
            if search_mode == "howto":
                results = self.agent.search_recipes(query=query, cuisine=cuisine, diet=diet)
            else:
                ingredients = self.agent.parse_ingredients(query)
                results = self.agent.search_recipes(ingredients=ingredients, cuisine=cuisine, diet=diet)

            self.current_recipes = []
            for recipe in results:
                try:
                    details = self.agent.get_recipe_details(recipe['id'])
                    self.current_recipes.append(details)
                except Exception as e:
                    logging.error(f"Error loading recipe {recipe['id']}: {e}")

            self.display_results(self.current_recipes)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def display_results(self, recipes: List[Dict]):
        self.results_area.config(state=tk.NORMAL)
        self.results_area.delete(1.0, tk.END)

        for idx, recipe in enumerate(recipes):
            # Header with Favorite button
            self.results_area.insert(tk.END, f"Recipe {idx+1}: {recipe['title']}\n", "title")
            self.results_area.insert(tk.END, "[Add to Favorites]\n", ("favorite", f"fav_{idx}"))
            
            # Basic Info
            self.results_area.insert(tk.END, f"\n⏱ Ready in {recipe.get('readyInMinutes', 'N/A')} minutes")
            self.results_area.insert(tk.END, f" | 🍽 Servings: {recipe.get('servings', 'N/A')}\n\n")

            # Ingredients
            self.results_area.insert(tk.END, "📝 Ingredients:\n", "subheader")
            for ing in recipe.get('extendedIngredients', []):
                self.results_area.insert(tk.END, f"• {ing['original']}\n")

            # Instructions
            self.results_area.insert(tk.END, "\n👩🍳 Instructions:\n", "subheader")
            for instruction in recipe.get('analyzedInstructions', []):
                for step in instruction.get('steps', []):
                    self.results_area.insert(tk.END, f"{step['number']}. {step['step']}\n")

            # Nutrition
            if nutrition := recipe.get('nutrition'):
                self.results_area.insert(tk.END, "\n📊 Nutrition:\n", "subheader")
                nutrients = {n['name']: n['amount'] for n in nutrition.get('nutrients', [])}
                self.results_area.insert(tk.END, 
                    f"Calories: {nutrients.get('Calories', 'N/A')} | "
                    f"Protein: {nutrients.get('Protein', 'N/A')}g | "
                    f"Carbs: {nutrients.get('Carbohydrates', 'N/A')}g | "
                    f"Fat: {nutrients.get('Fat', 'N/A')}g\n"
                )

            self.results_area.insert(tk.END, "\n" + "="*100 + "\n\n")

            # Add tag binding for this recipe
            self.results_area.tag_bind(f"fav_{idx}", "<Button-1>", 
                                      lambda e, r=recipe: self.add_to_favorites(r))

        self.results_area.config(state=tk.DISABLED)

    def add_to_favorites(self, recipe: Dict):
        recipe_id = str(recipe['id'])
        if not hasattr(self, 'favorites'):
            self.favorites = {}

        if recipe_id not in self.favorites:
            self.favorites[recipe_id] = {
                'title': recipe['title'],
                'data': recipe,
                'added': datetime.now().isoformat()
            }
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Success", "Recipe added to favorites!")
        else:
            messagebox.showinfo("Info", "Already in favorites!")

    def save_favorites(self):
        with open('favorites.json', 'w') as f:
            json.dump(self.favorites, f)

    def load_favorites(self):
        try:
            with open('favorites.json', 'r') as f:
                self.favorites = json.load(f)
            self.update_favorites_list()
        except FileNotFoundError:
            self.favorites = {}

    def update_favorites_list(self):
        self.favorites_list.delete(0, tk.END)
        for rid, data in self.favorites.items():
            self.favorites_list.insert(tk.END, data['title'])

    def view_favorite(self):
        if selection := self.favorites_list.curselection():
            recipe_id = list(self.favorites.keys())[selection[0]]
            recipe = self.favorites[recipe_id]['data']
            self.fav_details.config(state=tk.NORMAL)
            self.fav_details.delete(1.0, tk.END)
            self.fav_details.insert(tk.END, f"{recipe['title']}\n\n")
            self.fav_details.insert(tk.END, "Ingredients:\n")
            for ing in recipe.get('extendedIngredients', []):
                self.fav_details.insert(tk.END, f"- {ing['original']}\n")
            self.fav_details.insert(tk.END, "\nInstructions:\n")
            for instr in recipe.get('analyzedInstructions', []):
                for step in instr.get('steps', []):
                    self.fav_details.insert(tk.END, f"{step['number']}. {step['step']}\n")
            self.fav_details.config(state=tk.DISABLED)

    def remove_favorite(self):
        if selection := self.favorites_list.curselection():
            recipe_id = list(self.favorites.keys())[selection[0]]
            del self.favorites[recipe_id]
            self.save_favorites()
            self.update_favorites_list()
            self.fav_details.config(state=tk.NORMAL)
            self.fav_details.delete(1.0, tk.END)
            self.fav_details.config(state=tk.DISABLED)

    def export_favorite(self):
        if selection := self.favorites_list.curselection():
            recipe_id = list(self.favorites.keys())[selection[0]]
            recipe = self.favorites[recipe_id]['data']
            filename = f"{recipe['title'].replace(' ', '_')}.txt"
            with open(filename, 'w') as f:
                f.write(f"Recipe: {recipe['title']}\n\n")
                f.write("Ingredients:\n")
                for ing in recipe.get('extendedIngredients', []):
                    f.write(f"- {ing['original']}\n")
                f.write("\nInstructions:\n")
                for instr in recipe.get('analyzedInstructions', []):
                    for step in instr.get('steps', []):
                        f.write(f"{step['number']}. {step['step']}\n")
            messagebox.showinfo("Exported", f"Recipe saved as {filename}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = RecipeGUI()
        app.run()
    except Exception as e:
        logging.error(f"Critical error: {e}")
        messagebox.showerror("Fatal Error", "Application cannot start. Check logs for details.")