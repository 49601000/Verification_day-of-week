# Python Files Summary for 06_価格バックテスト

## Overview
このプロジェクトは、価格バックテストツールで、金融データの分析に焦点を当てています。特に、株価の曜日別統計と統計検定、ならびに六曜モードによる集計分析を行います。Streamlitを使用したUIで、サイバーパンク風のデザインです。

## Main Entry Point
- **main.py**: `src.ui.cyb_main` から `run()` をインポートして実行するシンプルなエントリーポイント。

## Modules

### src/ui/cyb_main.py
Streamlitを使用したメインUIモジュール。サイバーパンクテーマのスタイル設定。
- インポート: streamlit, pandas, numpy, altair, typing, sys
- 関数: `_setup_style()` (スタイル設定), `run()` (メイン実行関数)
- UI連携: `output_stat.py` から渡される `test_results` を使用して
  - 正規性テスト結果
  - 等分散テスト結果
  - 推奨検定方式（ANOVA または Kruskal-Wallis）
  を表示する。
- 特徴: カスタムCSSでダークテーマ、サイバーパンク風の色使い。
- 追加: サイドバーに「曜日モード / 六曜モード」切り替えを実装。

### src/logic/output_stat.py
統計データの集約とレポート生成を担当。
- 関数:
  - `get_indicator_descriptions()`: 統計指標の説明辞書を返却。
  - `get_full_stat_report()`: データ取得、グループ化、統計量算出、検定を統合したレポート生成。`perform_statistical_tests()` の結果に基づく判定ロジックを `decision` として追加。
  - `get_report_by_ticker_stat()`: ティッカー指定でレポート生成。
  - `print_stat_report()`: レポートを人間可読形式で出力。
- 統合: データフェッチ、曜日グループ化、統計計算、検定判定の3階層。

### src/logic/statistical_tests.py
グループ化されたデータに対して統計検定を実行。
- 関数:
  - `perform_statistical_tests()`: パラメトリック/ノンパラメトリック検定を計算し、結果を返す純粋関数。
  - `choose_test_strategy()`: 正規性/等分散判定に基づき、推奨する検定方式（ANOVA か Kruskal-Wallis）を決定して返す。
  - `print_test_results()`: 検定結果を表示。
- 検定内容:
  - パラメトリック: 正規性テスト (Shapiro-Wilk), 等分散テスト (Levene), ANOVA, Tukey-Kramer POST-HOC。
  - ノンパラメトリック: Kruskal-Wallis, Steel-Dwass POST-HOC。

### src/data/fetch_open_prices.py
yfinanceから始値データを取得。
- 関数: `fetch_open_prices()`: 指定ティッカーの始値リストを返却。
- 特徴: 期間指定可能、デフォルト2年(2y)に対応。

### src/data/weekday_analysis.py
データを曜日別/六曜別に分析。
- 関数:
  - `fetch_open_prices_with_dates()`: 日付付きDataFrame取得。
  - `group_by_weekday()`: 曜日ごとにグループ化 (日本語曜日名)。
  - `group_by_rokuyou()`: 六曜ごとにグループ化。
  - `calculate_weekday_stats()`: グループ別統計量算出 (件数、平均、標準偏差、最小、最大)。
- 特徴: 曜日モードと六曜モードの両方に対応。

## Dependencies
- streamlit, pandas, numpy, altair, yfinance, scipy, statsmodels, scikit-posthocs
- 外部ツール: QVTツールのモジュール (data_fetch)

## Usage
`main.py` を実行すると、Streamlitアプリが起動し、ティッカー指定で曜日別価格分析が可能。