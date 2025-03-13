from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from ticker_analyzer import TickerReturns
import json

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
    'scatter_points':'#00adbc',
    'line_color_table':'black',
    'fill_color_col_table':'#1c884c',
    'fill_color_table':'#5bbe7d'

}

#Defining dictionaries for each different text 
text_styles = {
    'question': {
        'color': colors['text'],
        'fontSize': '18px',
        'fontWeight':'bold',
        'textAlign':'center',
        'marginBottom':'10px'
    },
    'long-question':{
        'color': colors['text'],
        'fontSize': '18px',
        'fontWeight':'bold',
        'textAlign':'center',
        'marginBottom':'10px',
        'marginLeft':'250px',
        'marginRight':'250px'
    },
    'label': {
        'color': colors['text'],
        'fontSize': '15px',
        'marginBottom': '10px'
    },
    'markdown': {
        'color': colors['text'],
        'backgroundColor': colors['background'],
        'marginLeft': '100px',
        'marginRight': '100px',
        'fontSize': '18px',
        'lineHeight': '1.4'
    },
    'title': {
        'textAlign': 'center',
        'fontWeight':'bold',
        'color': colors['title'],
        'marginBottom': '20px',
        'fontSize': '25px'
    },
    'subtitle': {
        'textAlign': 'center',
        'fontWeight':'bold',
        'color': colors['text'],
        'marginBottom': '15px',
        'fontSize': '21px'
    },
    'dropdown':{
        'backgroundColor': colors['background'],
        'marginLeft': '50px',
        'marginRight': '500px',
        'fontSize': '18px',
        'lineHeight': '1.4'
    },
    'radio':{
        'backgroundColor': colors['background'],
        'marginLeft': '100px',
        'marginRight': '100px',
        'fontSize': '16px',
        'lineHeight': '1.4',
        'textAlign':'center'
    },
    'button': {
        'backgroundColor': colors['button'],
        'color': colors['background'],
        'padding': '10px 15px',
        'margin': '10px 0',
        'border': 'none',
        'borderRadius': '4px',
        'cursor': 'pointer',
        'fontSize': '16px',
        'textAlign':'center'
    }
}


#Fetching tickers form the JSON file
def get_all_tickers():
    try:
        with open('capm-scatter-plot/data/sp500_tickers.json', 'r') as f:
            ticker_options = json.load(f)
        return ticker_options
    except Exception as e:
        print(f"Error loading tickers: {e}")
        # Using magnificent 7 as fallback
        fallback_tickers_mag_7 = ["AAPL","MSFT","TSLA","GOOG","AMZN","NVDA","META"]
        return [{'label': ticker, 'value': ticker} for ticker in fallback_tickers_mag_7]

ticker_options = get_all_tickers()
ticker_list = capm_regression.set_ticker_list(ticker_options)

