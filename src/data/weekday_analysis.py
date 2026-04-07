import yfinance as yf
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime

def fetch_open_prices_with_dates(ticker_symbol: str, period: str = "300d") -> pd.DataFrame:
    """
    指定されたティッカーの任意の日数分の始値データと日付を DataFrame で取得します。
    デフォルトは300日分です。
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        
        if df.empty or 'Open' not in df.columns:
            print(f"Warning: No data found for {ticker_symbol}.")
            return pd.DataFrame()
        
        # 日付と始値をDataFrameとして返す
        result_df = pd.DataFrame({
            'Date': df.index,
            'Open': df['Open']
        })
        result_df['Date'] = pd.to_datetime(result_df['Date'])
        return result_df
        
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

def group_by_weekday(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    DataFrameを曜日ごとにグループ化します。
    戻り値: {'月曜日': df1, '火曜日': df2, ...}
    """
    if df.empty:
        return {}
    
    # 曜日を日本語で取得
    weekday_map = {
        0: '月曜日',
        1: '火曜日', 
        2: '水曜日',
        3: '木曜日',
        4: '金曜日',
        5: '土曜日',
        6: '日曜日'
    }
    
    df['Weekday'] = df['Date'].dt.weekday.map(weekday_map)
    
    # 曜日ごとにグループ化（土日も含むが、クエリは平日なのでそのまま）
    grouped = {}
    for weekday in weekday_map.values():
        grouped[weekday] = df[df['Weekday'] == weekday].copy()
    
    return grouped

def calculate_weekday_stats(grouped_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
    """
    曜日ごとの統計量を算出します。
    戻り値: {'月曜日': {'count': n, 'mean': m, 'std': s, 'min': min, 'max': max}, ...}
    """
    stats = {}
    for weekday, df in grouped_data.items():
        if not df.empty:
            prices = df['Open']
            stats[weekday] = {
                'count': len(prices),
                'mean': prices.mean(),
                'std': prices.std(),
                'min': prices.min(),
                'max': prices.max()
            }
        else:
            stats[weekday] = {
                'count': 0,
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0
            }
    return stats

if __name__ == "__main__":
    # 動作確認用
    symbol = "SOL-JPY"
    
    # 1. データ取得
    df = fetch_open_prices_with_dates(symbol)
    if df.empty:
        print("Failed to fetch data.")
        exit()
    
    print(f"Retrieved {len(df)} records for {symbol}")
    print(df.head())
    
    # 2. 曜日ごとにグループ化
    grouped = group_by_weekday(df)
    
    # 3. 統計量算出
    stats = calculate_weekday_stats(grouped)
    
    # 結果表示
    print("\n=== 曜日ごとのデータセット ===")
    for weekday, data in grouped.items():
        print(f"{weekday}: {len(data)} records")
        if not data.empty:
            print(f"  Sample: {data.head(3)}")
    
    print("\n=== 曜日ごとの統計量 ===")
    for weekday, stat in stats.items():
        print(f"{weekday}: 件数={stat['count']}, 平均={stat['mean']:.2f}, 標準偏差={stat['std']:.2f}, 最小={stat['min']:.2f}, 最大={stat['max']:.2f}")