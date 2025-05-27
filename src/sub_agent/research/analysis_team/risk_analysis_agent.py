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
from sub_agent.research.prompts import RISK_ANALYSIS_PROMPT

def calculate_volatility_metrics(hist: pd.DataFrame) -> Dict[str, Any]:
    returns = hist['Close'].pct_change().dropna()
    daily_volatility = returns.std()
    annualized_volatility = daily_volatility * np.sqrt(252)
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    max_drawdown = calculate_max_drawdown(hist['Close'])
    return {
        "daily_volatility": daily_volatility,
        "annualized_volatility": annualized_volatility,
        "var_95": var_95,
        "var_99": var_99,
        "max_drawdown": max_drawdown
    }

def calculate_max_drawdown(prices: pd.Series) -> float:
    peak = prices.expanding(min_periods=1).max()
    drawdown = (prices - peak) / peak
    return drawdown.min()

def analyze_financial_risk(stock: yf.Ticker) -> Dict[str, Any]:
    info = stock.info
    return {
        "debt_to_equity": info.get("debtToEquity", 0),
        "current_ratio": info.get("currentRatio", 0),
        "quick_ratio": info.get("quickRatio", 0),
        "interest_coverage": info.get("interestCoverage", 0),
        "total_debt": info.get("totalDebt", 0),
        "total_cash": info.get("totalCash", 0)
    }

def analyze_market_risk(stock: yf.Ticker) -> Dict[str, Any]:
    info = stock.info
    return {
        "beta": info.get("beta", 1.0),
        "52_week_high": info.get("fiftyTwoWeekHigh", 0),
        "52_week_low": info.get("fiftyTwoWeekLow", 0),
        "shares_outstanding": info.get("sharesOutstanding", 0),
        "float_shares": info.get("floatShares", 0)
    }

def analyze_liquidity_risk(stock: yf.Ticker) -> Dict[str, Any]:
    info = stock.info
    return {
        "average_volume": info.get("averageVolume", 0),
        "average_volume_10days": info.get("averageVolume10days", 0),
        "bid": info.get("bid", 0),
        "ask": info.get("ask", 0),
        "bid_size": info.get("bidSize", 0),
        "ask_size": info.get("askSize", 0)
    }

def analyze_concentration_risk(stock: yf.Ticker) -> Dict[str, Any]:
    institutional_holders = stock.institutional_holders
    major_holders = stock.major_holders
    if institutional_holders is not None and not institutional_holders.empty:
        top_holders = institutional_holders.head(5)
        concentration = (top_holders["Shares"].sum() / institutional_holders["Shares"].sum()) if not institutional_holders.empty else 0
    else:
        concentration = 0
    return {
        "institutional_concentration": concentration,
        "institutional_holders_count": len(institutional_holders) if institutional_holders is not None else 0,
        "major_holders_count": len(major_holders) if major_holders is not None else 0
    }

def analyze_risk(symbol: str, period: str = "1y") -> Dict[str, Any]:
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)
    return {
        "volatility_metrics": calculate_volatility_metrics(hist),
        "financial_risk": analyze_financial_risk(stock),
        "market_risk": analyze_market_risk(stock),
        "liquidity_risk": analyze_liquidity_risk(stock),
        "concentration_risk": analyze_concentration_risk(stock)
    }

risk_analysis_agent = LlmAgent(
    name="risk_analysis_agent",
    model="gemini-2.0-flash",
    description="An agent that performs risk analysis on stocks",
    instruction=RISK_ANALYSIS_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[analyze_risk],
    output_key="risk_analysis"
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
                final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.')}"
            break
    print(f"<<< Agent Response: {final_response_text}")

async def test_risk_analysis_agent():
    session_service = InMemorySessionService()
    APP_NAME = "risk_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    runner = Runner(
        agent=risk_analysis_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    await call_agent_async("Analyze the risk metrics for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_risk_analysis_agent()) 