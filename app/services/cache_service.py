"""
Cache service for financial data.

This module handles caching of financial data to avoid repeated API calls
and improve application performance.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from app.exceptions import ConfigurationError


class CacheService:
    """Service for caching financial data locally."""

    def __init__(self, cache_directory: Optional[str] = None) -> None:
        """
        Initialize the cache service.

        Args:
            cache_directory: Directory to store cache files (defaults to app/cache)
        """
        self.cache_directory = Path(cache_directory or "app/cache")
        self.cache_directory.mkdir(parents=True, exist_ok=True)

        # Default cache expiration (24 hours)
        self.default_expiration_hours = 24

    def get_cache_key(self, ticker: str, data_type: str, period: str = "annual") -> str:
        """
        Generate a cache key for the given parameters.

        Args:
            ticker: Company ticker symbol
            data_type: Type of financial data (e.g., 'income-statement', 'cash-flow-statement')
            period: Data period ('annual' or 'quarter')

        Returns:
            Cache key string
        """
        # Replace slashes with underscores to avoid directory structure issues
        safe_data_type = data_type.replace("/", "_")
        return f"{ticker}_{safe_data_type}_{period}.json"

    def get_cache_path(self, cache_key: str) -> Path:
        """
        Get the full path for a cache file.

        Args:
            cache_key: Cache key string

        Returns:
            Full path to cache file
        """
        return self.cache_directory / cache_key

    def is_cache_valid(self, cache_path: Path, expiration_hours: Optional[int] = None) -> bool:
        """
        Check if cached data is still valid.

        Args:
            cache_path: Path to cache file
            expiration_hours: Hours until cache expires (defaults to 24)

        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False

        expiration_hours = expiration_hours or self.default_expiration_hours
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < timedelta(hours=expiration_hours)

    def save_data(self, ticker: str, data_type: str, data: dict, period: str = "annual") -> None:
        """
        Save data to cache.

        Args:
            ticker: Company ticker symbol
            data_type: Type of financial data
            data: Data to cache
            period: Data period ('annual' or 'quarter')
        """
        cache_key = self.get_cache_key(ticker, data_type, period)
        cache_path = self.get_cache_path(cache_key)

        cache_entry = {
            "ticker": ticker,
            "data_type": data_type,
            "period": period,
            "cached_at": datetime.now().isoformat(),
            "data": data,
        }

        try:
            with open(cache_path, "w") as f:
                json.dump(cache_entry, f, indent=2, default=str)
        except (OSError, IOError, ValueError, TypeError) as e:
            raise ConfigurationError(f"Failed to save cache for {ticker}: {e}")

    def load_data(
        self,
        ticker: str,
        data_type: str,
        period: str = "annual",
        expiration_hours: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Load data from cache if valid.

        Args:
            ticker: Company ticker symbol
            data_type: Type of financial data
            period: Data period ('annual' or 'quarter')
            expiration_hours: Hours until cache expires

        Returns:
            Cached data if valid, None otherwise
        """
        cache_key = self.get_cache_key(ticker, data_type, period)
        cache_path = self.get_cache_path(cache_key)

        if not self.is_cache_valid(cache_path, expiration_hours):
            return None

        try:
            with open(cache_path, "r") as f:
                cache_entry = json.load(f)
                return cache_entry.get("data")
        except (OSError, IOError, ValueError, TypeError, json.JSONDecodeError):
            # If cache file is corrupted, remove it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def clear_cache(self, ticker: Optional[str] = None, data_type: Optional[str] = None) -> None:
        """
        Clear cache files.

        Args:
            ticker: Specific ticker to clear (if None, clears all)
            data_type: Specific data type to clear (if None, clears all)
        """
        if ticker and data_type:
            # Clear specific cache
            cache_key = self.get_cache_key(ticker, data_type)
            cache_path = self.get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            # Clear all cache files
            for cache_file in self.cache_directory.glob("*.json"):
                if ticker and not cache_file.name.startswith(ticker):
                    continue
                if data_type and data_type not in cache_file.name:
                    continue
                cache_file.unlink()

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_directory.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        cache_info = {
            "total_files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_directory),
            "files": [],
        }

        for cache_file in cache_files:
            try:
                with open(cache_file, "r") as f:
                    cache_entry = json.load(f)
                    cache_info["files"].append(
                        {
                            "file": cache_file.name,
                            "ticker": cache_entry.get("ticker"),
                            "data_type": cache_entry.get("data_type"),
                            "cached_at": cache_entry.get("cached_at"),
                            "size_bytes": cache_file.stat().st_size,
                            "is_valid": self.is_cache_valid(cache_file),
                        }
                    )
            except (OSError, IOError, ValueError, TypeError, json.JSONDecodeError):
                cache_info["files"].append(
                    {"file": cache_file.name, "error": "Corrupted cache file"}
                )

        return cache_info
