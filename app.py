import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# List of stock tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'SPY']
stock_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'SPY']
benchmark_tickers = ['SPY']


def fetch_returns(ticker, from_date, to_date):
    try:
        response = requests.get(f'http://localhost:5000/get-return/{ticker}?from_date={from_date}&to_date={to_date}')
        if response.status_code == 400:
            st.error("Please check the date range and try again. The date range should be less than 10 years.")
            return None
        else:
            return response.json()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
def fetch_alpha(stock_ticker, benchmark_ticker, from_date, to_date):
    try:
        response = requests.get(f'http://localhost:5000/get-alpha/{stock_ticker}/{benchmark_ticker}?from_date={from_date}&to_date={to_date}')
        return response.json()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def returnApp():
    st.title("Stock Returns Calculator")

    # Default dates
    today = datetime.now()
    default_from_date = today - timedelta(days=365)  # Default to one year ago
    default_to_date = today

    # Input fields
    ticker = st.selectbox("Select Stock Ticker (e.g., AAPL):", tickers , key="stock_ticker_selectbox_1")
    from_date = st.date_input("From Date:", default_from_date, key = "from_date_1")
    to_date = st.date_input("To Date:", default_to_date, key = "to_date_1")

    if st.button("Calculate Returns"):
        if not ticker:
            st.warning("Please enter a valid stock ticker.")
        else:
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            returns = fetch_returns(ticker, from_date_str, to_date_str)
            
            if returns:
                st.success(f"Returns for {ticker} from {from_date_str} to {to_date_str}: ")
                df = pd.DataFrame(returns)
                st.write(df)

                # Plot the price data 
                st.line_chart(data = df, y = "price", x = "date")
    
def alphaApp():
    st.title("Stock Alpha Calculator")

    # Default dates
    today = datetime.now()
    default_from_date = today - timedelta(days=365)  # Default to one year ago
    default_to_date = today

    # Input fields
    stock_ticker = st.selectbox("Select Stock Ticker (e.g., AAPL):", stock_tickers, key="stock_ticker_selectbox_2")
    benchmark_ticker = st.selectbox("Select Benchmark Ticker (e.g., SPY):", benchmark_tickers)
    from_date = st.date_input("From Date:", default_from_date, key = "from_date_2")
    to_date = st.date_input("To Date:", default_to_date, key = "to_date_2")

    if st.button("Calculate Alpha"):
        if not stock_ticker or not benchmark_ticker:
            st.warning("Please enter a valid stock ticker.")
        else:
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            response_data = fetch_alpha(stock_ticker, benchmark_ticker, from_date_str, to_date_str)
            
            if response_data:
                st.success(f"Statistics for {stock_ticker} from {from_date_str} to {to_date_str}: ")
                summary_data = {
                    "Alpha geometric (annualized)": [f"{response_data['alpha_geom_annualized']:.2%}"],
                    "Alpha geometric (daily)": [f"{response_data['alpha_geom_daily']:.5f}"],
                    "Alpha regression (annualized)": [f"{response_data['alpha_regression_annualized']:.2%}"],
                    "Alpha regression (daily)": [f"{response_data['alpha_regression_daily']:.5f}"],
                    "Beta": [f"{response_data['beta']:.2f}"],
                    "R-Squared": [f"{response_data['r_squared']:.2f}"],
                    "Alpha p-value": [f"{response_data['alpha_pvalue']:.5f}"],
                    "Beta p-value": [f"{response_data['beta_pvalue']:.5f}"],
                    f"{stock_ticker} average annualized return": [f"{response_data['ticker_annualized_return']:.2%}"],
                    f"{benchmark_ticker} average annualized return": [f"{response_data['benchmark_annualized_return']:.2%}"],
                    f"{stock_ticker} annualized volatility": [f"{response_data['ticker_annualized_volatility']:.2%}"],
                    f"{benchmark_ticker} annualized volatility": [f"{response_data['benchmark_annualized_volatility']:.2%}"],
                    f"{stock_ticker} Sharpe Ratio": [f"{response_data['ticker_sharpe_ratio']:.2f}"],
                    f"{benchmark_ticker} Sharpe Ratio": [f"{response_data['benchmark_sharpe_ratio']:.2f}"]
                }

                summary_df = pd.DataFrame(summary_data)
                summary_df = summary_df.T

                st.table(summary_df)

                st.subheader("Data")
                st.write( pd.DataFrame(response_data["data"]))

                # Plot the indexed price data
                st.subheader("Indexed Prices: Stock vs Benchmark")
                st.line_chart(data = pd.DataFrame(response_data["data"]), y = ["ticker_indexed_price", "benchmark_indexed_price"], x = "date")

                # Plot the Risk free rate
                st.subheader("Risk Free Rate")
                st.line_chart(data = pd.DataFrame(response_data["data"]), y = "risk_free_rate_annualized", x = "date")

                # Plot histogram of daily returns to show volaility / distribution
                st.subheader("Daily Return Distribution: Stock vs Benchmark")
                plt.figure(figsize=(8, 6))
                sns.histplot(data=pd.DataFrame(response_data["data"]), x="ticker_return_daily", bins=50, kde=True, color="blue", label="Stock")
                sns.histplot(data=pd.DataFrame(response_data["data"]), x="benchmark_return_daily", bins=50, kde=True, color="red", label="Benchmark")
                plt.legend()
                plt.xlabel('Daily Return')
                st.pyplot(plt.gcf())


                # Plot the returns of the stock and benchmark
                st.subheader("Excess Returns: Stock vs Benchmark")
                # Create DataFrame
                df = pd.DataFrame(response_data["data"])

                # Create a scatter plot with a regression line
                plt.figure(figsize=(8, 6))
                sns.regplot(x=df["benchmark_return_excess_daily"], y=df["ticker_return_excess_daily"])

                # Add title and labels
                plt.title('Scatter plot with regression line')
                plt.xlabel('Benchmark Return Excess (Daily)')
                plt.ylabel('Ticker Return Excess (Daily)')
                # Draw x and y axis through the origin
                plt.axhline(0, color='black',linewidth=0.5)
                plt.axvline(0, color='black',linewidth=0.5)

                # Display the plot in Streamlit
                st.pyplot(plt.gcf())

if __name__ == '__main__':
    returnApp()
    alphaApp()