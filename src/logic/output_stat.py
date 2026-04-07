import pandas as pd
from typing import Dict, Any
import yfinance as yf
import os
import sys

# パス追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 内部モジュールのインポート
from src.data.weekday_analysis import fetch_open_prices_with_dates, group_by_weekday, group_by_rokuyou, calculate_weekday_stats
from src.logic.statistical_tests import perform_statistical_tests, choose_test_strategy, decide_and_print_tests

def get_indicator_descriptions() -> Dict[str, str]:
    """
    フロントエンド等で利用可能な統計指標の解説辞書を返却します。
    """
    return {
        "weekday_stats": "曜日ごとの統計量（件数、平均、標準偏差、最小、最大）。",
        "parametric_tests": "パラメトリック検定結果（正規性、等分散、ANOVA、Tukey-Kramer）。",
        "nonparametric_tests": "ノンパラメトリック検定結果（Kruskal-Wallis、Steel-Dwass）。",
        "normality_tests": "各曜日の正規性テスト（Shapiro-Wilk）。",
        "homoscedasticity_test": "等分散テスト（Levene）。",
        "anova": "曜日間の平均値差の検定。",
        "kruskal_wallis": "曜日間の中央値差の検定。",
        "posthoc_tukey": "ANOVA有意時の多重比較（Tukey-Kramer）。",
        "posthoc_steel_dwass": "Kruskal-Wallis有意時の多重比較（Steel-Dwass）。"
    }

def get_full_stat_report(df: pd.DataFrame, symbol: str = "UNKNOWN", mode: str = "weekday") -> Dict[str, Any]:
    """
    1. グループ化
    2. 統計量算出
    3. 統計検定
    の3階層を統合したレポートを生成します。
    """
    mode = mode.lower()
    if mode == "rokuyou":
        grouped_data = group_by_rokuyou(df)
    else:
        grouped_data = group_by_weekday(df)
    
    # 2. 統計量算出
    stats = calculate_weekday_stats(grouped_data)
    
    # 3. 統計検定
    test_results = perform_statistical_tests(grouped_data)
    test_results['decision'] = choose_test_strategy(test_results)
    
    # 階層型レポートの構築
    return {
        "level_1_grouping": grouped_data,
        "level_2_stats": stats,
        "level_3_tests": test_results,
        "descriptions": get_indicator_descriptions(),
        "metadata": {
            "symbol": symbol,
            "total_records": len(df),
            "period": "1y",  # デフォルト
            "analysis_mode": mode
        }
    }

def get_report_by_ticker_stat(ticker: str, period: str = "300d", mode: str = "weekday") -> Dict[str, Any]:
    """
    ティッカーシンボルを指定して、データの取得から統計レポートの生成までを一括で行います。
    skin.py等のフロントエンドから利用可能な共通インターフェースです。
    """
    df = fetch_open_prices_with_dates(ticker, period)
    if df.empty:
        return {}
    return get_full_stat_report(df, symbol=ticker, mode=mode)

def print_stat_report(result: Dict[str, Any]):
    """
    統計結果を人間が読みやすい形式（階層構造を意識）で出力します。
    """
    metadata = result["metadata"]
    stats = result["level_2_stats"]
    tests = result["level_3_tests"]
    mode = metadata.get("analysis_mode", "weekday")
    mode_label = "六曜" if mode == "rokuyou" else "曜日"
    
    print("="*60)
    print(f" {metadata['symbol']} {mode_label}統計レポート")
    print("="*60)
    
    print(f"\n[1] 全体情報:")
    print(f"    - 総レコード数: {metadata['total_records']}")
    print(f"    - 期間: {metadata['period']}")
    
    print(f"\n[2] {mode_label}別統計量:")
    for group_name, stat in stats.items():
        print(f"    - {group_name}: 件数={stat['count']}, 平均={stat['mean']:.2f}, 標準偏差={stat['std']:.2f}")
    
    if "error" in tests:
        print(f"    エラー: {tests['error']}")
    else:
        decide_and_print_tests(tests)
    
    print("\n" + "="*60)

# skin.py に引き渡すためのインターフェース関数
def get_stat_data_for_skin(ticker: str, period: str = "300d", mode: str = "weekday") -> Dict[str, Any]:
    """
    skin.py が利用しやすい形式で統計データを返却します。
    """
    report = get_report_by_ticker_stat(ticker, period, mode)
    if not report:
        return {"error": "データ取得または分析に失敗しました。"}
    
    # skin.py 用に整形
    mode = report["metadata"].get("analysis_mode", "weekday")
    
    # 曜日モードの場合は平日だけを表示
    if mode == "weekday":
        weekday_order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
        group_order = [g for g in report["level_1_grouping"].keys() if g in weekday_order]
        grouped_data = {k: v.to_dict('records') for k, v in report["level_1_grouping"].items() if not v.empty and k in weekday_order}
        weekday_stats = {k: v for k, v in report["level_2_stats"].items() if k in weekday_order}
    else:
        group_order = list(report["level_1_grouping"].keys())
        grouped_data = {k: v.to_dict('records') for k, v in report["level_1_grouping"].items() if not v.empty}
        weekday_stats = report["level_2_stats"]
    
    return {
        "symbol": report["metadata"]["symbol"],
        "total_records": report["metadata"]["total_records"],
        "analysis_mode": mode,
        "weekday_stats": weekday_stats,
        "test_results": report["level_3_tests"],
        "group_order": group_order,
        "grouped_data": grouped_data,
        "descriptions": report["descriptions"]
    }

if __name__ == "__main__":
    # SOL-JPY の実データで実行
    ticker = "SOL-JPY"
    print(f"{ticker} の曜日別統計データを取得中...")
    full_report = get_report_by_ticker_stat(ticker, "300d")
    
    if full_report:
        # 統計レポートの詳細表示
        print_stat_report(full_report)
        
        # skin.py 引き渡し用データのサンプル
        skin_data = get_stat_data_for_skin(ticker)
        print(f"\nskin.py 引き渡し用データキー: {list(skin_data.keys())}")
    else:
        print("統計レポートの生成に失敗しました。")