import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from portfolio import Portfolio, update_portfolio, manage_portfolio 
from display import display_strategy_summary, display_portfolio, display_last_refresh_time
from api_manager import IBKRApp, IBKRAppSPY


# Cache portfolio between page refreshes
@st.cache_data
def init_portfolio(ttl=None, show_spinner=False):
    portfolio = Portfolio()
    portfolio.load_cache()
    return portfolio

# Cache API instance between page refreshes
@st.cache_resource
def init_ibkr_app(ttl=None):
    ibkr_app = IBKRApp()
    ibkr_app.start_thread()
    while not ibkr_app.is_connected:
        time.sleep(1)
    return ibkr_app

# Cache SPY API instance between page refreshes
@st.cache_resource
def init_ibkr_app_spy(ttl=None):
    ibkr_app_spy = IBKRAppSPY()
    ibkr_app_spy.start_thread()
    while not ibkr_app_spy.is_connected:
        time.sleep(1)
    return ibkr_app_spy


# Dashboard
if __name__ == '__main__': 
    st.title('Portfolio Summary')
    
    # Instantiate and load cache for the portfolio
    portfolio = init_portfolio()
    
    # Instantiate and start the API service
    ibkr_app = init_ibkr_app()
    ibkr_app_spy = init_ibkr_app_spy()

    # Display messagae if it's the first load
    first_load_placeholder = st.empty()
    if 'first_load' not in st.session_state:
        st.session_state.first_load = True
        first_load_placeholder.info("Connecting to IBKR...")
    else:
        st.session_state.first_load = False

    # Check if IBKR connected
    if ibkr_app.is_connected and ibkr_app_spy.is_connected:
        # Give some time for apps to start fetching updates
        time.sleep(20)

        # Get holdings and historical data
        live_holdings = ibkr_app.get_live_portfolio()
        historical_data = ibkr_app.get_historical_data()
        historical_data_spy = ibkr_app_spy.get_historical_data()

        # Make sure there are holdings before proceeding
        if live_holdings and historical_data and historical_data_spy:
            # Remove connection message
            first_load_placeholder.empty()
            
            # Update the portfolio based on API data
            update_portfolio(portfolio, live_holdings, historical_data)
            
            # Display the last refresh time
            display_last_refresh_time(portfolio)

            # Allow management of strategies through a sidebar
            manage_portfolio(portfolio)

            # Display the current portfolio
            display_strategy_summary(portfolio, historical_data_spy)

        else:
            st.warning("No portfolio data received yet.")

    # Automatic refresh after a specified amount of time
    refresh_interval = 25 # seconds
    st_autorefresh(interval=refresh_interval * 1000)