#Editting the layout of the app
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1('Risk-Return Analysis of Stocks',style=text_styles['title']),

    dcc.Markdown('''
    **Purpose and Objective**
    This WebApp uses the yFinance, Plotly, Dash and OLS APIs, allowing the user to analyze the risk-return relationship of any stocks within the S&P 500. The program will calculate the Betas,
                 Jensen's Alphas (using the OLS best-fitting line module), R2 (of the best-fitting line), Sharpe Ratio, Treynor Ratio and Rolling CAPM Analysis (Rolling Beta, Rolling Alpha and
                 Rolling R2). This provides the user a comprehensive understanding and a clear visualization of assets' risk, and their relationship with the S&P 500.
                 
    **Analysis Tool**
    This program uses CAPM as the basis for the analysis. CAPM (Capital Asset Pricing Model) is a financial model developed to evaluate an asset's price, it involves calculating an asset's 
                 price based on the risk relationship (volatility) with a particular market. While this application uses CAPM for analysis, the analytical tools provided by the program
                 go further into analyzing any particular stocks (ie Rolling CAPM)

    **Rolling CAPM Analysis**
    Rolling CAPM calculates the key CAPM parameters (Beta, Alpha, and R-squared) over sequential time periods using a moving window of data. Rather than using the entire historical 
                 dataset to calculate a single Beta value, Rolling CAPM uses a fixed-size window (typically 12, 24, or 36 months) that "rolls" forward through time.                      
                 ''',style=text_styles['markdown']),

    #Dropdown option so user can select tickers
    html.Div([
        html.Label("Select which assets (SP500 stocks) you want to add:", style=text_styles['markdown']),
        dcc.Dropdown(
            id="ticker-dropdown",
            options=ticker_options,
            multi=True,
            placeholder="Select tickers",
            style=text_styles['dropdown']),
            ],
            style={'marginBottom':'20px'}
            ),

    #Run Analysis Button
    html.Div([
        html.Button('Run Analysis', id='run-analysis-button',style=text_styles['button']),
            ],style={'textAlign':'center'}),

    #Loading Message
    html.Div(id='loading-message', style={'color': colors['text'], 'marginTop': '10px'}),

    #Once Analysis runs, user will be able to select with scatter plots they want to see...
    #...instead of showing all scatter plots at once
    
    # Scatter Plot Controls - Initially hidden
    html.Div([
        html.Hr(),
        html.H3('Scatter Plot Visualization Options', style=text_styles['subtitle']),
        
        # First radio item - whether to display scatter plots
        html.Div([
            html.Label("Would you like to see scatter plots?", style=text_styles['question']),
            html.Div([
                dcc.RadioItems(
                    id='show-scatter-radio',
                    options=[
                        {'label': 'Yes, show scatter plots', 'value': 'yes'},
                        {'label': 'No, hide scatter plots', 'value': 'no'}
                    ],
                    value='no', #Default value
                    style=text_styles['radio']
                ),
            ],style={'display': 'flex', 'justifyContent': 'center', 'width': '100%'}),
        ], style={'marginBottom': '15px', 'textAlign': 'center', 'width': '100%'}),
        
        # Second radio item - which scatter plots to show (initially hidden)
        html.Div([
            html.Div([
                html.Label("Select which ticker's scatter plots to display:", style=text_styles['question'])
            ], style={'textAlign': 'center', 'width': '100%', 'marginBottom': '10px'}),
            
            # Checklist instead of radio buttons for multi-selection
            html.Div([
                dcc.Checklist(
                    id='ticker-scatter-checklist',
                    options=[],  # Will be populated dynamically
                    value=[],    # No default selections
                    style={
                        'backgroundColor': colors['background'],
                        'fontSize': '16px',
                        'lineHeight': '1.4',
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center'
                    },
                    labelStyle={'margin': '0px 15px 5px 0px', 'display': 'inline-block', 'white-space': 'nowrap'}
                )
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'center'}),
            
            # Button in its own centered div
            html.Div([
                html.Button('Display Selected Scatter Plots', 
                        id='display-scatter-button', 
                        style=text_styles['button'])
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'center', 'marginTop': '15px'})
        ], id='ticker-scatter-container', style={'display': 'none', 'marginBottom': '15px', 'width': '100%'}),
        
        # Container for the selected scatter plot
        html.Div(id='selected-scatter-container')
        
    ], id='scatter-controls', style={'display': 'none'}),
    
    #Adding the rolling beta for a given stock
    html.Div([
        html.Hr(),
        html.H3('Rolling CAPM Analysis', style=text_styles['subtitle']),

        #Radio buttons for the user to select whether to see the rolling capms or not
        html.Div([
            html.Label("Would you like to see the Rolling CAPM?", style=text_styles['question']),
            html.Div([
                dcc.RadioItems(
                    id='show-rolling-capm-radio',
                    options=[
                        {'label': 'Yes, show Rolling CAPM', 'value': 'yes'},
                        {'label': 'No, hide Rolling CAPM', 'value': 'no'}
                    ],
                    value='no', #Default value
                    style=text_styles['radio']
                ),
            ],style={'display': 'flex', 'justifyContent': 'center', 'width': '100%'}),
        ], style={'marginBottom': '15px', 'textAlign': 'center', 'width': '100%'}),

        #Checklist buttons for the user to select which stocks they want to see the rolling betas 
        # (in case they selected yes before)
        html.Div([
            html.Div([
                html.Label("Select which ticker's Rolling CAPM to display:\n (Notice this will produce rolling beta, alpha and R2, so selecting more than one might be confusing!)", style=text_styles['question'])
            ], style={'textAlign': 'center', 'width': '100%', 'marginBottom': '10px'}),
            
            #Checklist for multi-selection
            html.Div([
                dcc.Checklist(
                    id='rolling-capm-ticker-checklist',
                    options=[],  # Will be populated dynamically - meaning this information will be filed later on
                    value=[],    # No default selections
                    style={
                        'backgroundColor': colors['background'],
                        'fontSize': '16px',
                        'lineHeight': '1.4',
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center'
                    },
                    labelStyle={'margin': '0px 15px 5px 0px', 'display': 'inline-block', 'white-space': 'nowrap'}
                )
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'center'}),

            #Slider for the user to select the window size
            html.Div([
                html.Label("Select rolling window size (months):", style=text_styles['question']),
                dcc.Slider(
                    id='window-size-slider',
                    min=6,
                    max=36,
                    step=3,
                    value=12,
                    marks={i: f'{i}m' for i in range(6, 37, 6)},
                ),
            ], style={'marginBottom': '20px', 'width': '80%', 'margin': '0 auto'}),
        

            #Aligning button to the center
            html.Div([
                html.Button('Generate Rolling Analysis', 
                        id='generate-rolling-capm-button', 
                        style=text_styles['button'])
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'center', 'marginTop': '15px'})
        ], id='rolling-capm-controls-container', style={'display': 'none', 'marginBottom': '15px', 'width': '100%'}),

        #Loading indicator - show to user that rolling analyses are loading
        html.Div(html.Div(id='rolling-capm-loading', style={'textAlign': 'center', 'marginTop': '10px'})),
        
        #Container with all rolling betas info
        html.Div(id='rolling-capm-chart-container'),
        
        # Container for the selected scatter plot
        html.Div(id='selected-rolling-container'),

], id='rolling-capm-section', style={'display': 'none'}),
    
    # Output Container for tables and analytics
    html.Div(id='output-container', style={'color': colors['text'], 'marginTop': '20px'})
])

