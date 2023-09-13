import time
import threading
from datetime import datetime
from typing import Dict
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.common import BarData


class IBKRApp(EWrapper, EClient):
    """
    A class to interface with IBKR and retrieve live portfolio updates.

    Attributes
    ----------
    portfolio_updates : dict
        Dictionary storing live portfolio updates, indexed by stock symbol.
    thread : threading.Thread or None
        Thread for running the IBKR app.
    lock : threading.Lock
        Lock for ensuring thread safety when accessing `portfolio_updates`.
    """

    def __init__(self):
        EClient.__init__(self, self)
        self.is_connected = False
        
        self.thread = None
        self.lock = threading.RLock()
        
        self.managed_accounts = []
        
        self.live_portfolio = {}
        self.net_liquidation = 0

        self.historical_data = {}
        self.historical_data_requests = {}
        self.reqId_counter = 0
        
    def connectAck(self):
        """
        Callback method that is called when a connection to the server is acknowledged.

        This method is part of the EWrapper and is automatically invoked when 
        the connection to the TWS/IB Gateway has been successfully established.

        Sets the `is_connected` attribute to True.

        Returns
        -------
        None
        """
        self.is_connected = True

    def connectionClosed(self):
        """
        Callback method that is called when the connection to the server is closed.

        This method is part of the EWrapper and is automatically invoked when 
        the connection to the TWS/IB Gateway is lost or manually closed.

        Sets the `is_connected` attribute to False.

        Returns
        -------
        None
        """
        self.is_connected = False

    def managedAccounts(self, accountsList: str):
        """
        Callback method that is called with the list of managed accounts.

        Parameters
        ----------
        accountsList : str
            Comma-separated list of managed accounts.
        """
        self.managed_accounts = accountsList.split(',')
        for account in self.managed_accounts:
            self.reqAccountUpdates(True, account)
    
    def updatePortfolio(self, contract, position, marketPrice, marketValue,
                        averageCost, unrealizedPNL, realizedPNL, accountName):
        """
        Callback function to update the portfolio.

        Parameters
        ----------
        contract : Contract
            An object representing details about the stock/contract.
        position : float
            Number of active positions for the contract.
        marketPrice : float
            Current market price of the contract.
        marketValue : float
            Current market value of the contract.
        averageCost : float
            Average cost of the contract.
        unrealizedPNL : float
            Unrealized profit and loss for the contract.
        realizedPNL : float
            Realized profit and loss for the contract.
        accountName : str
            Name of the account.
        """
        if contract.secType == "STK":
            with self.lock:
                self.live_portfolio[contract.symbol] = {
                    'market_value': marketValue,
                    'currency': contract.currency,
                }     
        self.request_historical_data(contract)
    
    def updateAccountValue(self, key, val, currency, accountName):
        """
        Callback for account-related values.
    
        Parameters
        ----------
        key : str
            The type of account info. ("AvailableFunds", "TotalCashValue", etc.)
        val : str
            The value associated with the specified key.
        currency : str
            The currency of the specified value.
        accountName : str
            The account name.
        """
        with self.lock:
            if key == "NetLiquidation":
                self.net_liquidation = float(val)

    def historicalData(self, reqId, bar: BarData):
        """
        Callback method to handle the received historical data for a stock.
        It is invoked when the historical data for a stock is received.
    
        Parameters
        ----------
        reqId : int
            The request ID associated with the historical data request.
        bar : BarData
            The bar data containing the historical data for the stock.
        """
        with self.lock:
            symbol = self.historical_data_requests.get(reqId, None)
            if symbol is None:
                return
            if symbol not in self.historical_data:
                self.historical_data[symbol] = {}
            self.historical_data[symbol][bar.date] = bar.close

    def request_historical_data(self, contract):
        """
        Request the historical data for a given stock contract.
    
        Parameters
        ----------
        contract : Contract
            The stock contract for which historical data is to be retrieved.
        """
        contract.exchange = "SMART"
        
        DURATION = "90 D"
        BAR_SIZE = "1 day"
        WHAT_TO_SHOW = "TRADES"

        with self.lock:
            self.reqId_counter += 1
            reqId = self.reqId_counter
            self.historical_data_requests[reqId] = contract.symbol
        
        self.reqHistoricalData(
            reqId=reqId,
            contract=contract,
            endDateTime="",
            durationStr=DURATION,
            barSizeSetting=BAR_SIZE,
            whatToShow=WHAT_TO_SHOW,
            useRTH=0,
            formatDate=1,
            keepUpToDate=False,
            chartOptions=[],
        )
    
    def run_app(self):
        """
        Connect and run the app. Initializes connection with IBKR 
        and requests account updates.
        """
        try:
            self.connect("127.0.0.1", 7497, 0)
            self.run()
        except Exception as e:
            print(f"Error connecting or running the IBKR App: {e}")

    def start_thread(self):
        """
        Start the data retrieval in a separate thread.
        """
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_app)
            self.thread.start()

    def stop_thread(self):
        """
        Stop the IBKR connection and the associated thread.
        """
        self.reqAccountUpdates(False, "")
        self.disconnect()
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def get_live_portfolio(self):
        """
        Get a copy of the live portfolio updates.

        Returns
        -------
        dict
            Dictionary containing live portfolio updates indexed by 
            stock symbol.
        """
        with self.lock:
            if not self.live_portfolio:
                raise ValueError("No portfolio data received from the API yet.")
                
            weights = {
                stock: stock_details['market_value'] / self.net_liquidation 
                for stock, stock_details in self.live_portfolio.items()
            }
        return weights

    def get_historical_data(self):
        """
        Retrieve the historical closing prices for stocks in the portfolio.
    
        Returns
        -------
        dict
            A dictionary with stock symbols as keys and lists of historical 
            closing prices as values.
    
        Raises
        ------
        ValueError
            If no historical data has been received from the API yet.
        """
        with self.lock:
            if not self.historical_data:
                raise ValueError("No historical data received from the API yet.")
            return self.historical_data
            

