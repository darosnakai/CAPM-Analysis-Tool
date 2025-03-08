from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate
from ticker_analyzer import TickerReturns

#Creating instance for CAPMRegression
capm_regression = TickerReturns()

index_name = "SP500"

app = Dash(__name__)

colors = {
    'background': '#F3F4F4',
    'text': '#464747',
    'button':'#324B4C',
    'title':'#a73a00',
    'trendline':'#e66e2d',
    'scatter_points':'#00adbc'
}


def get_all_tickers():
    try:
        filepath = "capm-scatter-plot/data/sp500_components.html"
        print(f"Attempting to read file at: {filepath}")

        all_stocks = pd.read_html(filepath)[0]
        
        #get value at rows i, column 0 (first column)
        all_tickers = [all_stocks.iloc[i, 0] for i in range(len(all_stocks))]
        
        # Create dropdown options
        ticker_options = [{'label': ticker, 'value': ticker} for ticker in all_tickers]
        return ticker_options
    
    except Exception as e:
        print(f"Error loading tickers: {e}")
        #Using magnificent 7 as fallback in case function does not run properly
        fallback_tickers_mag_7 = ["AAPL","MSFT","TSLA","GOOG","AMZN","NVDA","META"]
        return [{'label': ticker, 'value': ticker} for ticker in fallback_tickers_mag_7]

ticker_options = get_all_tickers()
ticker_list = capm_regression.set_ticker_list(ticker_options)

#Editting the layout of the app
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1('CAPM Regression w/ Excess Returns',style={
        'textAlign': 'center',
        'color': colors['title'],
        'marginBottom': '20px',
        'fontSize':'25px'
    }),

    dcc.Markdown('''
    **Purpose and Objective**
    This WebApp uses the yFinance API, allowing the user to create a portfolio with any stocks they want. Each stock is given a weight in the portfolio,
                 and the user can also select this. For each of the stocks, an individual scatter plot will be created, comparing the 
                 Excess Returns of the SP500 and the particular stock. The App will also create this same model for the created portfolio, 
                 so the user can identify the expectation of returns from the given portfolio.
                 
    **What is CAPM?**
    CAPM (Capital Asset Pricing Model) is a financial model developed to evaluate an asset's price, it involves calculating an
                 asset's price based on the risk relationship (volatility) with a particular market. 

    **Beta and Alpha**
    CAPM's Beta and Alpha can be calculated using a linear regression model between the excess returns of a diversified market (S&P500) and a particular stock.
                 The linear regression model will create what is called a "best-fitting" line (y = mx + b), that will map all the points in the 
                 scatter plot and figure out what is the line that best corresponds to all points when observed together. The slope of this line is called Beta,
                 which refers to the asset's sensitivity to movements in a given market (SP500). The y-intercept is the Alpha, referring to the excess return of the asset
                 when the return of the market (SP500) is 0%. It suggests if the asset outperforms or underperforms the given market.
                 The principal assumption of CAPM is that returns can be explained entirely by the asset's risk relationship with the market. If a stock follows CAPM 
                 perfectly, then alpha should be 0 (only beta should affect the asset's change in price). When a stock has a non-zero alpha, this means that it is a 
                 deviation from the expected performance using CAPM as a benchmark.
                 
    **Notice:** 
    While CAPM is an established model, modern research and current industry practices have diminished its uses with the advancements of financial modelling,
                 opting to other, newer models, such as the Fama-French model. However, it is important to grasp crucial concepts of CAPM usage and applications, while it
                 still is a widely used model in the financial industry.
                 
                 ''',style={'color': colors['text'], 
                            'backgroundColor': colors['background'],
                            'marginLeft': '5px',
                            'marginRight': '5px'
                            }),

    #Dropdown option so user can select tickers
    html.Div([
        html.Label("Select which assets (SP500 stocks) you want to add:", style={'color': colors['text'],'marginBottom':'10px'}),
        dcc.Dropdown(
            id="ticker_dropdown",
            options=ticker_options,
            multi=True,
            placeholder="Select tickers",
            style={'color': colors['text'], 
                   'backgroundColor': colors['background'],
                   'marginRight':'500px',
                    }
        ),
    ],style={'marginBottom':'20px', 'marginLeft':'5px','marginRight':'5px'}),

    #Run Analysis Button
    html.Div([
        html.Button('Run Analysis', id='run-analysis-button',style={
            'backgroundColor': colors['button'],
            'color': colors['background'],
            'padding': '10px 15px',
            'margin': '10px 0',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontSize': '16px',
        }),
    ],style={'textAlign':'center'}),
    #Loading Message
    html.Div(id='loading-message', style={'color': colors['text'], 'marginTop': '10px'}),
    #Output Container - so that the UI recognizes that only this part will be updated by the input
    html.Div(id='output-container', style={'color': colors['text'], 'marginTop': '20px'})
    
])

#Callback for the Run Analysis Button - this is what allows the webApp to be interactive
@app.callback(
    [Output('loading-message', 'children'),
     Output('output-container', 'children')],
    #When the user clicks it will run
    [Input('run-analysis-button','n_clicks')],
    #State parameter allos me to access the current value of components within the ticker_dropdown
    #Dash will retrieve the current value of the component with id 'ticker_dropdown'
    [State('ticker_dropdown', 'value')],
    prevent_initial_call = True
)