#Callback for the Run Analysis Button - this is what allows the webApp to be interactive
@app.callback(
    [Output('loading-message', 'children'),
     Output('output-container', 'children'), #Container of all the scatter plots and information
     Output('scatter-controls', 'style'), #Controls regarding the visualization of the scatter plots
     Output('ticker-scatter-checklist', 'options'),  # Changed from radio to checklist
     Output('ticker-scatter-checklist', 'value')], #If answer is yes, user will select the tickers he wanst to see
    #When the user clicks it will run
    [Input('run-analysis-button','n_clicks')],
    #State parameter allos me to access the current value of components within the ticker-dropdown
    #Dash will retrieve the current value of the component with id 'ticker-dropdown'
    [State('ticker-dropdown', 'value')],
    prevent_initial_call = True
)

#The two parameter of the function (n_clicks, selected_tickers), correspond IN ORDER to the inputs and states in the callback decorator
#So if I added another input or state in the callback and added a third argument here, it would correspond to that one
def update_output_analysis(n_clicks,selected_tickers):
    if n_clicks is None:
        raise PreventUpdate
    
    if not selected_tickers or len(selected_tickers) == 0:
        return(
            html.Div("No tickers selected!", style=text_styles['subtitle']),
            html.Div("Please select tickers using the dropdown above before running the analysis", style=text_styles['subtitle']),
            {'display': 'none'},
            [],
            []
        )
    
    #List with all the tickets inside the S&P 500
    capm_regression.set_ticker_list(ticker_options)
    
    #Fetching excess returns of sp500
    sp500_excess_returns_df = pd.DataFrame({'SP500 Excess Returns (%)':capm_regression.get_sp500_excess_returns_df()})
    
    #List that will contain all scatter plots for output
    all_scatter_plots = {}

    #Mean because returns on S&P500 are relatively stable over time (compared to other equity markets)
    sp500_monthly_returns = capm_regression.get_sp500_monthly_returns()
    sp500_monthly_returns = sp500_monthly_returns.dropna()
    sp500_expected_returns = sp500_monthly_returns.mean()

    risk_free_rate = capm_regression.get_monthly_tbill_yield()
    risk_free_rate = risk_free_rate.dropna()
    rf = risk_free_rate.mean()

    #DataFram that will contain all betas, alphas, R2 and Treynor Ratio of selected stocks
    stocks_info = pd.DataFrame(columns = ['Ticker','Beta','Monthly Expected Returns (%)', 'Alpha (%)','R2','Treynor Ratio (%)','Sharpe Ratio', 'Annual Alpha (%)'])
    
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

        #Rounding each information
        beta = round(beta,3)
        alpha_rounded = round(alpha,3)
        r_squared = round(r_squared,3)

        #Making Alpha annualized
        annual_alpha = alpha*12
        annual_alpha = round(annual_alpha,3)
        

        #CAPM formula is: E[rA] = rf + βA × (E[rm] - rf)
        #rf and E[rm] are the same for all assets, so calculated before for loop
        expected_returns = rf + beta*(sp500_expected_returns-rf)

        #Making Expected Returns in %
        expected_returns = expected_returns*100
        expected_returns = round(expected_returns,3)

        #Treynor Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Beta
        #Average excess return of each asset / Asset Beta
        mean_excess_returns = ticker_excess_returns_df.mean()
        treynor_ratio = mean_excess_returns/beta

        #Data is in monthly timeframe, so I need to make it annualized
        treynor_ratio = treynor_ratio*12
        treynor_ratio = round(treynor_ratio,3)

        #Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Standard deviation of portfolio's excess returns
        std_dev_excess_returns = ticker_excess_returns_df.std()
        #Data is in monthly timeframe, so I need to make it annualized
        #Multiplying by sqrt(12) because sharpe ratio uses std deviation (has to be sqrt of time)
        sharpe_ratio = (mean_excess_returns/std_dev_excess_returns)*(12**0.5)
        sharpe_ratio = round(sharpe_ratio,3)

        #Saving the Beta, Alpha, R2, Treynor and Sharpe Ratio of each ticker to the dataframe
        stocks_info.loc[each_ticker] = [each_ticker, beta, expected_returns, alpha_rounded, r_squared, treynor_ratio,sharpe_ratio, annual_alpha]
 
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
        text=f"{each_ticker} Expected Returns: {expected_returns}<br>Risk-Free Rate: {rf:.2%}<br>S&P500 Expected Returns: {sp500_expected_returns:.2%}",
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
            name=f"Best-Fitting Line: Beta(β)={beta:.3f}; Alpha(α)={alpha_rounded:.3f}; R²={r_squared:.3f}"
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
        all_scatter_plots[each_ticker] = scatter_fig


        #Adding each figure to the webapp
        html.Div([
            html.Div(f'Scatter Plot of Monthly Excess Returns for {each_ticker} versus the {index_name}',style=text_styles['subtitle']),
            scatter_plot
        ])
    
   
    #Creating DataTable with all the information inside the dataframe stocks_info apart from the annualized alpha
    stocks_table = go.Figure(data=[go.Table(
        header=dict(values=list(stocks_info.columns),
                    line_color=colors['line_color_table'],
                    fill_color=colors['fill_color_col_table'],
                    align='center',
                    height = 30),
        cells=dict(values=[stocks_info.index,stocks_info['Beta'],stocks_info['Monthly Expected Returns (%)'],stocks_info['Alpha (%)'],stocks_info['R2'],stocks_info['Treynor Ratio (%)'],stocks_info['Sharpe Ratio'],stocks_info['Annual Alpha (%)']],
                   fill_color=colors['fill_color_table'],
                   line_color=colors['line_color_table'],
                   align='center',
                   height = 30),
                   columnwidth=[0.3, 0.3, 0.3])
        ])
    
    table_height = 100 + (len(selected_tickers) * 30)

    stocks_table.update_layout(
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        width=750,  
        height=table_height,  # Keep height small too
        margin=dict(l=5, r=5, t=5, b=10),  # Minimal margins
        autosize=False
    )
    
    #Bar chart with all (Jensen's) Alphas for comparison
    alpha_fig = px.bar(stocks_info,
                       x = 'Ticker',
                       y = 'Annual Alpha (%)',
                       title= 'Jensen\'s Alpha for each Ticker',
                       labels= {'Annual Alpha (%)': 'Jensen\'s Alpha (%)'},
                       text = 'Annual Alpha (%)',
                       color='Annual Alpha (%)',
                       color_continuous_scale=[
                            (0.0, '#891f00'),   # Red for negative values
                            (0.5, "white"), # White for zero
                            (1.0, "#5bbe7d")  # Green for positive values
                        ],
                       color_continuous_midpoint=0)
    
    alpha_fig.add_shape(
                        type='line',
                        x0=0,
                        x1=len(stocks_info),
                        y0=0,
                        y1=0,
                        line=dict(color='black', width=1.5, dash='dash')
                    )
    
    alpha_fig.update_traces(texttemplate='%{text:.3f}%', textposition='outside')
    
    alpha_fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title_x=0.5,
        coloraxis_showscale=False,
    )

    alpha_bar_chart = dcc.Graph(figure=alpha_fig)

    #Creating bar chart with treynor ratios of selected stocks
    treynor_fig = px.bar(stocks_info,
                         x = 'Ticker',
                         y= 'Treynor Ratio (%)',
                         title= 'Treynor Ratio for each Ticker',
                        text = 'Treynor Ratio (%)',
                        color='Treynor Ratio (%)',
                        color_continuous_scale=[
                                (0.0, '#891f00'),   # Red for negative values
                                (0.5, "white"), # White for zero
                                (1.0, "#5bbe7d")  # Green for positive values
                            ],
                        color_continuous_midpoint=0)
    
    treynor_fig.add_shape(
                    type='line',
                    x0=0,
                    x1=len(stocks_info),
                    y0=0,
                    y1=0,
                    line=dict(color='black', width=1.5, dash='dash')
                )
    
    treynor_fig.update_traces(texttemplate='%{text:.3f}%', textposition='outside')

    treynor_fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title_x=0.5,
        coloraxis_showscale=False,
    )
    
    treynor_bar_chart = dcc.Graph(figure=treynor_fig)

    #Creating bar chart with sharpe ratios of selected stocks
    sharpe_fig = px.bar(stocks_info,
                         x = 'Ticker',
                         y= 'Sharpe Ratio',
                         title= 'Sharpe Ratio for each Ticker',
                        text = 'Sharpe Ratio',
                        color='Sharpe Ratio',
                        color_continuous_scale=[
                                (0.0, '#891f00'),   # Red for negative values
                                (0.5, "white"), # White for zero
                                (1.0, "#5bbe7d")  # Green for positive values
                            ],
                        color_continuous_midpoint=0)
    
    sharpe_fig.add_shape(
                    type='line',
                    x0=0,
                    x1=len(stocks_info),
                    y0=0,
                    y1=0,
                    line=dict(color='black', width=1.5, dash='dash')
                )
    
    sharpe_fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')

    sharpe_fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title_x=0.5,
        coloraxis_showscale=False,
    )
    
    sharpe_bar_chart = dcc.Graph(figure=sharpe_fig)

    #Saving the dictionary of scatter plots figures as an attribute of the Dash app instance
    # This needs to be serialized so we'll save scatter plot IDs instead
    app.scatter_plots_dict = all_scatter_plots
    print(f"Stored {len(all_scatter_plots)} scatter plots with keys: {list(all_scatter_plots.keys())}")



    # Create options for the ticker selection radio button
    ticker_checklist_options = [{'label': ticker, 'value': ticker} for ticker in selected_tickers]


    return [
        #Loading Message
        html.Div("Analysis completed!",style=text_styles['subtitle']),

        html.Div([
            dcc.Markdown('''**Beta and Alpha**
            CAPM's Beta and Alpha can be calculated using a linear regression model between the excess returns of a diversified market (S&P500) and a particular stock.
                The linear regression model will create what is called a "best-fitting" line (y = mx + b), that will map all the points in the 
                scatter plot and figure out what is the line that best corresponds to all points when observed together. The slope of this line is called Beta,
                which refers to the asset's sensitivity to movements in a given market (SP500). The y-intercept is the Alpha, referring to the excess return of the asset
                when the return of the market (SP500) is 0%. (Jensen's) Alpha suggests if the asset outperforms or underperforms the given market.
                The principal assumption of CAPM is that returns can be explained entirely by the asset's risk relationship with the market. If a stock follows CAPM 
                perfectly, then alpha should be 0 (only beta should affect the asset's change in price). When a stock has a non-zero alpha, this means that it is a 
                deviation from the expected performance using CAPM as a benchmark.''',
                style=text_styles['markdown']),

            html.Div("Dataset with all Betas, Alphas and R2 of selected tickers:", style=text_styles['subtitle']),
            html.Div([dcc.Graph(figure=stocks_table)],style={ #Output container (only data table part)
                'display': 'flex',
                'justifyContent': 'center',  
                'width': '100%',             
                'marginBottom': '20px'
            }), 
            
            dcc.Markdown('''**Jensen's Alpha** measures the risk-adjusted performance relative to what the CAPM would predict.
                         It evaluates if the portfolio (in this case a given stock) overperforms or underperforms a particular market (SP500)
                         relative to what CAPM predicted. If CAPM was 100%, this alpha would always be 0, which is almost never the case, meaning
                         that CAPM does not capture all factors regarding the asset's returns. **Negative Alpha** indicates the asset is underperforming 
                         the market and **Postive Alpha** indicates the asset is overperforming the market.
                         ''', style=text_styles['markdown']),
            
            html.Div("Annualized Jensen's Alpha:", style=text_styles['subtitle']),
            
            html.Div([alpha_bar_chart], style={
                'display': 'flex',
                'justifyContent': 'center',
                'width': '100%',
                'marginBottom': '20px'
            }),

            dcc.Markdown('''**Treynor Ratio:** A performance metric that measures the excess return per unit of systematic risk. 
                         It evaluates how much return an asset/portfolio generates for each unit of market risk (beta) it takes.
                         Treynor Ratio only considers systematic risk (risk that cannot be diversified away), hence using Beta for the 
                         calculation. Higher values suggest an asset has generated strong excess returns relative to its systematic 
                         risk (beta). Lower values indicate a lower risk-adjusted return, meaning the investment is generating less 
                         excess returns per unit of systematic risk (beta).
            ''', style=text_styles['markdown']),

            html.Div("Annualized Treynor Ratio:", style=text_styles['subtitle']),
            
            html.Div([treynor_bar_chart], style={
                'display': 'flex',
                'justifyContent': 'center',
                'width': '100%',
                'marginBottom': '20px'
            }),

            dcc.Markdown('''**Sharpe Ratio:** Similar to the Treynor Ratio, Sharpe Ratio also measures the return of an investment with its risk.
                         Instead of using the beta for calculating market risk (Treynor Ratio), the Sharpe Ratio uses uses total risk (standard deviation) in its 
                         calculation. Higher Sharpe ratios indicate more efficient investments that deliver better returns per unit of overall risk. Lower Sharpe
                         Ratios indicates investments that provide weak returns per unit of overall risk, meaning that for the amount of volatility investors 
                         have endured with this investment, they've received less compensation in excess returns.


            ''', style=text_styles['markdown']),

            html.Div("Annualized Sharpe Ratio:", style=text_styles['subtitle']),
            
            html.Div([sharpe_bar_chart], style={
                'display': 'flex',
                'justifyContent': 'center',
                'width': '100%',
                'marginBottom': '20px'
            }),

             #Storing the scatter plots data in a hidden div for later use
            html.Div(id='scatter-plots-store', style={'display': 'none'})
        ]),
        
        {'display': 'block'},
        
        ticker_checklist_options,
        
        []  # No default selections for the checklist
    ]

