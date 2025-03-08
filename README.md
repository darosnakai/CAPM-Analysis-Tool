# CAPM-Based Risk and Return Analysis

## Overview
This application provides Capital Asset Pricing Model analysis tool for stocks listed in the S&P500, allowing users to calculate Expected Returns, Beta and Alpha for the given asset. The appliction uses 20-year historical data from Yahoo Finance (using the yfinance API), Plotly and Dash for plotting the graph. 

## What is CAPM?
CAPM is a model that measures an asset's expected returns based on systematic risk (undiversifiable risk). It quantifies how much an asset moves to the overall market or a proxy.

**CAPM Formula:** *E(rA) = rf + βA × (E(rm) - rf)*

Where:

- **Beta (β):** Represents the asset's sensitivity to market movements (essentially showing its systematic risk). If an asset's beta is 2, then you expect the asset to have 2% if the market has 1% returns, or -2% returns if the market has -1% return
- **rf:** Risk-free rate (Treasury Bills 20yr interest rate)
- **E(rm):** Expected returns of the market. There are many ways to calculate this, but this application is using historical returns of the given asset and market. 
-**E(rA):** Expected returns of an asset

### Expected Returns
While CAPM technically gives us an estimate of future expected returns based on past returns, it assumes that the historical relationship between the stock and the market (Beta) will remain constant in the future, which is not the case. Even though CAPM grasps the relationship between the stock and the market, this relationship changes over time. When using the historical returns of the S&P500 as expected returns, we assume the past 20 years of returns will repeat in the future. 

## Interpreting Results
The application uses the yFinance module to extract monthly returns of a given stocks (selected by the user) and calculates their excess returns when compared to the risk-free rate (Excess Returns = Asset Returns - Risk-Free Returns). It does the same calculation for the S&P500. For each monthly interval, the application will calculate the given excess return of the asset and the S&P500, finally plotting them all in a scatter plot. Each blue dot in the plot corresponds to the Excess Returns of the asset and of the S&P500 at each given month in the past 20 years:

SCATTER PLOT HERE

### Regression (Best-Fitting) Line (y = βx + α)
The model performs linear regression using the plotted points, creating the orange best-fitting line, and calculates R-Squared. Simply, linear regression is responsible for analyzing all the points in the scatter plot and calculating what is the line that best fits to all points together. This linear regression is responsible for finding the Beta (β) and Alpha (α), which correspond to the slope (β) and y-intercept (α) of the line, respectively. 

### Beta (β) and Alpha (α)
Beta (β), slope of the best-fitting line, refers to the asset's sensitivity to movements in a given market (S&P500), essentially showing its systematic risk (undiversifiable risk). Alpha (α), y-intercept of the best fitting line, is the excess return of the asset when the return of the market (S&P500) is 0%. It suggests if the asset outperforms or underperforms the given market. The principal assumption of CAPM is that returns can be explained entirely by the asset's risk relationship with the market. If a stock follows CAPM perfectly, then alpha should be 0 (only beta should affect the asset's change in price). When a stock has a non-negligible alpha, this means that it is a deviation from the expected performance using CAPM as a benchmark, in other words, CAPM might be insufficient for calculating this asset's returns.

### Removing Outliers
It was necessary to remove outliers for a more accurate understanding of the asset's behavior compared to the S&P500 and better analyze central tendency. The method used was the IQR method. 

## Future Work
- Create a dataset with the betas, alphas and r2's of the given stocks selected by the user

- Button to create a portfolio with a given weight for each asset selected by the user, calculate the beta of this portfolio and its expected returns compared to the S&P500

## Additions to the Application
- Rolling Beta Analysis (shows dynamic risk changes)
- Risk-Adjusted Performance Metrics (Sharpe & Treynor)
- Jensen’s Alpha (better CAPM performance evaluation)
- Monte Carlo Simulations (simulate future scenarios)
- Expected Return Forecasting (forward-looking CAPM)