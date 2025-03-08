import pandas as pd
import numpy as np
import plotly as pl
import dash as ds
import yfinance as yf
import time

start_time = time.time()

class TickerReturns():
    def __init__(self):
        self.ticker_list = []
        self.index_ticker = "^GSPC"
        self.tbill_30y_ticker = "^TYX"
        self.period = "20y"
        self.interval = "1mo"
        self.all_tickers_returns_df = pd.DataFrame()
        self.sp500_excess_returns_df = pd.DataFrame()
        self.index_returns_data = pd.DataFrame()
        self.monthly_tbill_yield = pd.DataFrame()

        self.ticker_returns_df = pd.DataFrame()
        self.ticker_excess_returns = pd.DataFrame()

    #Transforming the list (input by the user) into the list of the instance 
    #Important for fetching the data
    def set_ticker_list(self,list_input):
        self.ticker_list = list_input
        return self.ticker_list
    
    #Calculating Monthly Returns of all tickers inside the self.ticker_list
    def get_all_returns_df(self):
        
        all_tickers_returns_df = pd.DataFrame()

        #Iteration of each ticker in the ticker list to add into one single df
        for each_ticker in self.ticker_list:
            ticker_info = yf.Ticker(each_ticker)
            historical_data = pd.DataFrame(ticker_info.history(period=self.period,interval=self.interval))
            
            #This pct change method will get exactly the returns we need from each given ticker
            ticker_returns_data = historical_data['Close'].astype(float).pct_change()
            ticker_returns_data.name = f"{each_ticker} Returns"
            
            #Adding each pandas Series (Close column) to the df to put everything in one df
            all_tickers_returns_df = pd.concat([all_tickers_returns_df,ticker_returns_data],axis=1)

        #Setting the index of the df to datetime (done to all dfs for compatibility)
        all_tickers_returns_df.index = pd.to_datetime(all_tickers_returns_df.index).date

        self.all_tickers_returns_df = all_tickers_returns_df
        
        return self.all_tickers_returns_df
    
    #Function will only provide the returns for one ticker
    #Doing a df with all returns is too inefficient (especially if the user select several tickers in the webapp)
    def get_ticker_returns_df(self, ticker):

        ticker_info = yf.Ticker(ticker)
        historical_data = pd.DataFrame(ticker_info.history(period=self.period,interval=self.interval))
        
        #This pct change method will get exactly the returns we need from each given ticker
        ticker_returns_data = historical_data['Close'].astype(float).pct_change()
        ticker_returns_data.name = f"{ticker} Returns"
        ticker_returns_data.index = pd.to_datetime(ticker_returns_data.index).date
        self.ticker_returns_df = ticker_returns_data

        return self.ticker_returns_df
    

    def get_monthly_tbill_yield(self):
        tbill_info = yf.Ticker(self.tbill_30y_ticker)
        tbill_historical_data = pd.DataFrame(tbill_info.history(period=self.period,interval=self.interval))

        #Converting each of the risk free rate to a monthly risk free rate and adding to a df
        #Notice we are using a simple interest approach (common in excess return calculations)
        tbill_historical_data['Monthly Rate'] = tbill_historical_data['Close']/12/100

        monthly_tbill_yield = tbill_historical_data['Close']/12/100
        monthly_tbill_yield.name = f"{self.tbill_30y_ticker} Monthly Rate"
        monthly_tbill_yield.index = pd.to_datetime(monthly_tbill_yield.index).date
        self.monthly_tbill_yield = monthly_tbill_yield
        
        return self.monthly_tbill_yield
    
    def get_sp500_monthly_returns(self):
        index_info = yf.Ticker(self.index_ticker)
        index_historical_data = pd.DataFrame(index_info.history(period=self.period,interval=self.interval))
            
        #pctchange() method will get exactly the returns we need from each given ticker
        index_returns_data = index_historical_data['Close'].astype(float).pct_change()
        index_returns_data.name = "SP500 Monthly Returns"
        index_returns_data.index = pd.to_datetime(index_returns_data.index).date

        self.index_returns_data = index_returns_data

        return self.index_returns_data
 
    #Use of SP500 as the proxy (data availability, liquidity of assets and 
    #Most importantly most diversifiable index - evaluation of systematic risk)
    def get_sp500_excess_returns_df(self):
        #Calculating Excess Returns
        #Excess Returns = Returns on investment - Returns on a risk-free investment (proxy)
        #Returns on investments will be the monthly returns of each asset
        #Proxy for all returns (sp500 and stocks) will be the monthly risk-free rate of 20y T-Bills
        self.get_sp500_monthly_returns()
        self.get_monthly_tbill_yield()

        #Creating a DataFrame with both Series (aligned by date, since they have the same indexes)
        combined_df = pd.DataFrame({
            f'Index_Returns':self.index_returns_data,
            f'Risk_Free_Rate':self.monthly_tbill_yield
        })
        
        #I noticed that 06/24 - 02/25 dates are not available in the Tbills, so I am removing them with dropna
        #Now I will only have cells that are present on both columns
        combined_df = combined_df.dropna()

        excess_returns_col = 'SP500 Excess Returns (%)'

        combined_df[excess_returns_col] = (combined_df['Index_Returns'] - combined_df['Risk_Free_Rate'])*100

        #Detecting outliers using the IQR method
        #Calculating the upper and lower limits
        Q1 = combined_df[excess_returns_col].quantile(0.25)
        Q3 = combined_df[excess_returns_col].quantile(0.75)
        IQR = Q3 - Q1
        
        #These would be the lower and upper bounds of the dataframe with no outliers
        lower = Q1 - 1.5*IQR
        upper = Q3 + 1.5*IQR

        #Counting outliers (bigger than upper bound)
        upper_outliers = combined_df[excess_returns_col] > upper

        #Counting outliers (smaller than lower bound)
        lower_outliers = combined_df[excess_returns_col] < lower

        #Adding all outliers
        all_outliers = upper_outliers | lower_outliers

        #Creating a DataFrame that contains only the rows where all_outliers is false
        #~ is a bitwise NOT operator (so it will select only NON-outliers)
        combined_df_filtered = combined_df[~all_outliers]

        # Report removal
        print(f"Removed {all_outliers.sum()} outliers from {excess_returns_col} ")

        self.sp500_excess_returns_df=combined_df_filtered[excess_returns_col]

        return self.sp500_excess_returns_df

    #Getting the excess returns of a particular ticker
    def ticker_excess_returns_df(self,ticker):

        #Getting monthly returns dataframe 
        self.get_ticker_returns_df(ticker)
        #Getting monthly tbill yield dataframe
        self.get_monthly_tbill_yield()

        #Creating a copy to not alter the original dataset
        ticker_returns = self.ticker_returns_df.copy()
        tbill_yield = self.monthly_tbill_yield.copy()

        #Column name in which we are fetching given ticker returns data
        ticker_returns_column = f'{ticker} Returns'

        #Creating df with ticker returns and risk free rate for calculation of excess returns
        combined_df=pd.DataFrame({
            ticker_returns_column:ticker_returns,
            f'Risk_Free_Rate':tbill_yield
        })

        #Dropping rows with missing values
        combined_df = combined_df.dropna()


        #Calculating excess returns
        excess_returns_col = f'{ticker} Excess Returns (%)'
        combined_df[excess_returns_col] = (combined_df[ticker_returns_column] - combined_df['Risk_Free_Rate'])*100

        #Detecting outliers using the IQR method
        #Calculating the upper and lower limits
        Q1 = combined_df[excess_returns_col].quantile(0.25)
        Q3 = combined_df[excess_returns_col].quantile(0.75)
        IQR = Q3 - Q1
        
        #These would be the lower and upper bounds of the dataframe with no outliers
        lower = Q1 - 1.5*IQR
        upper = Q3 + 1.5*IQR

        #Counting outliers (bigger than upper bound)
        upper_outliers = combined_df[excess_returns_col] > upper

        #Counting outliers (smaller than lower bound)
        lower_outliers = combined_df[excess_returns_col] < lower

        #Adding all outliers
        all_outliers = upper_outliers | lower_outliers

        #Creating a DataFrame that contains only the rows where all_outliers is false
        #~ is a bitwise NOT operator (so it will select only NON-outliers)
        combined_df_filtered = combined_df[~all_outliers]

        # Report removal
        print(f"Removed {all_outliers.sum()} outliers from {excess_returns_col}")
        
        self.ticker_excess_returns = combined_df_filtered[excess_returns_col]
    
        return self.ticker_excess_returns