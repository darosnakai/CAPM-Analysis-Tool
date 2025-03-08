import pandas as pd
import numpy as np
import plotly as pl
import dash as ds
import yfinance as yf
import time
import json

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
    
    def save_tickers_to_json(self):
        #Originally had wikipedia page (List of SP500 tickers) saved as html
        #This function converted this html file to a json file
        filepath = "capm-scatter-plot/data/sp500_components.html"
        print(f"Attempting to read file at: {filepath}")

        all_stocks = pd.read_html(filepath)[0]
        
        #get value at rows i, column 0 (first column)
        all_tickers = [all_stocks.iloc[i, 0] for i in range(len(all_stocks))]
        
        # Create dropdown options
        ticker_options = [{'label': ticker, 'value': ticker} for ticker in all_tickers]

        with open('capm-scatter-plot/data/sp500_tickers.json','w') as f:
            json.dump(ticker_options,f)
        
        print("Tickers saved to sp500_tickers.json")
        return True
    
    #Since files are already processed, not much is needed in this part

data = DataPreprocessor()

all_tickers = data.save_tickers_to_json()

print(len(all_tickers))