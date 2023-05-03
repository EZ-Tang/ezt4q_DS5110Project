import dash
import yfinance as yf
import pandas as pd
import numpy as np
from dash import dcc, html, ctx
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash import dash_table
import RedditAPI
import ChatGPTSentiment



app = dash.Dash(__name__)
global yfinanceTicker
global ticker
global stockName
global df

df = pd.DataFrame(columns = ["Name", "Sentiment", "Feedback", "Tokens"])

ticker = ""

app.layout = html.Div([
    html.H1('ChatGPT + Reddit Sentiment Analysis For Stocks'),
    html.Div([
    html.Label('Stock Symbol:'),
    dcc.Input(
        style={"margin-left": "15px"},
        id='symbol',
        type='text',
        value=''
    ),
    ]),

    html.Div([
    html.Label('Stock Name:'),
    dcc.Input(
        style={"margin-left": "26px"},
        id='name',
        type='text',
        value=''
    ),
    ]),

    html.Div([
    html.Label('Subreddit:'),
    dcc.Input(
        style={"margin-left": "42px"},
        id='subreddit',
        type='text',
        value=''
    ),
    html.Button('Submit', id='btn-nclicks-1', n_clicks=0, style={"margin-left": "10px"}),
    ]),
    html.Div(children=[
    html.Div([dcc.Graph(id='graph')], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    style_data={
    'whiteSpace': 'normal',
    'height': 'auto',
    },
    data=df.to_dict('records'))], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])
])

"""
Displays the price graph of stock
"""
@app.callback(
    Output('graph', 'figure'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('symbol', 'value'),
)
def update_graph(submitBtn, sym):
    global ticker
    global stockName
    global yfinanceTicker
    if "btn-nclicks-1" == ctx.triggered_id:
        try:
            ticker = sym
            yfinanceTicker = yf.Ticker(sym)
            stockName = yfinanceTicker.info['shortName']
            print(stockName)
            df = yf.download(sym, period='1y')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
            fig.update_layout(title=stockName, xaxis_title='Date', yaxis_title='Price ($)')
            return fig
        except Exception as e:
            return {'data': [], 'layout': {'title': str(e)}}
    else:
        if (ticker == ""):
            return go.Figure()
        try:
            df = yf.download(ticker, period='1y')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
            fig.update_layout(title=stockName, xaxis_title='Date', yaxis_title='Price ($)')
            return fig
        except Exception as e:
            return {'data': [], 'layout': {'title': str(e)}}



@app.callback(
    Output('table', 'data'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('symbol', 'value'),
    Input('name', 'value'),
    Input('subreddit', 'value')
)
def update_table(submitBtn, sym, name, sub):
    global ticker
    global stockName
    global yfinanceTicker
    global df
    name = name.lower()
    
    if "btn-nclicks-1" == ctx.triggered_id:
        text = RedditAPI.analyze(name, sub)
        sentimentDf = ChatGPTSentiment.make_sentiment_df([name],[text])
        if df.empty:
            df = sentimentDf
        else:
            df = pd.concat([df, sentimentDf], axis=0)
        return df.to_dict('records')
    else:
        return df.to_dict('records')

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
    