import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from portfolio import Portfolio, update_portfolio, manage_portfolio 
from display import display_strategy_summary, display_portfolio, display_last_refresh_time
from api_manager import IBKRApp


if __name__ == '__main__': 
    st.title('Portfolio Summary')

    # Initialize the connection message 
    ibkr_connection_message = None 

    # Retrieve or initialize the portfolio object from the session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio()
        st.session_state.portfolio.load_cache()

    # Instantiate and start the API app if not already in the session state
    if 'ibkr_app' not in st.session_state:
        ibkr_connection_message = st.info("Connecting to IBKR...")
        st.session_state.ibkr_app = IBKRApp()
        st.session_state.ibkr_app.start_thread()

        # Wait until connected
        while not st.session_state.ibkr_app.is_connected:
            time.sleep(1)

    # Check if IBKR connected
    if st.session_state.ibkr_app.is_connected:
        # Wait for API call to retrieve live portfolio
        time.sleep(30)
        
        # Get holdings and historical data
        live_holdings = st.session_state.ibkr_app.get_live_portfolio()
        historical_data = st.session_state.ibkr_app.get_historical_data()

        # Clear the connection message
        if ibkr_connection_message:
            ibkr_connection_message.empty()

        # Make sure there are holdings before proceeding
        if live_holdings and historical_data:
            # Update the portfolio based on API data
            update_portfolio(st.session_state.portfolio, live_holdings, historical_data)
            
            # Display the last refresh time
            display_last_refresh_time(st.session_state.portfolio)

            # Allow management of strategies through a sidebar
            manage_portfolio(st.session_state.portfolio)

            # Display the current portfolio
            display_strategy_summary(st.session_state.portfolio)

        else:
            st.warning("No portfolio data received yet.")

    # Automatic refresh after a specified amount of time
    refresh_interval = 120 # seconds
    st_autorefresh(interval=refresh_interval * 1000)