# Callback to show/hide the ticker selection based on the yes/no radio button
@app.callback(
    Output('ticker-scatter-container', 'style'),
    [Input('show-scatter-radio', 'value')],
    prevent_initial_call=True
)
def toggle_ticker_selection(show_scatter):
    if show_scatter == 'yes':
        return {'display': 'block', 'marginBottom': '15px','width': '100%'}
    else:
        return {'display': 'none'}

# Callback to display the selected scatter plot
@app.callback(
    Output('selected-scatter-container', 'children'),
    [Input('display-scatter-button', 'n_clicks')],
    [State('ticker-scatter-checklist', 'value'),
     State('show-scatter-radio', 'value')],
    prevent_initial_call=True
)

def display_selected_scatter_plots(n_clicks, selected_tickers, show_scatter):
    print(f"Display function called with: n_clicks={n_clicks}, selected_tickers={selected_tickers}, show_scatter={show_scatter}")
    
    if not n_clicks or show_scatter != 'yes' or not selected_tickers:
        print("Early return: conditions not met")
        return []

    scatter_plots = []
    print(f"Scatter plots dict exists: {'scatter_plots_dict' in dir(app)}")
    if hasattr(app, 'scatter_plots_dict'):
        print(f"Available tickers: {list(app.scatter_plots_dict.keys())}")
    
    # Loop through each selected ticker and add its scatter plot
    for ticker in selected_tickers:
        try:
            if not hasattr(app, 'scatter_plots_dict'):
                print(f"No scatter_plots_dict found on app object")
                scatter_plots.append(html.Div(f"Error: No scatter plots dictionary available", style=text_styles['subtitle']))
                continue
                
            scatter_fig = app.scatter_plots_dict.get(ticker)
            print(f"For ticker {ticker}, found figure: {scatter_fig is not None}")
            
            if scatter_fig is not None:
                scatter_plots.append(html.Div([
                    html.Hr(),
                    html.H3(f'Scatter Plot for {ticker}', style=text_styles['subtitle']),
                    dcc.Graph(figure=scatter_fig)
                ]))
            else:
                scatter_plots.append(html.Div(f"No scatter plot available for {ticker}", style=text_styles['subtitle']))
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            scatter_plots.append(html.Div(f"Error displaying scatter plot for {ticker}: {str(e)}", style=text_styles['subtitle']))
    
    print(f"Returning {len(scatter_plots)} scatter plot divs")
    return scatter_plots

