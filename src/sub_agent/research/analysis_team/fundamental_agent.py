from typing import Dict, Any
import yfinance as yf
import pandas as pd
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio
from sub_agent.research.utils.file_utils import FileUtils
from sub_agent.research.prompts import FUNDAMENTAL_ANALYSIS_PROMPT

def get_financial_statements(stock: yf.Ticker) -> Dict[str, Any]:
    """Get financial statements data."""
    return {
        "income_statement": process_financial_statement(stock.income_stmt),
        "balance_sheet": process_financial_statement(stock.balance_sheet),
        "cash_flow": process_financial_statement(stock.cashflow),
        "quarterly_income": process_financial_statement(stock.quarterly_income_stmt),
        "quarterly_balance": process_financial_statement(stock.quarterly_balance_sheet),
        "quarterly_cash_flow": process_financial_statement(stock.quarterly_cashflow)
    }

def calculate_key_ratios(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate key financial ratios."""
    info = stock.info
    return {
        "pe_ratio": info.get("trailingPE", 0),
        "forward_pe": info.get("forwardPE", 0),
        "peg_ratio": info.get("pegRatio", 0),
        "price_to_book": info.get("priceToBook", 0),
        "price_to_sales": info.get("priceToSalesTrailing12Months", 0),
        "dividend_yield": info.get("dividendYield", 0),
        "beta": info.get("beta", 0)
    }

def calculate_growth_metrics(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate growth metrics."""
    info = stock.info
    return {
        "revenue_growth": info.get("revenueGrowth", 0),
        "earnings_growth": info.get("earningsGrowth", 0),
        "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth", 0),
        "earnings_annual_growth": info.get("earningsAnnualGrowth", 0)
    }

def calculate_efficiency_metrics(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate efficiency metrics."""
    info = stock.info
    return {
        "return_on_equity": info.get("returnOnEquity", 0),
        "return_on_assets": info.get("returnOnAssets", 0),
        "profit_margins": info.get("profitMargins", 0),
        "operating_margins": info.get("operatingMargins", 0)
    }

def calculate_profitability_metrics(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate profitability metrics."""
    info = stock.info
    return {
        "gross_profit": info.get("grossProfit", 0),
        "operating_income": info.get("operatingIncome", 0),
        "net_income": info.get("netIncome", 0),
        "ebitda": info.get("ebitda", 0)
    }

def calculate_liquidity_metrics(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate liquidity metrics."""
    info = stock.info
    return {
        "current_ratio": info.get("currentRatio", 0),
        "quick_ratio": info.get("quickRatio", 0),
        "working_capital": info.get("workingCapital", 0)
    }

def calculate_leverage_metrics(stock: yf.Ticker) -> Dict[str, Any]:
    """Calculate leverage metrics."""
    info = stock.info
    return {
        "debt_to_equity": info.get("debtToEquity", 0),
        "long_term_debt": info.get("longTermDebt", 0),
        "total_debt": info.get("totalDebt", 0)
    }

def process_financial_statement(statement: pd.DataFrame) -> Dict[str, Any]:
    """Process financial statement data."""
    if statement is None or statement.empty:
        return {}
    
    # Convert DataFrame to dict and handle Timestamp objects
    result = {}
    for col in statement.columns:
        if isinstance(col, pd.Timestamp):
            col_str = col.strftime('%Y-%m-%d')
        else:
            col_str = str(col)
        
        result[col_str] = {}
        for idx, value in statement[col].items():
            if isinstance(idx, pd.Timestamp):
                idx_str = idx.strftime('%Y-%m-%d')
            else:
                idx_str = str(idx)
            result[col_str][idx_str] = float(value) if pd.notnull(value) else None
    
    return result

def analyze_stock(symbol: str) -> Dict[str, Any]:
    """Analyze a stock using all available metrics."""
    # TODO: In the future, get the stock symbol from session_state instead of as a direct argument
    stock = yf.Ticker(symbol)
    return {
        "financial_statements": get_financial_statements(stock),
        "key_ratios": calculate_key_ratios(stock),
        "growth_metrics": calculate_growth_metrics(stock),
        "efficiency_metrics": calculate_efficiency_metrics(stock),
        "profitability_metrics": calculate_profitability_metrics(stock),
        "liquidity_metrics": calculate_liquidity_metrics(stock),
        "leverage_metrics": calculate_leverage_metrics(stock)
    }

# Create the LlmAgent instance
fundamental_agent = LlmAgent(
    name="fundamental_analysis_agent",
    model="gemini-2.0-flash",
    description="An agent that performs fundamental analysis on stocks",
    instruction=FUNDAMENTAL_ANALYSIS_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[analyze_stock],
    output_key="fundamental_analysis"
)


# --- Function to Interact with the Agent ---
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

async def test_fundamental_agent():
    # --- Session Management ---
    session_service = InMemorySessionService()
    APP_NAME = "fundamental_analysis_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    runner = Runner(
        agent=fundamental_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # Test the agent with a stock analysis query
    await call_agent_async("Analyze the fundamental metrics for Microsoft (MSFT)", runner, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(test_fundamental_agent())


