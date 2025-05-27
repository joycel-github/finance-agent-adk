from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from src.sub_agent.research.search_team.industry_info_utils import IndustryInfoUtils

# TODO: Add competitor analysis functionality
# The current implementation focuses on industry-level metrics but lacks competitor analysis.
# We should consider:
# 1. Using a dedicated financial data API (e.g., Alpha Vantage, IEX Cloud) for competitor data
# 2. Implementing a search-based approach using LLM to identify and analyze competitors
# 3. Adding competitor metrics to the industry analysis (market share, competitive advantages, etc.)
# 4. Including competitive landscape analysis in the final report

def analyze_industry(symbol: str) -> Dict[str, Any]:
    """Analyze industry data for a given symbol."""
    info_fetcher = IndustryInfoUtils()
    industry_data = info_fetcher.fetch_and_store_info(symbol)
    return industry_data

# Create the LlmAgent instance
industry_agent = LlmAgent(
    name="IndustryAgent",
    model="gemini-2.0-flash",
    description="Find industry trends, performance metrics, and growth opportunities information for a given company symbol.",
    instruction="""
    You are an expert industry information collector. Your role is to find industry trends, performance metrics, and growth opportunities data for a given company symbol.
    
    Always use find_local_stored_latest_industry_info_file to get the latest stored local file for the industry. 
    If it exists and was created less than 24 hours ago, return the data file path as output_key.
    Otherwise, use fetch_and_store_info to create a new file and return the path of the new file.
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,  # More deterministic output
    ),
    tools=[
        # TODO: we should add more tools and have the search agnent smartly identify the best tool to use
        IndustryInfoUtils().fetch_and_store_info,
        IndustryInfoUtils().find_local_stored_latest_industry_info_file
    ],
    output_key="industry_info_file_path"
)

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif getattr(event, "actions", None) and getattr(event.actions, "escalate", False):
                final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.')}"
            break

    print(f"<<< Agent Response: {final_response_text}")

async def test_industry_agent():
    # --- Session Management ---
    session_service = InMemorySessionService()
    APP_NAME = "industry_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    runner = Runner(
        agent=industry_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # Test the agent with an industry analysis query
    await call_agent_async("Analyze the industry trends for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_industry_agent()) 