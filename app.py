# app.py

from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import plotly.graph_objs as go
import json

# Override Yahoo Finance
yf.pdr_override()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get stock ticker symbol from the form
        stock = request.form["stock"]
    else:
        # Default stock ticker symbol
        stock = "MSFT"

    # Retrieve stock data frame (df) from yfinance API at an interval of 1m
    df = yf.download(tickers=stock, period="1d", interval="1m")

    # Declare plotly figure (go)
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="market data",
        )
    )

    fig.update_layout(
        title=str(stock) + " Live Share Price:",
        yaxis_title="Stock Price (USD per Shares)",
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )

    # Save the plot to an HTML file
    plot_html = fig.to_html(full_html=False)

    # CashFlow:
    ticker = yf.Ticker(stock)

    df = ticker.cashflow
    df[df.columns[0]] = df[df.columns[0]] / 1000000
    df[df.columns[1]] = df[df.columns[1]] / 1000000
    df[df.columns[2]] = df[df.columns[2]] / 1000000
    df[df.columns[3]] = df[df.columns[3]] / 1000000
    cash_flow = df.to_html()

    # Stock News

    news_list = ticker.news

    # stock holdings

    stock_holding = ticker.institutional_holders

    stock_holding[stock_holding.columns[4]] = round(
        stock_holding[stock_holding.columns[4]] % 10000
    ).apply(lambda x: str(x) + "M")

    stock_holding[stock_holding.columns[1]] = round(
        stock_holding[stock_holding.columns[1]] % 1000
    ).apply(lambda x: str(x) + "M")

    stock_holding_html = stock_holding.to_html()

    return render_template(
        "index.html",
        plot_html=plot_html,
        stock=stock,
        cash_flow=cash_flow,
        news_list=news_list,
        stock_holding_html=stock_holding_html,
        # balance_sheet_html=balance_sheet_html,
    )


if __name__ == "__main__":
    app.run(debug=True)