#Callback to show/hide the rolling beta analyses based on yes/no radio button
@app.callback(
    Output('rolling-capm-controls-container','style'),
    [Input('show-rolling-capm-radio','value')],
    prevent_initial_call=True
)

#Function will get the input from the 'show-rolling-capm-radio', which indicates if the user
#wants to see the rolling analyses or not
def toggle_rolling_analysis(show_rolling_analysis):
    if show_rolling_analysis == 'yes':
        return {'display': 'block', 'marginBottom': '15px','width': '100%'}
    else:
        return {'display': 'none'}
    
#Callback to populate the ticker analysis list when first analysis run
@app.callback(
    [Output('rolling-capm-section','style'), #will fetch the rolling beta section
     Output('rolling-capm-ticker-checklist', 'options'), #will fetch the rolling beta checklist
     Output('rolling-capm-ticker-checklist', 'value')], 
    [Input('run-analysis-button','n_clicks')], #when the user clicks to run analysis, the function below will run
    [State('ticker-dropdown','value')], #the values to populate the selected tickers will be the ones selected by the user in the dropdown
     prevent_intial_call=True
)

def show_rolling_beta_section(n_clicks, selected_tickers):
    if n_clicks is None or not selected_tickers:
        return {'display': 'none'}, [], []
    
    # Create options for the ticker checklist
    ticker_options = [{'label': ticker, 'value': ticker} for ticker in selected_tickers]
    
    return {'display': 'block'}, ticker_options, []

