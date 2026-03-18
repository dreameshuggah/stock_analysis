            
# STOCK FINANCIAL ANALYSIS DASHBOARD - README

Project Link: https://stock-financial-analysis-dashboard.streamlit.app/




### 1. OVERVIEW
-----------
The Stock Financial Analysis Dashboard is an interactive web application 
built with Streamlit and Python. It provides investors and analysts with 
a centralized platform to retrieve real-time stock data, visualize 
historical price trends, and perform fundamental and technical analysis 
on publicly traded companies.

The app leverages the 'yfinance' API to fetch data directly from Yahoo 
Finance, ensuring up-to-date market information.

## 2. KEY FEATURES
---------------
* Real-time Data Retrieval: Enter any valid ticker symbol (e.g., AAPL, 
  TSLA, MSFT) to pull instant market data.
* Interactive Charts: High-quality visualizations of price movements 
  using Plotly, including Candlestick and Line charts.
* Technical Indicators: Built-in support for common indicators such as 
  Moving Averages (SMA/EMA), RSI, and Bollinger Bands.
* Financial Statements: Easy access to Balance Sheets, Income 
  Statements, and Cash Flow summaries.
* Key Metrics: Quick view of P/E Ratio, Market Cap, 52-Week High/Low, 
  and Dividend Yield.
* Export Functionality: Option to download historical data as CSV files 
  for offline analysis.

## 3. TECH STACK
-------------
* Language: Python 3.x
* Framework: Streamlit
* Data Source: yfinance (Yahoo Finance API)
* Libraries: 
    - Pandas (Data manipulation)
    - Plotly / Matplotlib (Visualization)
    - NumPy (Numerical calculations)

## 4. INSTALLATION (LOCAL SETUP)
-----------------------------
If you wish to run the dashboard locally, follow these steps:

1. Clone the repository:
   $ git clone [repository-url]
   $ cd stock-financial-analysis-dashboard

2. Install dependencies:
   $ pip install -r requirements.txt

3. Launch the app:
   $ streamlit run app.py

## 5. HOW TO USE
-------------
1. Enter a Stock Ticker.
2. Date Range: Select price period 1y,2y,5y,max for the historical data 
   you wish to analyze.
3. Analysis include: Current price, Price Performance, Key Metrics
   Technical Analysis & Fundamental Performance.
4. Interactions: Hover over charts to see specific price points or 
   toggle indicators on/off.

## 6. LIMITATIONS & DISCLAIMER
---------------------------
* Data Lag: While data is "real-time," there may be a slight delay 
  (10-15 minutes) depending on the exchange and API limitations.
* Non-Financial Advice: This tool is for educational and informational 
  purposes only. It does not constitute financial advice. Always 
  consult with a professional before making investment decisions.

## 7. ACKNOWLEDGMENTS
------------------
* Data provided by Yahoo Finance via the yfinance library.
* Dashboard UI powered by the Streamlit framework.




