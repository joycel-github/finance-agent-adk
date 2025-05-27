from typing import Dict, Any
import yfinance as yf
import os
import json
from datetime import datetime

class IndustryInfoUtils:
    """Class responsible for fetching and collecting industry data."""

    # TODO: yahoo doesn't work well. we need better api. Also why read yf.Ticker so many times..
    def get_industry_info(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive industry information including market trends, metrics, and growth opportunities.
        
        Args:
            symbol (str): The stock symbol to analyze
            
        Returns:
            Dict[str, Any]: Dictionary containing industry information with the following keys:
                - market_trends: Industry and sector trends
                - industry_metrics: Industry and sector metrics
                - growth_opportunities: Market and growth potential
        """
        return {
            "market_trends": self._get_market_trends(symbol),
            "industry_metrics": self._get_industry_metrics(symbol),
            "growth_opportunities": self._get_growth_opportunities(symbol)
        }
    
    def _get_market_trends(self, symbol: str) -> Dict[str, Any]:
        """Get market trends and industry performance."""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "industry": info.get("industry", ""),
            "sector": info.get("sector", ""),
            "industry_pe": info.get("industryPE", 0),
            "sector_pe": info.get("sectorPE", 0),
            "industry_growth": info.get("industryGrowth", 0),
            "sector_growth": info.get("sectorGrowth", 0)
        }
    
    def _get_industry_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get industry-specific metrics and benchmarks."""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "industry_averages": {
                "pe_ratio": info.get("industryPE", 0),
                "profit_margin": info.get("industryProfitMargin", 0),
                "revenue_growth": info.get("industryRevenueGrowth", 0)
            },
            "sector_averages": {
                "pe_ratio": info.get("sectorPE", 0),
                "profit_margin": info.get("sectorProfitMargin", 0),
                "revenue_growth": info.get("sectorRevenueGrowth", 0)
            }
        }
    
    def _get_growth_opportunities(self, symbol: str) -> Dict[str, Any]:
        """Get growth opportunities and market potential."""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "total_addressable_market": info.get("totalAddressableMarket", 0),
            "market_growth_rate": info.get("marketGrowthRate", 0),
            "industry_growth_rate": info.get("industryGrowth", 0),
            "sector_growth_rate": info.get("sectorGrowth", 0)
        }

    def store_info(self, info: Dict[str, Any], symbol: str = None, directory: str = "src/agents/data") -> str:
        """Store the info dict as a JSON file locally and return the file path."""
        if symbol is None:
            symbol = info.get("symbol", "unknown")
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(directory, f"{symbol}_industry_info_{timestamp}.json")
        with open(file_path, "w") as f:
            json.dump(info, f, indent=2, default=str)
        return file_path

    def fetch_and_store_info(self, symbol: str, directory: str = "src/agents/data") -> str:
        """Fetch industry info and store it as a JSON file, returning the file path."""
        info = self.get_industry_info(symbol)
        return self.store_info(info, symbol=symbol, directory=directory)

    def find_local_stored_latest_industry_info_file(self, symbol: str, directory: str = "src/agents/data") -> str:
        """Find the path of the latest stored industry info file for a given industry."""
        import glob
        pattern = os.path.join(directory, f"{symbol}_industry_info_*.json")
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getctime) 