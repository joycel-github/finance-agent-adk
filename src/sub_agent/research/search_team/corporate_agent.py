from typing import Dict, Any, List, AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.events.event import Event
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.events.event_actions import EventActions
from typing_extensions import override
import logging
from google.genai.types import GenerateContentConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import asyncio
from src.sub_agent.research.search_team.corporate_info_utils import CorporateInfoUtils

logger = logging.getLogger(__name__)

# Create the LlmAgent instance
corporate_agent = LlmAgent(
    name="CorporateAgent",
    model="gemini-2.0-flash",
    description="Gathers corporate and price information from yFinance",
    instruction="""
    You are a corporate information agent that can gather detailed corporate data for any given stock symbol.
    Always use read_corporate_info_from_local_file to get the latest stored local file. If it exists and was created less than 24 hours ago, return the data file path as output_key.
    Otherwise, use fetch_and_store_info to create a new file and return the path of the new file.
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[CorporateInfoUtils().fetch_and_store_info, CorporateInfoUtils().find_local_stored_latest_corporate_info_file],
    output_key="coporate_info_file_path"
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

async def test_corporate_agent():
    # --- Session Management ---
    session_service = InMemorySessionService()
    APP_NAME = "corporate_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    runner = Runner(
        agent=corporate_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # Test the agent with a corporate analysis query
    await call_agent_async("Analyze the corporate information for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_corporate_agent()) 