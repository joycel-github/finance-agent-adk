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
from sub_agent.research.prompts import SENTIMENT_ANALYSIS_PROMPT

def analyze_news_sentiment(news) -> Dict[str, Any]:
    if not news:
        return {"sentiment_score": 0, "article_count": 0}
    sentiment_scores = []
    for article in news[:10]:
        title = article.get("title", "")
        score = calculate_text_sentiment(title)
        sentiment_scores.append(score)
    return {
        "sentiment_score": float(np.mean(sentiment_scores)) if sentiment_scores else 0,
        "article_count": len(sentiment_scores)
    }

def analyze_recommendation_sentiment(recommendations: pd.DataFrame) -> Dict[str, Any]:
    if recommendations is None or recommendations.empty:
        return {"sentiment_score": 0, "recommendation_count": 0}
    print("[DEBUG] Recommendations DataFrame columns:", recommendations.columns.tolist())
    print("[DEBUG] Recommendations DataFrame head:")
    print(recommendations.head())
    recommendation_map = {
        "Strong Buy": 1.0,
        "Buy": 0.75,
        "Hold": 0.5,
        "Sell": 0.25,
        "Strong Sell": 0.0
    }
    # Try to find the column that contains the recommendation grade
    grade_col = None
    for col in ["To Grade", "toGrade", "Recommendation", "Grade"]:
        if col in recommendations.columns:
            grade_col = col
            break
    if grade_col is None:
        # Fallback: use the first column if it looks like a grade column
        for col in recommendations.columns:
            if recommendations[col].dtype == object:
                grade_col = col
                break
    if grade_col is None:
        return {"sentiment_score": 0, "recommendation_count": 0}
    scores = [recommendation_map.get(rec, 0.5) for rec in recommendations[grade_col]]
    return {
        "sentiment_score": float(np.mean(scores)) if scores else 0,
        "recommendation_count": len(scores)
    }

def analyze_institutional_sentiment(institutional_holders: pd.DataFrame) -> Dict[str, Any]:
    if institutional_holders is None or institutional_holders.empty:
        return {"sentiment_score": 0, "holder_count": 0}
    sentiment_score = 0.5
    return {
        "sentiment_score": sentiment_score,
        "holder_count": len(institutional_holders)
    }

def analyze_market_sentiment(stock: yf.Ticker) -> Dict[str, Any]:
    info = stock.info
    return {
        "short_ratio": info.get("shortRatio", 0),
        "short_percent_float": info.get("shortPercentOfFloat", 0),
        "shares_short": info.get("sharesShort", 0),
        "shares_short_prior_month": info.get("sharesShortPriorMonth", 0)
    }

def calculate_text_sentiment(text: str) -> float:
    # Placeholder: In production, use an LLM or sentiment model
    # Here, we use a simple keyword-based approach
    positive_keywords = ["gain", "growth", "positive", "up", "bull", "strong"]
    negative_keywords = ["loss", "decline", "negative", "down", "bear", "weak"]
    score = 0
    for word in positive_keywords:
        if word in text.lower():
            score += 1
    for word in negative_keywords:
        if word in text.lower():
            score -= 1
    return max(-1, min(1, score / 2))

def analyze_sentiment(symbol: str) -> Dict[str, Any]:
    stock = yf.Ticker(symbol)
    news = stock.news
    recommendations = stock.recommendations
    institutional_holders = stock.institutional_holders
    return {
        "news_sentiment": analyze_news_sentiment(news),
        "recommendation_sentiment": analyze_recommendation_sentiment(recommendations),
        "institutional_sentiment": analyze_institutional_sentiment(institutional_holders),
        "market_sentiment": analyze_market_sentiment(stock)
    }

sentiment_agent = LlmAgent(
    name="sentiment_analysis_agent",
    model="gemini-2.0-flash",
    description="An agent that performs sentiment analysis on stocks",
    instruction=SENTIMENT_ANALYSIS_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[analyze_sentiment],
    output_key="sentiment_analysis"
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

async def test_sentiment_agent():
    session_service = InMemorySessionService()
    APP_NAME = "sentiment_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    runner = Runner(
        agent=sentiment_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    await call_agent_async("Analyze the sentiment for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_sentiment_agent()) 