#The two parameter of the function (n_clicks, selected_tickers), correspond IN ORDER to the inputs and states in the callback decorator
#So if I added another input or state in the callback and added a third argument here, it would correspond to that one
def update_output_analysis(n_clicks,selected_tickers):
    if n_clicks is None:
        raise PreventUpdate
    
    if not selected_tickers or len(selected_tickers) == 0:
        return(
            html.Div("No tickers selected!", style={
        'textAlign': 'center',
        'color': colors['text'],
        'marginBottom': '15px',
        }),
            html.Div("Please select tickers using the dropdown above before running the analysis", style={
        'textAlign': 'center',
        'color': colors['text'],
        'marginBottom': '15px',
        })
        )
    
    #List with all the tickets inside the S&P 500
    capm_regression.set_ticker_list(ticker_options)
    
    #Fetching excess returns of sp500
    sp500_excess_returns_df = pd.DataFrame({'SP500 Excess Returns (%)':capm_regression.get_sp500_excess_returns_df()})
    
    #List that will contain all scatter plots for output
    all_scatter_plots = []

    #Mean because returns on S&P500 are relatively stable over time (compared to other equity markets)
    sp500_monthly_returns = capm_regression.get_sp500_monthly_returns()
    sp500_monthly_returns = sp500_monthly_returns.dropna()
    sp500_expected_returns = sp500_monthly_returns.mean()

    risk_free_rate = capm_regression.get_monthly_tbill_yield()
    risk_free_rate = risk_free_rate.dropna()
    rf = risk_free_rate.mean()
    
    #Running the Analysis from the ticker_analyzer file
    #Each iteration will generate a scatter plot for a given ticker with the S&P 500
    for each_ticker in selected_tickers:
        #Showing loading message
        loading_message = f'Creating Plot with {each_ticker}'
        html.Div(loading_message)

        #Excess Returns function in ticker_analyzer file will fetch the monthly returns of the ticker and the risk free rate dataframes
        #It will then calculate the excess return for any given interval (month) and return a dataframe with all of them (also handles nan values)
        ticker_excess_returns_df = capm_regression.ticker_excess_returns_df(each_ticker)
        
        #SP500 will do the same as explained above
        ticker_sp500_excess_returns = pd.concat([ticker_excess_returns_df,sp500_excess_returns_df],axis=1)
        
        #Doing a Scatter Plot for each ticker - using OLS for the trendline regression
        #This regression line will create the beta (slope) and the alpha (y-intercept)
        scatter_fig = px.scatter(
            ticker_sp500_excess_returns,
            x=f"{index_name} Excess Returns (%)",
            y=f"{each_ticker} Excess Returns (%)", 
            title=f'Scatter Plot of Monthly Excess Returns for {each_ticker} versus the {index_name}',
            trendline="ols"
            )
        
        #Fetching information from the trendline to add in the legend
        #Getting results of the trendline done with scatter_fig plot
        trendline_results = px.get_trendline_results(scatter_fig)
        
        #Trendline_results is a dataframe
        model_results = trendline_results.iloc[0]["px_fit_results"]

        #Fecthing beta, alpha and rsquared (found with ols regression line)
        beta = model_results.params[1]
        alpha = model_results.params[0]
        r_squared = model_results.rsquared

        #CAPM formula is: E[rA] = rf + βA × (E[rm] - rf)
        #rf and E[rm] are the same for all assets, so calculated before for loop
        expected_returns = rf + beta*(sp500_expected_returns-rf)
        
        #Updating the points of the scatter plot to match the color of the entire page
        scatter_fig.update_traces(
                selector=dict(type='scatter', mode='markers'), 
                marker=dict(
                color=colors['scatter_points'],
                size=8,
                opacity=0.7,
                line=dict(width=1,color=colors['text'])            
                ),showlegend=True,   
            name=f'{each_ticker} vs. {index_name} Excess Returns'  
        )

        #Adding annotation Expected Returns in the top left corner of the scatter plot
        scatter_fig.add_annotation(
        x=-8, 
        y=17.5,   
        text=f"{each_ticker} Expected Returns: {expected_returns:.2%}<br>Risk-Free Rate: {rf:.2%}<br>S&P500 Expected Returns: {sp500_expected_returns:.2%}",
        showarrow=False,
        align="left",
        font=dict(color=colors['text'])
        )

        #Modifying the color of the trendline to make it more aesthetic
        scatter_fig.update_traces(
                selector=dict(type='scatter', mode='lines'), 
                line=dict(
                color=colors['trendline'],        
                width=2.5,             
            ),
            showlegend=True,        
            name=f"Best-Fitting Line: Beta(β)={beta:.3f}; Alpha(α)={alpha:.3f}; R²={r_squared:.3f}"
        )
        
        #Modifying Appearance of the Plot
        scatter_fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            title_x=0.5
        )
        
        #Creating scatter plot with DCC graph
        scatter_plot=dcc.Graph(figure=scatter_fig)

        #Appending each scatter plot to the list of scatter plots
        all_scatter_plots.append(html.Div([
            scatter_plot,
            html.Hr() #Adding horizontal line between each plot
        ]))

        #Adding each figure to the webapp
        html.Div([
            html.Div(f'Scatter Plot of Monthly Excess Returns for {each_ticker} versus the {index_name}',style={
                'textAlign': 'center',
                'color': colors['text'],
                'marginBottom': '20px',
                'fontSize':'25px'
            }),
            scatter_plot
        ])

    return (
        html.Div("Analysis completed!",style={
        'textAlign': 'center',
        'color': colors['text'],
        'marginBottom': '20px',
        'fontSize':'20px'
        }),
        html.Div(all_scatter_plots) #Output container (list or tuple - look at callback)
    )

    
if __name__ == '__main__':
    app.run_server(debug=True)