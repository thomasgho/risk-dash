import os
import json
from datetime import datetime


class CacheManager:
    def __init__(self, session_state):
        """Initialize the CacheManager with Streamlit's session state."""
        self.session_state = session_state

        # Create cache folder for on-disk caching
        if not os.path.exists('cache'):
            os.makedirs('cache')
        
        # Define file paths for on-disk caching
        self.portfolio_cache_path = "cache/portfolio_historical_prices.json"
        self.spy_cache_path = "cache/spy_historical_prices.json"
        self.strategy_cache_path = "cache/strategies.json" 
        
        # Initialize in-memory cache if not already initialized
        if not hasattr(self.session_state, "portfolio_historical_cache"):
            self.session_state.portfolio_historical_cache = {}
        if not hasattr(self.session_state, "spy_historical_cache"):
            self.session_state.spy_historical_cache = {}
        if not hasattr(self.session_state, "strategy_cache"):
            self.session_state.strategy_cache = {}            

    def set_in_memory(self, key, data):
        """Set data in in-memory cache."""
        self.session_state[key] = data

    def get_from_memory(self, key):
        """Retrieve data from in-memory cache."""
        return self.session_state.get(key, None)
    
    def set_on_disk(self, filepath, data):
        """Set data in on-disk cache."""
        with open(filepath, "w") as file:
            json.dump(data, file)

    def get_from_disk(self, filepath):
        """Retrieve data from on-disk cache."""
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                return json.load(file)
        return None

    def set_historical_data(self, ticker, data):
        """Cache historical data for a specific ticker."""
        # Update in-memory cache
        self.session_state.portfolio_historical_cache[ticker] = data

        # Update on-disk cache
        self.set_on_disk(self.portfolio_cache_path, self.session_state.portfolio_historical_cache)

    def get_historical_data(self, ticker):
        """Retrieve cached historical data for a specific ticker."""
        # Check in-memory cache first
        data = self.session_state.portfolio_historical_cache.get(ticker, None)
        if data:
            return data
        
        # If not in in-memory cache, check on-disk cache
        data = self.get_from_disk(self.portfolio_cache_path)
        if data and ticker in data:
            return data[ticker]

        return None

    def set_spy_data(self, data):
        """Cache SPY historical data."""
        # Update in-memory cache
        self.session_state.spy_historical_cache = data

        # Update on-disk cache
        self.set_on_disk(self.spy_cache_path, data)

    def get_spy_data(self):
        """Retrieve cached SPY historical data."""
        # Check in-memory cache first
        data = self.session_state.spy_historical_cache
        if data:
            return data
        
        # If not in in-memory cache, check on-disk cache
        return self.get_from_disk(self.spy_cache_path)
        
    def set_strategy(self, portfolio):
        """
        Save the current state of the portfolio to a JSON file.
        """
        last_cached_time = datetime.now()
        
        cache_data = {
            'portfolio': portfolio,
            'last_cached_time': last_cached_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if not os.path.exists('cache'):
            os.makedirs('cache')
        with open(self.strategy_cache_path, 'w') as f:
            json.dump(cache_data, f)

    def load_strategy_cache(self):
        """
        Load the portfolio state from a JSON file.
        """
        try:
            with open(self.strategy_cache_path, 'r') as f:
                cache_data = json.load(f)
                portfolio = cache_data['portfolio']
                last_cached_time = datetime.strptime(
                    cache_data['last_cached_time'], '%Y-%m-%d %H:%M:%S')
            return portfolio, last_cached_time
        except FileNotFoundError:
            st.warning('Cache not found. Starting with a clean slate.')
            return None, None
        except json.JSONDecodeError:
            st.warning('Error decoding cache. Starting with a clean slate.')
            return None, None
            
    def clear_cache(self):
        """Clear all cached data."""
        self.session_state.historical_data_cache = {}
        self.session_state.spy_data_cache = {}
        if os.path.exists(self.historical_data_path):
            os.remove(self.historical_data_path)
        if os.path.exists(self.spy_data_path):
            os.remove(self.spy_data_path)


# Initialize the CacheManager with a mock session state for demonstration
# In actual implementation, you'll pass streamlit's session_state to CacheManager
class MockSessionState:
    pass

mock_state = MockSessionState()
cache_manager = CacheManager(mock_state)
cache_manager
