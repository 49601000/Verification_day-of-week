import yfinance as yf
import pandas as pd
from typing import List

def fetch_open_prices(ticker_symbol: str, period: str = "300d") -> List[float]:
    """
    指定されたティッカーの任意の日数分の始値データを yfinance から取得します。
    デフォルトは300日分です。
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        
        if df.empty or 'Open' not in df.columns:
            print(f"Warning: No data found for {ticker_symbol}.")
            return []
        
        # 始値を抽出し、昇順でリスト化
        open_prices: List[float] = df.sort_index(ascending=True)['Open'].tolist()
        return open_prices
        
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return []

if __name__ == "__main__":
    # 動作確認用
    symbol = "SOL-JPY"
    prices = fetch_open_prices(symbol)
    print(f"Retrieved {len(prices)} open prices for {symbol}")
    if prices:
        print(f"First 5 prices: {prices[:5]}")
        print(f"Last 5 prices: {prices[-5:]}")