import time
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta


def calculate_portfolio_volatility(portfolio_weights):
    """
    Calculates the portfolio volatility given a portfolio 
    of stocks and weights.

    Parameters
    ----------
    portfolio_weights : dict
        A dictionary containing stock tickers as keys 
        and their corresponding portfolio weights as values.

    Returns
    -------
    float
        The portfolio volatility. Returns np.nan if historical 
        prices cannot be retrieved or if the portfolio is empty.
    """

    # Check if the portfolio is empty
    if not portfolio_weights:
        st.warning("The portfolio is empty. Unable to calculate volatility.")
        return np.nan

    # Define the time period
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')

    # Extract stocks and weights from the portfolio_weights
    stocks = list(portfolio_weights.keys())
    weights = np.array(list(portfolio_weights.values()))

    # Download the stock price data
    try:
        historical_prices = yf.download(stocks, start=start_date, end=end_date)['Adj Close']
    except Exception as e:
        st.warning(f"Unable to retrieve historical prices for {stocks}. Error: {e}")
        return np.nan

    # Calculate the returns
    returns = historical_prices.pct_change()    

    # Calculate the covariance matrix
    cov_matrix = returns.cov() * 252  # We multiply by 252 to annualize the covariance

    # Calculate the portfolio volatility
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    return portfolio_volatility


def calculate_portfolio_beta(portfolio_weights):
    """
    Calculates the portfolio beta given a portfolio
    of stocks and weights.

    Args:
        portfolio_weights (dict): A dictionary of tickers (keys)
        and their corresponding weights (values)

    Returns:
        float: The portfolio beta. Returns np.nan if historical 
        prices cannot be retrieved or if the portfolio is empty.
    """ 
    
    # Check if the portfolio is empty
    if not portfolio_weights:
        st.warning("The portfolio is empty. Unable to calculate beta.")
        return np.nan

    # Define the time period
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')

    # Extract stocks and weights from the portfolio_weights
    stocks = list(portfolio_weights.keys())
    weights = np.array(list(portfolio_weights.values()))

    # Download the stock price data
    try:
        historical_prices = yf.download(stocks, start=start_date, end=end_date)['Adj Close']
    except Exception as e:
        st.warning(f"Unable to retrieve historical prices for {stocks}. Error: {e}")
        return np.nan 

    # Calculate the returns
    returns = historical_prices.pct_change()

    # Download the market data
    try:
        spy_historical_price = yf.download('SPY', start=start_date, end=end_date)
    except Exception as e:
        st.warning(f"Unable to retrieve historical prices for SPY. Error: {e}")
        return np.nan  

    # Calculate the market returns
    market_returns = spy_historical_price['Adj Close'].pct_change()

    # Calculate the covariance of the returns of each stock with the market
    cov_with_market = returns.apply(lambda x: x.cov(market_returns))

    # Calculate the variance of the market
    market_variance = market_returns.var()

    # Calculate the beta for each stock
    beta = cov_with_market / market_variance

    # Calculate the portfolio beta
    portfolio_beta = np.sum(weights * beta)

    return portfolio_beta