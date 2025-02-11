import re
import json
from typing import Dict, List
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MovieAgent:
    def __init__(self):  # FIXED: Corrected __init__ method
        self.disclaimer = """
        Movie recommendations are subjective and based on available data.
        Ratings and availability may vary by region and platform.
        """
        
        # Enhanced system prompt for focused movie recommendations
        movie_system_prompt = """You are a movie recommendation assistant specializing in providing detailed film suggestions.
        Your responses must:
        1. Provide relevant movie recommendations based on user preferences
        2. Include movie details (year, director, genre, runtime)
        3. Consider similar movies and thematic connections
        4. Include critic and audience ratings when available
        5. Provide content warnings and age ratings
        6. Note streaming availability when relevant
        7. Indicate confidence level based on match with user preferences
        
        If a query is not movie-related, respond with: "This query falls outside the scope of movie recommendations."
        
        Structure your responses as JSON with recommendations, details, and reasoning fields."""

        # Initialize Phi agent with Groq and movie recommendation prompt
        self.agent = Agent(
            model=Groq(),
            system_prompt=movie_system_prompt
        )

        # Comprehensive movie categories and keywords
        self.categories = {
            "genre": [
                "action", "comedy", "drama", "horror", "thriller", "sci-fi",
                "fantasy", "romance", "documentary", "animation", "western",
                "musical", "crime", "adventure", "mystery"
            ],
            "mood": [
                "happy", "sad", "tense", "uplifting", "dark", "thought-provoking",
                "heartwarming", "scary", "funny", "inspiring", "relaxing"
            ],
            "era": [
                "classic", "modern", "80s", "90s", "2000s", "2010s", "2020s",
                "silent era", "golden age", "new wave"
            ],
            "audience": [
                "family", "kids", "teen", "adult", "all ages", "mature",
                "parental guidance", "restricted"
            ],
            "technical": [
                "special effects", "cinematography", "soundtrack", "acting",
                "directing", "screenplay", "visuals", "practical effects"
            ]
        }

    def validate_movie_query(self, query: str) -> bool:
        """Validate if the query is movie-related."""
        movie_indicators = [
            "movie", "film", "watch", "cinema", "show", "actor", "director",
            "genre", "plot", "recommendation", "similar to", "like"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in movie_indicators)

    def preprocess_query(self, query: str) -> str:
        """Clean and standardize the input query."""
        query = re.sub(r'[^\w\s]', ' ', query)
        return ' '.join(query.split()).lower()

    def identify_preferences(self, query: str) -> Dict[str, float]:
        """Identify relevant movie preferences with confidence scores."""
        query = self.preprocess_query(query)
        scores = {}
        for category, keywords in self.categories.items():
            matches = sum(1 for kw in keywords if kw in query)
            total_keywords = len(keywords)
            scores[category] = matches / total_keywords if matches > 0 else 0
        return scores

    def generate_response(self, query: str) -> Dict:
        """Generate movie recommendations using Phi agent with Groq."""
        try:
            # First validate if query is movie-related
            if not self.validate_movie_query(query):
                return {
                    "error": "This query appears to be outside the scope of movie recommendations. Please provide a movie-related question."
                }

            # Identify relevant preferences
            preferences = self.identify_preferences(query)
            relevant_categories = [cat for cat, score in preferences.items() if score > 0]

            # Prepare the enhanced movie recommendation prompt
            prompt = f"""Movie recommendation request: {query}

            Relevant categories: {', '.join(relevant_categories) if relevant_categories else 'general movies'}

            Provide detailed movie recommendations including:
            1. Movie titles with year and director
            2. Genre and thematic elements
            3. Brief plot synopsis (no spoilers)
            4. Ratings and reviews
            5. Content warnings and age rating
            
            Structure your response as JSON:
            {{
                "recommendations": [
                    {{
                        "title": "movie title",
                        "year": "year",
                        "director": "director name",
                        "genre": ["genre1", "genre2"],
                        "synopsis": "brief plot summary",
                        "rating": "age rating",
                        "content_warnings": ["warning1", "warning2"],
                        "streaming": ["platform1", "platform2"]
                    }}
                ],
                "reasoning": "explanation for recommendations",
                "confidence": 0.x,
                "alternative_suggestions": ["movie1", "movie2"]
            }}"""
            
            # Get response from Phi agent
            response = self.agent.run(prompt)

            # FIXED: Parse response safely
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                data = {
                    "recommendations": [],
                    "reasoning": "Response parsing error. Original response: " + response[:200] + "...",
                    "confidence": 0.5,
                    "alternative_suggestions": []
                }

            return {
                "recommendations": data.get("recommendations", []),
                "reasoning": data.get("reasoning", "No explanation provided"),
                "confidence": data.get("confidence", 0.5),
                "alternative_suggestions": data.get("alternative_suggestions", []),
                "categories": relevant_categories,
                "disclaimer": self.disclaimer
            }

        except Exception as e:
            return {"error": f"Error processing movie recommendation query: {str(e)}"}

# FIXED: Proper indentation for main()
def main():
    agent = MovieAgent()
    print("Movie Recommendation Assistant (type 'quit' to exit)")
    print("Please describe what kind of movie you're looking for!")

    while True:
        query = input("\nYour movie request: ")
        if query.lower() in ['quit', 'exit']:
            break

        response = agent.generate_response(query)

        if 'error' in response:
            print(f"\nError: {response['error']}")
            continue

        print("\nRecommendations:")
        for movie in response['recommendations']:
            print(f"\nTitle: {movie['title']} ({movie['year']})")
            print(f"Director: {movie['director']}")
            print(f"Genre: {', '.join(movie['genre'])}")
            print(f"Synopsis: {movie['synopsis']}")
            print(f"Rating: {movie['rating']}")
            print(f"Content Warnings: {', '.join(movie['content_warnings'])}")
            print(f"Available on: {', '.join(movie['streaming'])}")

        if response['alternative_suggestions']:
            print("\nYou might also like:")
            print(", ".join(response['alternative_suggestions']))

        print(f"\nConfidence Score: {response['confidence']:.2f}/1.0")
        print("\nReasoning:", response['reasoning'])
        print("\nDisclaimer:", response['disclaimer'])

# FIXED: Corrected main() execution
if __name__ == "__main__":
    main()
