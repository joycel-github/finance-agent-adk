import os
import json
import glob
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# TODO: move this src/utils

class FileUtils:
    """Utility class for file operations."""
    
    def __init__(self, base_directory: str = "src/agents/data"):
        """Initialize FileUtils with a base directory."""
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)


    def store_json_info(self, info: Dict[str, Any], symbol: str = None, directory: str = None, prefix: str = "corporate_info") -> str:
        """Store the info dict as a JSON file locally and return the file path."""
        if symbol is None:
            symbol = info.get("symbol", "unknown")
        directory = directory or self.base_directory
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(directory, f"{symbol}_{prefix}_{timestamp}.json")
        with open(file_path, "w") as f:
            json.dump(info, f, indent=2, default=str)
        return file_path

    def read_latest_json_file(self, symbol: str, directory: str = None, prefix: str = "corporate_info") -> Optional[Dict[str, Any]]:
        """Read the latest JSON file for a given symbol if it exists."""
        directory = directory or self.base_directory
        pattern = os.path.join(directory, f"{symbol}_{prefix}_*.json")
        files = glob.glob(pattern)
        if not files:
            return None
        latest_file = max(files, key=os.path.getctime)
        with open(latest_file, "r") as f:
            return json.load(f)

    def find_latest_json_file(self, symbol: str, directory: str = None, prefix: str = "corporate_info") -> Optional[str]:
        """Find the path of the latest stored JSON file for a given symbol."""
        directory = directory or self.base_directory
        pattern = os.path.join(directory, f"{symbol}_{prefix}_*.json")
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def list_all_files(self, directory: str = None, prefix: str = None) -> list[str]:
        """List all files in the directory, optionally filtered by prefix."""
        directory = directory or self.base_directory
        if prefix:
            pattern = os.path.join(directory, f"*_{prefix}_*.json")
        else:
            pattern = os.path.join(directory, "*.json")
        return glob.glob(pattern)

    def delete_old_files(self, days: int = 30, directory: str = None) -> int:
        """Delete files older than specified days. Returns number of files deleted."""
        directory = directory or self.base_directory
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for file_path in self.list_all_files(directory):
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_time < cutoff_date:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError:
                    continue
        return deleted_count 