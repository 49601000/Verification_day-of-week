06_価格バックテスト Streamlit版

構成:
- main.py                # Streamlit 入口
- requirements.txt
- .streamlit/config.toml # Streamlit 設定
- config/                # 将来の設定ファイル用フォルダ
- src/
  - data/               # データ取得・前処理
  - logic/              # 統計処理・レポート生成
  - ui/                 # Streamlit UI 実装

起動:
    streamlit run main.py
