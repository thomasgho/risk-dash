import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from calculations import calculate_portfolio_volatility, calculate_portfolio_beta


def display_last_refresh_time(portfolio):
    """
    Displays the last refresh time of the portfolio.

    Parameters
    ----------
    portfolio : Portfolio
        An instance of the Portfolio class representing the current portfolio state.
    """
    last_refresh_time = portfolio.get_last_refresh_time()
    if last_refresh_time:
        # Format the timestamp
        formatted_time = last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')

        # Create a styled container to display the last refresh time
        st.markdown(
            f"""
            <div style="
                text-align: right; 
                font-size: small; 
                color: grey; 
                border-top: 1px 
                solid #f0f0f0; 
                padding-top: 10px;
            ">
                Last Refresh: {formatted_time}
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_portfolio(portfolio):
    """
    Displays a table of the portfolio, including ticker, strategy and weight.

    Parameters
    ----------
    portfolio : Portfolio
        An instance of the Portfolio class representing the current portfolio state.
    """

    stocks = portfolio.get_portfolio()
    sorted_stocks = sorted(stocks.items(), key=lambda x: x[1]['weight'], reverse=True)

    def get_color(weight):
        red_value = int(255 - weight * 2.55)
        green_value = int(weight * 2.55)
        return f'rgb({red_value}, {green_value}, 0)'

    # Styling
    title_style = (
        'font-size: 18px; font-weight: bold; color: #ffffff; '
        'border-bottom: 2px solid #f0f0f0; padding-bottom: 5px; '
        'margin-bottom: 10px;'
    )
    table_style = (
        'width: 100%; border-collapse: collapse; font-size: 14px; '
        'border: 1px solid #f0f0f0;'
    )
    th_style = (
        'padding: 8px; text-align: left; border-bottom: 1px solid #f0f0f0;'
    )
    td_style = (
        'padding: 8px; text-align: left; border-bottom: 1px solid #f0f0f0;'
    )
    weight_col_style = 'width: 70%;'

    # HTML Table for portfolio
    portfolio_table_html = (
        f'<div style="width: 45%; padding-right: 10px;">'
        f'<div style="{title_style}">Current Portfolio</div>'
        f'<table style="{table_style}">'
        f'<tr><th style="{th_style}">Ticker</th><th style="{th_style}">Strategy</th>'
        f'<th style="{th_style}{weight_col_style}">Weight</th></tr>'
    )

    for ticker, details in sorted_stocks:
        weight_percentage = details['weight'] * 100
        progress_bar_color = get_color(weight_percentage)
        progress_bar = (
            f'<div style="width: 100%; background-color: #f0f0f0;">'
            f'<div style="width: {weight_percentage}%; height: 10px; '
            f'background-color: {progress_bar_color};"></div></div>'
        )
        portfolio_table_html += (
            f'<tr><td style="{td_style}">{ticker}</td>'
            f'<td style="{td_style}">{details["strategy"]}</td>'
            f'<td style="{td_style}">{progress_bar} {weight_percentage:.2f}%</td></tr>'
        )
        
    portfolio_table_html += '</table></div>'
    st.markdown(portfolio_table_html, unsafe_allow_html=True)


def display_strategy_summary(portfolio):
    """
    Displays a table of the portfolio grouped by strategy, including weights, 
    volatility, and beta.

    Parameters
    ----------
    portfolio : Portfolio
        An instance of the Portfolio class representing the current portfolio state.
    """
    portfolio_weights = portfolio.get_weights()
    portfolio_strategies = portfolio.get_strategies()
    portfolio_historical = portfolio.get_historical_data()
    
    # Group tickers by strategy
    strategy_groups = {}
    for ticker, strategy in portfolio_strategies.items():
        if strategy not in strategy_groups:
            strategy_groups[strategy] = []
        strategy_groups[strategy].append(ticker)

    # Compute aggregate values by strategy
    data = []
    for strategy, tickers in strategy_groups.items():
        if strategy == 'Hedge':
            pass
        else:
            strat_weights = {ticker: portfolio_weights[ticker] for ticker in tickers}
            summed_weight = np.sum(list(strat_weights.values()))
            strat_histories = {ticker: portfolio_historical[ticker] for ticker in tickers}
            volatility = calculate_portfolio_volatility(strat_weights, strat_histories)
            beta = calculate_portfolio_beta(strat_weights, strat_histories)
            data.append([strategy, summed_weight, volatility, beta])

    # Compute values for the combined 'Run-up' and 'Hedge' strategies
    combined_strategies = ['Run-up', 'Hedge']
    combined_weights = {ticker: portfolio_weights[ticker] for ticker, strategy in portfolio_strategies.items() if strategy in combined_strategies}
    combined_weight = np.sum(list(combined_weights.values()))
    combined_histories = {ticker: portfolio_historical[ticker] for ticker, strategy in portfolio_strategies.items() if strategy in combined_strategies}
    combined_volatility = calculate_portfolio_volatility(combined_weights, combined_histories)
    combined_beta = calculate_portfolio_beta(combined_weights, combined_histories)
    data.append(['Run-up Hedged', combined_weight, combined_volatility, combined_beta])

    # Compute values for the entire portfolio
    total_weight = np.sum(list(portfolio_weights.values()))
    total_volatility = calculate_portfolio_volatility(portfolio_weights, portfolio_historical)
    total_beta = calculate_portfolio_beta(portfolio_weights, portfolio_historical)
    data.append(['Total', total_weight, total_volatility, total_beta])
    
    # Convert data to DataFrame for easier manipulation
    df = pd.DataFrame(data, columns=['Strategy', 'Summed Weights', 'Volatility', 'Beta'])

    # Styling
    title_style = (
        'font-size: 18px; font-weight: bold; color: #ffffff; '
        'border-bottom: 2px solid #f0f0f0; padding-bottom: 5px; '
        'margin-bottom: 10px;'
    )
    table_style = (
        'width: 100%; border-collapse: collapse; font-size: 14px; '
        'border: 1px solid #f0f0f0;'
    )
    th_style = (
        'padding: 8px; text-align: left; border-bottom: 1px solid #f0f0f0;'
    )
    td_style = (
        'padding: 8px; text-align: left; border-bottom: 1px solid #f0f0f0;'
    )

    # HTML Table for the strategy summary
    strategy_table_html = (
        f'<div style="width: 60%; padding-right: 10px;">'
        f'<table style="{table_style}">'
        f'<tr><th style="{th_style}">Strategy</th><th style="{th_style}">Weights</th>'
        f'<th style="{th_style}">Volatility</th><th style="{th_style}">Beta</th></tr>'
    )

    for index, row in df.iterrows():
        strategy_table_html += (
            f'<tr><td style="{td_style}">{row["Strategy"]}</td>'
            f'<td style="{td_style}">{row["Summed Weights"]:.2f}</td>'
            f'<td style="{td_style}">{row["Volatility"]:.2f}</td>'
            f'<td style="{td_style}">{row["Beta"]:.2f}</td></tr>'
        )
    
    strategy_table_html += '</table></div>'
    st.markdown(strategy_table_html, unsafe_allow_html=True)

