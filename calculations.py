import time
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def calculate_portfolio_volatility(portfolio_weights, portfolio_histories):
    """
    Calculates the portfolio volatility given a portfolio 
    of stocks, weights and their historical prices.

    Parameters
    ----------
    portfolio_weights : dict
        A dictionary containing stock tickers as keys 
        and their corresponding portfolio weights as values.
    portfolio_histories : dict
        A dictionary containing stock tickers as keys 
        and their corresponding historical prices as values.

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

    # Format the weights and historical prices 
    weights = np.array(list(portfolio_weights.values()))
    historical_prices = pd.DataFrame(portfolio_histories).sort_index()

    # Calculate the returns
    returns = historical_prices.pct_change()

    # Calculate the covariance matrix
    cov_matrix = returns.cov() * 252  # We multiply by 252 to annualize the covariance

    # Calculate the portfolio volatility
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    return portfolio_volatility


def calculate_portfolio_beta(portfolio_weights, portfolio_histories, market_history):
    """
    Calculates the portfolio beta given a portfolio
    of stocks and weights.

    Parameters
    ----------
    portfolio_weights : dict
        A dictionary containing stock tickers as keys 
        and their corresponding portfolio weights as values.
    portfolio_histories : dict
        A dictionary containing stock tickers as keys 
        and their corresponding historical prices as values.
    market_history : dict
        A dictionary containing the historical prices of the
        market (SPY).

    Returns
    -------
    float
        The portfolio beta. Returns np.nan if historical 
        prices cannot be retrieved or if the portfolio is empty.
    """ 
    
    # Check if the portfolio is empty
    if not portfolio_weights:
        st.warning("The portfolio is empty. Unable to calculate beta.")
        return np.nan

    # Format the weights and historical prices 
    weights = np.array(list(portfolio_weights.values()))
    historical_prices = pd.DataFrame(portfolio_histories).sort_index()
    market_historical_prices = pd.Series(market_history).sort_index()

    # Calculate the returns
    returns = historical_prices.pct_change()

    # Calculate the market returns
    market_returns = market_historical_prices.pct_change()

    # Calculate the covariance of the returns of each stock with the market
    cov_with_market = returns.apply(lambda x: x.cov(market_returns))

    # Calculate the variance of the market
    market_variance = market_returns.var()

    # Calculate the beta for each stock
    beta = cov_with_market / market_variance

    # Calculate the portfolio beta
    portfolio_beta = np.sum(weights * beta)

    return portfolio_beta