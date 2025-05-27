from typing import Dict, Any
import yfinance as yf
import pandas as pd
import numpy as np
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from sub_agent.research.prompts import TECHNICAL_ANALYSIS_PROMPT

def calculate_technical_indicators(hist: pd.DataFrame) -> Dict[str, Any]:
    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
    hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
    hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    hist['RSI'] = 100 - (100 / (1 + rs))
    exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['MACD'] = exp1 - exp2
    hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
    hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
    hist['BB_Upper'] = hist['BB_Middle'] + 2 * hist['Close'].rolling(window=20).std()
    hist['BB_Lower'] = hist['BB_Middle'] - 2 * hist['Close'].rolling(window=20).std()
    latest = hist.iloc[-1]
    return {
        "price": {
            "current": latest['Close'],
            "open": latest['Open'],
            "high": latest['High'],
            "low": latest['Low'],
            "volume": latest['Volume']
        },
        "moving_averages": {
            "sma_20": latest['SMA_20'],
            "sma_50": latest['SMA_50'],
            "sma_200": latest['SMA_200']
        },
        "momentum": {
            "rsi": latest['RSI'],
            "macd": latest['MACD'],
            "signal_line": latest['Signal_Line']
        },
        "volatility": {
            "bollinger_upper": latest['BB_Upper'],
            "bollinger_middle": latest['BB_Middle'],
            "bollinger_lower": latest['BB_Lower']
        }
    }

def analyze_technical(symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period, interval=interval)
    return calculate_technical_indicators(hist)

technical_agent = LlmAgent(
    name="technical_analysis_agent",
    model="gemini-2.0-flash",
    description="An agent that performs technical analysis on stocks",
    instruction=TECHNICAL_ANALYSIS_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[analyze_technical],
    output_key="technical_analysis"
)

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif getattr(event, "actions", None) and getattr(event.actions, "escalate", False):
                final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.') }"
            break
    print(f"<<< Agent Response: {final_response_text}")

async def test_technical_agent():
    session_service = InMemorySessionService()
    APP_NAME = "technical_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    runner = Runner(
        agent=technical_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    await call_agent_async("Analyze the technical indicators for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_technical_agent()) 