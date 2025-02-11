import re
import json
from typing import Dict, List
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LegalAgent:
    def __init__(self):
        self.disclaimer = """
        This information is provided for educational purposes only and does not constitute legal advice. 
        Please consult with a qualified attorney for advice specific to your situation.
        """
        
        # Enhanced system prompt for stricter legal domain focus
        legal_system_prompt = """You are a legal information assistant specializing in providing factual legal information and references.
        Your responses must:
        1. Only address legal questions and legal implications
        2. Always include relevant legal statutes, regulations, or case law when available
        3. Clearly distinguish between established law and legal interpretation
        4. Provide jurisdiction-specific information when relevant
        5. Include citations to legal sources
        6. Flag any areas where state/local laws may vary significantly
        7. Indicate confidence level based on clarity of established law
        
        If a question is not legal in nature, respond with: "This query falls outside the scope of legal information."
        
        Structure your responses as JSON with explanation, laws, advice, and confidence fields."""
        
        # Initialize Phi agent with Groq and enhanced legal prompt
        self.agent = Agent(
            model=Groq(),
            system_prompt=legal_system_prompt
        )

        # Expanded legal practice areas with more comprehensive keywords
        self.practice_areas = {
            "criminal": [
                "arrest", "crime", "felony", "misdemeanor", "prosecution", "defense",
                "bail", "sentence", "criminal record", "probation", "parole"
            ],
            "civil": [
                "contract", "tort", "damages", "lawsuit", "liability", "negligence",
                "breach", "injury", "compensation", "settlement", "mediation"
            ],
            "family": [
                "divorce", "custody", "alimony", "marriage", "child support",
                "adoption", "guardianship", "visitation", "paternity", "prenuptial"
            ],
            "employment": [
                "discrimination", "termination", "wages", "harassment", "benefits",
                "workers compensation", "union", "overtime", "fmla", "ada"
            ],
            "property": [
                "real estate", "landlord", "tenant", "lease", "eviction",
                "foreclosure", "zoning", "easement", "deed", "title"
            ],
            "immigration": [
                "visa", "citizenship", "deportation", "asylum", "green card",
                "naturalization", "immigration status", "work permit"
            ]
        }

    def validate_legal_query(self, query: str) -> bool:
        """Validate if the query is legal in nature."""
        # Check if query contains legal keywords or phrases
        legal_indicators = [
            "law", "legal", "right", "court", "lawyer", "attorney", "lawsuit",
            "sue", "liability", "contract", "criminal", "civil", "statute"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in legal_indicators)

    def preprocess_query(self, query: str) -> str:
        """Clean and standardize the input query."""
        query = re.sub(r'[^\w\s]', ' ', query)
        return ' '.join(query.split()).lower()

    def identify_practice_area(self, query: str) -> Dict[str, float]:
        """Identify relevant legal practice areas with confidence scores."""
        query = self.preprocess_query(query)
        scores = {}
        for area, keywords in self.practice_areas.items():
            matches = sum(1 for kw in keywords if kw in query)
            total_keywords = len(keywords)
            scores[area] = matches / total_keywords if matches > 0 else 0
        return scores

    def generate_response(self, query: str) -> Dict:
        """Generate response using Phi agent with Groq."""
        try:
            # First validate if query is legal in nature
            if not self.validate_legal_query(query):
                return {
                    "error": "This query appears to be outside the scope of legal information. Please provide a law-related question."
                }

            # Identify relevant practice areas
            practice_areas = self.identify_practice_area(query)
            relevant_areas = [area for area, score in practice_areas.items() if score > 0]

            # Prepare the enhanced legal prompt
            prompt = f"""Legal question: {query}

            Relevant practice areas: {', '.join(relevant_areas) if relevant_areas else 'general legal'}

            Provide detailed legal information including:
            1. Relevant laws, statutes, and precedents with citations
            2. Jurisdictional considerations and variations
            3. Practical legal implications and considerations
            4. Confidence score (0-1) based on clarity of established law
            
            Structure your response as JSON:
            {{
                "explanation": "detailed legal analysis",
                "laws": [
                    {{"name": "law name", "citation": "citation", "jurisdiction": "jurisdiction"}}
                ],
                "advice": "practical legal considerations",
                "confidence": 0.x,
                "jurisdiction_notes": "any jurisdiction-specific information"
            }}"""
            
            # Get response from Phi agent
            response = self.agent.run(prompt)
            
            # Parse response with enhanced error handling
            try:
                if "```json" in response:
                    data = json.loads(response.split("```json")[1].split("```")[0])
                else:
                    data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback structure with explanation why parsing failed
                data = {
                    "explanation": "Response parsing error. Original response: " + response[:200] + "...",
                    "laws": [],
                    "advice": "Unable to parse specific advice from response",
                    "confidence": 0.5,
                    "jurisdiction_notes": "Unable to parse jurisdiction information"
                }

            return {
                "answer": data.get("explanation", "No explanation provided"),
                "laws": data.get("laws", []),
                "confidence": data.get("confidence", 0.5),
                "advice": data.get("advice", "No specific advice provided"),
                "jurisdiction_notes": data.get("jurisdiction_notes", ""),
                "practice_areas": relevant_areas,
                "disclaimer": self.disclaimer
            }

        except Exception as e:
            return {"error": f"Error processing legal query: {str(e)}"}

def main():
    agent = LegalAgent()
    print("Legal Query Assistant (type 'quit' to exit)")
    print("Please note: This tool provides legal information, not legal advice.")
    
    while True:
        query = input("\nYour legal question: ")
        if query.lower() in ['quit', 'exit']:
            break
            
        response = agent.generate_response(query)
        
        if 'error' in response:
            print(f"\nError: {response['error']}")
            continue
            
        print("\nLegal Analysis:")
        print(response['answer'])
        
        if response['practice_areas']:
            print("\nRelevant Practice Areas:", ", ".join(response['practice_areas']))
        
        print("\nJurisdictional Considerations:")
        print(response['jurisdiction_notes'])
        
        print("\nPractical Legal Considerations:")
        print(response['advice'])
        
        print("\nRelevant Laws/Cases:")
        for law in response['laws']:
            print(f"- {law.get('name', 'Unnamed law')}")
            print(f"  Citation: {law.get('citation', 'No citation')}")
            print(f"  Jurisdiction: {law.get('jurisdiction', 'Not specified')}")
            
        print(f"\nConfidence Score: {response['confidence']:.2f}/1.0")
        print("\nDisclaimer:", response['disclaimer'])

if __name__ == "__main__":
    main()