import os
import json
from datetime import datetime
import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox


STRATEGY_OPTIONS = ['Run-up', 'Hedge', 'Hold', 'Medium', 'Long']


class Portfolio:
    """
    A class to manage a portfolio of stocks, each with a corresponding 
    weight and strategy.
    """

    def __init__(self):
        """Initializes an empty portfolio."""
        self.portfolio = {}
        self.historical_data = {} 
        self.last_refresh_time = None
        self.last_saved_time = None

    def add_stock(self, ticker, weight, strategy):
        """
        Adds a stock to the portfolio.

        Parameters
        ----------
        ticker : str
            The stock's ticker symbol.
        weight : float
            The weight of the stock in the portfolio.
        strategy : str
            The trading strategy associated with the stock (e.g., 
            'Run-up', 'Hedge', 'Hold', 'Medium', 'Long').
        """
        self.portfolio[ticker] = {'weight': weight, 'strategy': strategy}

    def update_stock(self, ticker, weight=None, strategy=None):
        """
        Updates the weight and/or strategy of a stock in the portfolio.

        Parameters
        ----------
        ticker : str
            The stock's ticker symbol.
        weight : float, optional
            The new weight of the stock (default is None).
        strategy : str, optional
            The new strategy associated with the stock (default is None).
        """
        if ticker in self.portfolio:
            if weight is not None:
                self.portfolio[ticker]['weight'] = weight
            if strategy is not None:
                self.portfolio[ticker]['strategy'] = strategy

    def remove_stock(self, ticker):
        """
        Removes a stock from the portfolio.

        Parameters
        ----------
        ticker : str
            The stock's ticker symbol.
        """
        if ticker in self.portfolio:
            del self.portfolio[ticker]
        if ticker in self.historical_data:
            del self.historical_data[ticker]

    def set_historical_data(self, ticker, data):
        """
        Set the historical data for a stock.

        Parameters
        ----------
        ticker : str
            The stock's ticker symbol.
        data : pd.DataFrame
            The historical data for the stock.
        """
        self.historical_data[ticker] = data
    
    def save_cache(self):
        """
        Save the current state of the portfolio to a JSON file.
        
        Notes
        -----
        This function will create a cache directory if it does 
        not exist and will save the strategy data in a file named 
        'strategy.json' within the cache directory.
        """
        cache_data = {
            'portfolio': self.portfolio,
            'last_saved_time': self.last_saved_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if not os.path.exists('cache'):
            os.makedirs('cache')
        with open('cache/strategy.json', 'w') as f:
            json.dump(cache_data, f)
        self.last_saved_time = datetime.now()

    def load_cache(self):
        """
        Load the portfolio state from a JSON file.
        
        Notes
        -----
        If the file is not found or there is an error in decoding 
        the file, a warning will be displayed to the user, and the 
        program will proceed without loading the strategies.
        """
        try:
            with open('cache/strategy.json', 'r') as f:
                cache_data = json.load(f)
                self.portfolio = cache_data['portfolio']
                self.last_saved_time = datetime.strptime(
                    cache_data['last_saved_time'], '%Y-%m-%d %H:%M:%S')
        except FileNotFoundError:
            st.warning('Cache not found. Starting with a clean slate.')
        except json.JSONDecodeError:
            st.warning('Error decoding cache. Starting with a clean slate.')
    
    def get_portfolio(self):
        """
        Returns the stocks in the portfolio.

        Returns
        -------
        dict
            A dictionary containing the stocks, with their ticker symbols 
            as keys, and corresponding weight and strategy as values.
        """
        return self.portfolio

    def get_weights(self):
        """
        Returns the weights in the portfolio.

        Returns
        -------
        dict
            A dictionary containing the ticker symbols 
            as keys, and corresponding weight as values.
        """
        return {ticker: data['weight'] for ticker, data in self.portfolio.items()}

    def get_strategies(self):
        """
        Returns the strategies in the portfolio.

        Returns
        -------
        dict
            A dictionary containing the ticker symbols 
            as keys, and corresponding strategies as values.
        """
        return {ticker: data['strategy'] for ticker, data in self.portfolio.items()}

    def get_historical_data(self, ticker=None):
        """
        Get the historical data for a stock or the entire portfolio.

        Parameters
        ----------
        ticker : str, optional
            The stock's ticker symbol. If None, returns the historical data 
            for the entire portfolio.

        Returns
        -------
        pd.DataFrame or dict of pd.DataFrame
            The historical data for the specified stock or for the entire portfolio.
        """
        if ticker:
            return self.historical_data.get(ticker, None)
        return self.historical_data
    
    def get_last_refresh_time(self):
        """
        Get the timestamp of the last refresh for the portfolio.
    
        Returns
        -------
        datetime or None
            The timestamp of the last refresh if the portfolio has been 
            refreshed, otherwise None.
        """
        return self.last_refresh_time

    def get_last_saved_time(self):
        """
        Get the timestamp of the last time the portfolio strategies
        were cached.
    
        Returns
        -------
        datetime or None
            The timestamp of the last save if the strategy has been 
            saved, otherwise None.
        """
        return self.last_saved_time


def update_portfolio(portfolio, holdings, historical_data):
    """
    Updates the portfolio based on data retrieved from the API call. 
    Detects new and removed stocks. If new stocks are detected, a prompt 
    will appear for users to select a strategy.

    Parameters
    ----------
    portfolio : Portfolio
        An instance of the Portfolio class representing the current 
        portfolio state.
    holdings : dict
        A dictionary retrieved from API call where keys are tickers 
        and values are weighting.
    historical_data : dict
        A dictionary containing historical data for stocks.
    """
    
    # Record the current time
    portfolio.last_refresh_time = datetime.now()
    
    # Get tickers of old portfolio and new portfolio
    old_tickers = set(portfolio.get_portfolio().keys())
    new_tickers = set(ticker for ticker, weight in holdings.items() if weight != 0)

    # Detecting removed stocks (in old but not in new)
    removed_tickers = old_tickers - new_tickers
    for ticker in removed_tickers:
        portfolio.remove_stock(ticker)
        st.success(f"{ticker} has been removed from the portfolio.")

    # Detecting new stocks (in new but not in old)
    added_tickers = new_tickers - old_tickers
    if added_tickers:
        # Create a placeholder that will hold the form
        placeholder = st.empty()

        # Create the form within the placeholder
        with placeholder.form(key='submit_strategy_form'):
            st.write("New stock(s) detected. Please choose their strategy:")
            
            # Log user strategy selections using dropdown menu
            selected_strategies = {}
            for ticker in added_tickers:
                selected_strategy = st.selectbox(
                    f"Strategy for {ticker}:", 
                    STRATEGY_OPTIONS,
                    key=ticker
                )
                selected_strategies[ticker] = selected_strategy
            
            # Display a button to submit the form
            submit_button = st.form_submit_button(label='Submit')
            
            # If the button is clicked, update portfolio with selected strategies
            if submit_button:
                for ticker, strategy in selected_strategies.items():
                    weight = holdings[ticker]
                    portfolio.add_stock(ticker, weight, strategy)
                    st.success(f"Strategy for {ticker} has been successfully submitted.")
                    
                # Remove the prompt from the screen once strategies have been submitted
                placeholder.empty()            

        # Update historical data for new stocks
        for ticker in added_tickers:
            portfolio.set_historical_data(ticker, historical_data[ticker])

    # Updating existing stocks (intersection of old and new)
    for ticker in new_tickers & old_tickers:
        weight = holdings[ticker]
        portfolio.update_stock(ticker, weight)
        portfolio.set_historical_data(ticker, historical_data[ticker])


def manage_portfolio(portfolio):
    """
    Manages the strategies of the stocks in the portfolio through a 
    Streamlit sidebar. Users can update stocks by changing strategy.

    Parameters
    ----------
    portfolio : Portfolio
        The Portfolio object containing the current portfolio.

    Returns
    -------
    Portfolio
        The updated portfolio with modified strategies.
    """
    st.sidebar.header('Manage Strategies')

    # Get stocks and sort them alphabetically by ticker
    stocks = portfolio.get_portfolio()
    sorted_tickers = sorted(stocks.keys())

    # Selectbox for choosing a ticker
    selected_ticker = st.sidebar.selectbox(
        'Select ticker to update strategy:',
        sorted_tickers,
        help='Choose a stock from the portfolio to manage.'
    )

    if selected_ticker:
        # Get the current strategy for the selected ticker
        current_strategy = stocks[selected_ticker]['strategy']

        # Select a new strategy
        new_strategy = st.sidebar.selectbox(
            'Choose a new strategy:',
            STRATEGY_OPTIONS,
            index=STRATEGY_OPTIONS.index(current_strategy),
            help='Select a new strategy from the dropdown.'
        )

        # Confirmation button to update strategy
        if st.sidebar.button('Update Strategy'):
            portfolio.update_stock(selected_ticker, strategy=new_strategy)
            st.sidebar.success(
                f"{selected_ticker} strategy updated to {new_strategy}."
            )
          