@app.callback(
    [Output('rolling-capm-chart-container', 'children'), #result of the function below will be the container with all rolling betas
     Output('rolling-capm-loading', 'children')],#loading message also
    [Input('generate-rolling-capm-button', 'n_clicks')],#when the user clicks to run, it will run (input)
    [State('rolling-capm-ticker-checklist', 'value'),#values will depend on the checklist of the rolling beta checklist
     State('window-size-slider', 'value')],#window size slider for user to select the window
    prevent_initial_call=True
)

def generate_rolling_capm_charts(n_clicks,selected_tickers, window_size):
    print(f"Display function called with: n_clicks={n_clicks}, selected_tickers={selected_tickers}, window_size={window_size}")

    #Do not return anything if the user does not click on the run analysis or 
    #if the user clicks and there is nothing in the checklist
    if n_clicks is None or not selected_tickers:
        return [], ''
    
    #Showing loading message
    loading_message = f'Calculating rolling CAPM metrics for {len(selected_tickers)} tickers...'
    
    #Storing all charts
    rolling_capm_charts = []

    #For loop to generate each rolling beta figure

    for each_ticker in selected_tickers:
        try:
            rolling_analysis_df = capm_regression.calculate_rol_analysis_ols(ticker=each_ticker,window_size=window_size)
            #This df will have three columns (Beta, Alpha, R2), with the date as the index

            #creating the rolling beta graph
            rol_beta_fig = px.line(
                rolling_analysis_df,
                x=rolling_analysis_df.index,
                y='Beta',
                title=f'Rolling Beta for {each_ticker} (Window: {window_size} months)',
                labels={'Beta': 'Beta', 'date': 'Date'}
            )

            # Add a horizontal line at beta = 1 for reference
            rol_beta_fig.add_shape(
                type='line',
                x0=rolling_analysis_df.index.min(),
                x1=rolling_analysis_df.index.max(),
                y0=1,
                y1=1,
                line=dict(color='black', width=1.5, dash='dash')
            )

            #Update layout for aesthetic purposes
            rol_beta_fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'],
                title_x=0.5,
                height=400,
                xaxis_title="Date",
                yaxis_title="Beta Value",
            )

            #Adding Rolling Alpha Graph
            rol_alpha_fig = px.line(
                rolling_analysis_df,
                x=rolling_analysis_df.index,
                y='Alpha',
                title=f'Rolling Alpha for {each_ticker} (Window: {window_size} months)',
                labels={'Alpha': 'Alpha', 'date': 'Date'}
            )

            # Add a horizontal line at beta = 1 for reference
            rol_alpha_fig.add_shape(
                type='line',
                x0=rolling_analysis_df.index.min(),
                x1=rolling_analysis_df.index.max(),
                y0=1,
                y1=1,
                line=dict(color='black', width=1.5, dash='dash')
            )

            #Update layout for aesthetic purposes
            rol_alpha_fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'],
                title_x=0.5,
                height=400,
                xaxis_title="Date",
                yaxis_title="Alpha Value",
            )

            #Adding Rolling R2 Graph
            rol_r2_fig = px.line(
                rolling_analysis_df,
                x=rolling_analysis_df.index,
                y='R2',
                title=f'Rolling R2 for {each_ticker} (Window: {window_size} months)',
                labels={'R2': 'R2', 'date': 'Date'}
            )

            # Add a horizontal line at beta = 1 for reference
            rol_r2_fig.add_shape(
                type='line',
                x0=rolling_analysis_df.index.min(),
                x1=rolling_analysis_df.index.max(),
                y0=1,
                y1=1,
                line=dict(color='black', width=1.5, dash='dash')
            )

            #Update layout for aesthetic purposes
            rol_r2_fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'],
                title_x=0.5,
                height=400,
                xaxis_title="Date",
                yaxis_title="Alpha Value",
            )
            
            #Adding to Rolling Beta Charts
            rolling_capm_charts.append(html.Div([
                html.H4(f'Rolling CAPM Analysis for {each_ticker}', style=text_styles['subtitle']),
                html.Div([
                    dcc.Graph(figure=rol_beta_fig),
                    html.P([
                        html.Strong("Beta Interpretation: "), 
                        "Shows how the stock's sensitivity to market movements changes over time. - β > 1: More volatile than market; β < 1: Less volatile than market.",
                    ], style=text_styles['markdown'])
                ]),
                html.Div([
                    dcc.Graph(figure=rol_alpha_fig),
                    html.P([
                        html.Strong("Alpha Interpretation: "), 
                        "Shows how the stock's risk-adjusted performance relative to CAPM changes over time. α > 0: Outperforming the market; α < 0: Underperforming the market.",
                    ], style=text_styles['markdown'])
                ]),
                html.Div([
                    dcc.Graph(figure=rol_r2_fig),
                    html.P([
                        html.Strong("R-squared Interpretation:"), 
                        "Shows how well CAPM explains the stock's returns over time. Higher values indicate market movements (volatility) explain more of the stock's behavior.",
                    ], style=text_styles['markdown'])
                ]),
            ])
            )


        except Exception as e:
            rolling_capm_charts.append(html.Div([
                html.H4(f'Rolling CAPM Analysis for {each_ticker}', style=text_styles['subtitle']),
                html.P(f"Error calculating rolling beta: {str(e)}", style=text_styles['subtitle'])
            ]))

    return rolling_capm_charts, ''
    
if __name__ == '__main__':
    app.run_server(debug=True)