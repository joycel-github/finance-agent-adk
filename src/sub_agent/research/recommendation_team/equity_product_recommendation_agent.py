from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from sub_agent.research.prompts import EQUITY_PRODUCTS_RECOMMENDATION_PROMPT


equity_products_recommendation = LlmAgent(
    name="equity_products_recommendation",
    model="gemini-2.0-flash",
    description="An agent that generates equity product recommendations (buy, sell, hold) based on merged_analysis",
    instruction=EQUITY_PRODUCTS_RECOMMENDATION_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    output_key="equity_recommendation"
)