class IBKRAppSPY(EClient, EWrapper):
    """
    A class to retrieve historical closing prices for SPY over the last 
    90 days using the IBKR API.

    Attributes
    ----------
    historical_data : dict
        Dictionary to store the historical closing prices for SPY.
    lock : threading.Lock
        Lock for ensuring thread safety when accessing shared resources.
    thread : threading.Thread or None
        Thread for running the IBKRAppSPY.
    data_retrieved : threading.Event
        Event to signal when the historical data has been retrieved.
    """

    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        
        self.historical_data = {}
        
        self.lock = threading.Lock()
        self.thread = None

    def nextValidId(self, orderId):
        """
        Callback method that is called when the next valid order ID is received.
        """
        self.request_historical_data()

    def request_historical_data(self):
        """
        Send historical data requests for SPY.
        """
        contract = Contract()
        contract.symbol = "SPY"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
            
        self.reqHistoricalData(
            reqId=1,
            contract=contract,
            endDateTime="",
            durationStr="90 D",
            barSizeSetting="1 day",
            whatToShow="TRADES",
            useRTH=0,
            formatDate=1,
            keepUpToDate=False,
            chartOptions=[]
        )

    def historicalData(self, reqId, bar):
        """
        Callback method to populate the historical_data dictionary 
        with the closing prices.
        """
        with self.lock:
            self.historical_data[bar.date] = bar.close

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        """
        Callback method that is called when historical data for a 
        request is finished.
        """
        self.disconnect()

    def run_app(self):
        """
        Connect and run the app. Initializes connection with IBKR.
        """
        try:
            self.connect("localhost", 7497, clientId=1)
            self.run()
        except Exception as e:
            print(f"Error connecting or running the IBKR_SPY_HistoricalData: {e}")

    def start_thread(self):
        """
        Start the data retrieval in a separate thread.
        """
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_app)
            self.thread.start()

    def stop_thread(self):
        """
        Stop the IBKR connection and the associated thread.
        """
        self.disconnect()
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def get_historical_data(self):
        """
        Returns the historical_data dictionary.

        Returns
        -------
        dict
            Dictionary with dates as keys and closing prices as values.
        """
        with self.lock:
            return self.historical_data.copy()


def test():
    import pandas as pd
    
    app = IBKRApp()
    app.start_thread()

    spy_app = IBKRAppSPY()
    spy_app.start_thread()
    
    try:
        # Give the app some time to connect and start fetching updates
        time.sleep(5)

        # Display portfolio        
        portfolio = app.get_live_portfolio()
        historical_data = app.get_historical_data()
        
        # Get SPY data
        spy_app.thread.join()
        spy_historical_data = spy_app.get_historical_data()
        
        print("Live Portfolio Updates:")
        print(portfolio)
        
        print("Historical Closing Prices:")
        print(pd.DataFrame(historical_data).sort_index())
        
        print("Historical SPY Closing Prices:")
        print(pd.DataFrame({'SPY': spy_historical_data}).sort_index())

    finally:
        app.stop_thread()


if __name__ == "__main__":
    test()