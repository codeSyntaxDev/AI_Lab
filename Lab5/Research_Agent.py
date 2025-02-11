from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
import os

# Load API Key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define the research agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),  # Use GPT-4o for best results
    tools=[DuckDuckGo(), Newspaper4k()],  # Search + Extract Text
    description="You are an advanced AI researcher that finds and summarizes key information from the web.",
    instructions=[
        "Search for the top 5 relevant links on the given topic.",
        "Extract the text from each webpage and analyze it.",
        "Summarize the key findings into a concise research report.",
    ],
    markdown=True,  # Format output in Markdow|n for better readability
)

# Function to run the research agent
def run_research(topic):
    print(f"🔍 Researching: {topic}...\n")
    response = agent.run(topic, stream=True)  # Stream the response for real-time feedback
    print("\n📌 Research Summary:\n", response)

# Run the agent with a topic of your choice
topic = input("Enter your research topic: ")
run_research(topic)