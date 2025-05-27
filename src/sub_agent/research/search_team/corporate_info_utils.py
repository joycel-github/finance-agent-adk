from typing import Dict, Any, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from ..utils.file_utils import FileUtils

class CorporateInfoUtils:
    def __init__(self, data_directory: str = "src/agents/data"):
        """Initialize CorporateInfoUtils with a data directory."""
        self.file_utils = FileUtils(base_directory=data_directory)

    def get_corporate_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch and process corporate information for a given symbol."""
        stock = yf.Ticker(symbol)
        return {
            "symbol": symbol,
            "company_info": self._get_company_info(stock),
            "financial_statements": self._get_financial_statements(stock),
            "ownership": self._get_ownership_info(stock),
            "corporate_governance": self._get_corporate_governance(stock),
            "business_segments": self._get_business_segments(stock),
            "price_data": self._get_price_data(stock)
        }

    def _get_company_info(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get basic company information."""
        info = stock.info
        return {
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "description": info.get("longBusinessSummary", ""),
            "website": info.get("website", ""),
            "employees": info.get("fullTimeEmployees", 0),
            "country": info.get("country", ""),
            "city": info.get("city", ""),
            "state": info.get("state", ""),
            "address": info.get("address1", ""),
            "phone": info.get("phone", ""),
            "ceo": info.get("companyOfficers", [{}])[0].get("name", "") if info.get("companyOfficers") else "",
            "founded": info.get("firstTradeDateEpochUtc", "")
        }

    def _get_financial_statements(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get financial statements data."""
        return {
            "income_statement": self._process_financial_statement(stock.income_stmt),
            "balance_sheet": self._process_financial_statement(stock.balance_sheet),
            "cash_flow": self._process_financial_statement(stock.cashflow),
            "quarterly_income": self._process_financial_statement(stock.quarterly_income_stmt),
            "quarterly_balance": self._process_financial_statement(stock.quarterly_balance_sheet),
            "quarterly_cash_flow": self._process_financial_statement(stock.quarterly_cashflow)
        }

    def _get_ownership_info(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get ownership information."""
        return {
            "institutional_holders": self._process_holders(stock.institutional_holders),
            "major_holders": self._process_holders(stock.major_holders),
            "insider_holders": self._process_holders(stock.insider_holders) if hasattr(stock, 'insider_holders') else None
        }

    def _get_corporate_governance(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get corporate governance information."""
        info = stock.info
        return {
            "board_members": info.get("companyOfficers", []),
            "audit_committee": info.get("auditCommittee", []),
            "compensation_committee": info.get("compensationCommittee", []),
            "nominating_committee": info.get("nominatingCommittee", []),
            "governance_committee": info.get("governanceCommittee", [])
        }

    def _get_business_segments(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get business segments information."""
        info = stock.info
        return {
            "business_summary": info.get("longBusinessSummary", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "sub_industry": info.get("subIndustry", ""),
            "business_segments": info.get("businessSegments", {})
        }

    def _get_price_data(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get current and historical price data."""
        current_price = stock.info.get("regularMarketPrice", 0)
        previous_close = stock.info.get("regularMarketPreviousClose", 0)
        open_price = stock.info.get("regularMarketOpen", 0)
        day_high = stock.info.get("regularMarketDayHigh", 0)
        day_low = stock.info.get("regularMarketDayLow", 0)
        volume = stock.info.get("regularMarketVolume", 0)
        daily_change = round(current_price - previous_close, 2)
        daily_change_percent = (daily_change / previous_close * 100) if previous_close else 0
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist_data = stock.history(start=start_date, end=end_date)
        return {
            "current": {
                "price": current_price,
                "previous_close": previous_close,
                "open": open_price,
                "day_high": day_high,
                "day_low": day_low,
                "volume": volume,
                "daily_change": daily_change,
                "daily_change_percent": daily_change_percent
            },
            "historical": {
                "daily": self._process_historical_data(hist_data),
                "periods": {
                    "1d": self._get_period_stats(hist_data, "1D"),
                    "1w": self._get_period_stats(hist_data, "1W"),
                    "1m": self._get_period_stats(hist_data, "1M"),
                    "3m": self._get_period_stats(hist_data, "3M"),
                    "6m": self._get_period_stats(hist_data, "6M"),
                    "1y": self._get_period_stats(hist_data, "1Y")
                }
            }
        }

    def _process_historical_data(self, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """Process historical price data."""
        if hist_data is None or hist_data.empty:
            return {}
        return {
            "dates": [str(date) for date in hist_data.index.strftime('%Y-%m-%d').tolist()],
            "prices": hist_data['Close'].tolist(),
            "volumes": hist_data['Volume'].tolist(),
            "highs": hist_data['High'].tolist(),
            "lows": hist_data['Low'].tolist(),
            "opens": hist_data['Open'].tolist()
        }

    def _process_financial_statement(self, statement: pd.DataFrame) -> Dict[str, Any]:
        """Process financial statement data."""
        if statement is None or statement.empty:
            return {}
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

    def _process_holders(self, holders: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process holders data."""
        if holders is None or holders.empty:
            return []
        return holders.to_dict('records')

    def _get_period_stats(self, hist_data: pd.DataFrame, period: str) -> Dict[str, Any]:
        """Get statistics for a specific period."""
        if hist_data is None or hist_data.empty:
            return {}
        return {
            "start": hist_data['Close'].iloc[0],
            "end": hist_data['Close'].iloc[-1],
            "change": hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0],
            "change_percent": (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0] * 100
        }
    
    def fetch_and_store_info(self, symbol: str, directory: str = None) -> str:
        """Fetch corporate info and store it as a JSON file, returning the file path."""
        info = self.get_corporate_info(symbol)
        return self.file_utils.store_json_info(info, symbol=symbol, directory=directory, prefix="corporate_info")

    def store_info(self, info: Dict[str, Any], symbol: str = None, directory: str = None) -> str:
        """Store the info dict as a JSON file locally and return the file path."""
        return self.file_utils.store_json_info(info, symbol=symbol, directory=directory, prefix="corporate_info")

    def read_corporate_info_from_local_file(self, symbol: str, directory: str = None) -> Dict[str, Any]:
        """Read corporate info from the latest local JSON file if it exists."""
        return self.file_utils.read_latest_json_file(symbol, directory=directory, prefix="corporate_info")

    def find_local_stored_latest_corporate_info_file(self, symbol: str, directory: str = None) -> str:
        """Find the path of the latest stored corporate info file for a given symbol."""
        return self.file_utils.find_latest_json_file(symbol, directory=directory, prefix="corporate_info") 