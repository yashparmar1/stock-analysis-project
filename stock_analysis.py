import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to fetch daily stock data from Alpha Vantage API
def fetch_stock_data(stock_symbol, api_key):
    # API endpoint URL
    base_url = 'https://www.alphavantage.co/query'
    
    # Parameters for the API request
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': stock_symbol,
        'apikey': api_key
    }
    
    # Make the request to the API
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Parse the JSON response to get the time series data
        time_series = data['Time Series (Daily)']
        
        # Convert the time series data into a pandas DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']  # Rename columns
        
        # Convert columns to numeric values
        df = df.apply(pd.to_numeric)
        
        # Sort the data by date
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        return df
    else:
        print(f"Error: Unable to fetch data for {stock_symbol}")
        return None

# Function to calculate correlation between two stocks
def calculate_correlation(stock1_data, stock2_data):
    # Calculate daily percentage returns for both stocks
    stock1_returns = stock1_data['Close'].pct_change().dropna()
    stock2_returns = stock2_data['Close'].pct_change().dropna()
    
    # Calculate the Pearson correlation coefficient
    correlation = stock1_returns.corr(stock2_returns)
    return correlation

# Function to identify price ratio divergence
def identify_divergence(stock1_data, stock2_data):
    # Calculate the price ratio (stock1 / stock2)
    price_ratio = stock1_data['Close'] / stock2_data['Close']
    
    # Calculate average and standard deviation of the price ratio
    avg_ratio = price_ratio.mean()
    std_dev = price_ratio.std()

    # Define a threshold for divergence (e.g., 2 standard deviations)
    threshold = 2 * std_dev

    # Identify points where the price ratio diverges beyond the threshold
    divergence_points = price_ratio[(price_ratio > avg_ratio + threshold) | (price_ratio < avg_ratio - threshold)]
    
    return price_ratio, divergence_points, avg_ratio, threshold

# Your Alpha Vantage API key
api_key = '8XTYVGI0OHVDSTO1'

# Fetch stock data for Apple (AAPL) and Microsoft (MSFT)
stock1_symbol = 'AAPL'
stock2_symbol = 'MSFT'

stock1_data = fetch_stock_data(stock1_symbol, api_key)
stock2_data = fetch_stock_data(stock2_symbol, api_key)

# Check if both stocks' data was fetched successfully
if stock1_data is not None and stock2_data is not None:
    # Save the stock data to CSV files
    stock1_data.to_csv(f'{stock1_symbol}_daily_data.csv', index=True)
    stock2_data.to_csv(f'{stock2_symbol}_daily_data.csv', index=True)
    print(f"Data saved for {stock1_symbol} and {stock2_symbol}")
    
    # Calculate correlation between the two stocks
    correlation = calculate_correlation(stock1_data, stock2_data)
    print(f"Correlation between {stock1_symbol} and {stock2_symbol}: {correlation}")
    
    # Identify divergence in price ratio
    price_ratio, divergence_points, avg_ratio, threshold = identify_divergence(stock1_data, stock2_data)
    
    # Print divergence points
    print("Divergence points:")
    print(divergence_points)
    
    # Plot the closing prices of both stocks
    plt.figure(figsize=(14, 7))
    
    plt.subplot(2, 1, 1)
    plt.plot(stock1_data.index, stock1_data['Close'], label=f'{stock1_symbol} Closing Price', color='blue')
    plt.plot(stock2_data.index, stock2_data['Close'], label=f'{stock2_symbol} Closing Price', color='orange')
    plt.title(f'Closing Prices of {stock1_symbol} and {stock2_symbol}')
    plt.legend()
    
    # Plot the price ratio and highlight divergence
    plt.subplot(2, 1, 2)
    plt.plot(price_ratio, label='Price Ratio (AAPL / MSFT)', color='green')
    plt.axhline(y=avg_ratio, color='red', linestyle='--', label='Mean Ratio')
    plt.axhline(y=avg_ratio + threshold, color='red', linestyle='--', label='+2 Std Dev')
    plt.axhline(y=avg_ratio - threshold, color='red', linestyle='--', label='-2 Std Dev')
    plt.scatter(divergence_points.index, divergence_points, color='red', label='Divergence')
    plt.title('Price Ratio and Divergence')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

else:
    print("Unable to fetch data for both stocks.")
