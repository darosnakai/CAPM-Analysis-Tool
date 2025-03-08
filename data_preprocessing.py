import pandas as pd
import numpy as np
import plotly as pl
import dash as ds
import yfinance as yf
import time

#Class serves to save files if needed. In case the user prefers to use local files instead of fetching from API
#Fetching a lot of data from the API can be inefficient, that is the reason for this file
class DataPreprocessor:
    def __init__(self):
        #Period and interval of all tickers will be the same for standardisation
        self.period = "20y"
        self.interval = "1mo"
        self.tbill_30y_ticker = "^TYX"
        self.index_ticker = "^GSPC"
        self.ticker_name = None

    #Get the ticker name of each ticker in the list (dont know how to do it learn)
    def get_ticker_name(self):
        return self.ticker_name
    
    #Method will fetch and save all historical data from a particular ticker
    def ticker_historical_data(self,ticker_list):
        #For loop to save monthly historical data of stocks individually
        for ticker_symbol in ticker_list:
            ticker_name = ticker_symbol
            ticker_obj = yf.Ticker(ticker_symbol)
            pathname = f'historical_stock_data_{ticker_name}_monthly_{self.period}.csv'
            hist_ticker = pd.DataFrame(ticker_obj.history(period=self.period,interval=self.interval))
            hist_ticker.to_csv(pathname)
            
            print(f"Saved Monthly (20y) Historical Data of {ticker_name} to {pathname}.csv")
        return pathname
    
    #Will use the SP500 for comparison (most accurate and efficient index data)
    def sp500_historical_data(self):
        index_ticker = self.index_ticker
        index_obj = yf.Ticker(index_ticker)
        pathname = f'historical_stock_data_{index_ticker}_monthly_{self.period}.csv'
        hist_ticker = pd.DataFrame(index_obj.history(period=self.period,interval=self.interval))
        hist_ticker.to_csv(pathname)
        return pathname
    
    #Getting the historical 20y monthly yield of the tbill
    def tbill_historical_rates(self):
        tbill = self.tbill_30y_ticker
        index_obj = yf.Ticker(tbill)

        pathname = f'yield_tbill_monthly_{self.period}.csv'
        hist_ticker = pd.DataFrame(index_obj.history(period=self.period,interval=self.interval))
        hist_ticker.to_csv(pathname)
        return pathname
    
    #Since files are already processed, not much is needed in this part