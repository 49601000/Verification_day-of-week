import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from typing import Dict, Any
import sys

# QVTツールのモジュールをインポート
sys.path.append(r"c:\Users\info\MyAntigravity\02_hobby\01_QVTツール\app")
from modules.data_fetch import convert_ticker

# 内部モジュールのインポート
from src.logic.output_stat import get_stat_data_for_skin

# ─── グローバルスタイル ──────────────────────────────────────────

def _setup_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

    :root {
        --bg:       #05050a;
        --surface:  #0a0a15;
        --card:     #0d0d1f;
        --border:   #00f3ff44;
        --cyan:     #00f3ff;
        --green:    #00ff88;
        --pink:     #ff0055;
        --yellow:   #f5c542;
        --text:     #c8f0ff;
        --text-2:   #6aaabb;
        --text-3:   #2a4a55;
    }

    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', monospace;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }
    .stApp, .stApp > div, section.main, .block-container {
        background-color: var(--bg) !important;
    }
    .main > div { padding-top: 1rem; padding-bottom: 3rem; }

    [data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--cyan);
    }

    h1, h2, h3 {
        color: var(--cyan) !important;
        text-shadow: 0 0 10px var(--cyan), 0 0 20px var(--cyan);
        font-family: 'Orbitron', monospace;
        letter-spacing: 2px;
    }

    .stButton > button {
        background-color: rgba(0, 243, 255, 0.08);
        color: var(--cyan);
        border: 1px solid var(--cyan);
        border-radius: 0px;
        transition: 0.3s;
        width: 100%;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background-color: var(--cyan);
        color: #000;
        box-shadow: 0 0 20px var(--cyan);
    }

    div[data-testid="stTextInput"] input {
        background: var(--surface) !important;
        border: 1px solid var(--cyan) !important;
        color: var(--cyan) !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.1rem !important;
        border-radius: 0px !important;
    }

    div[data-testid="stTabs"] button {
        font-family: 'Share Tech Mono', monospace !important;
        color: var(--text-2) !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--cyan) !important;
        text-shadow: 0 0 8px var(--cyan);
        border-bottom: 2px solid var(--cyan) !important;
    }

    div[data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0px !important;
        padding: 0.8rem !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--cyan) !important;
        text-shadow: 0 0 8px var(--cyan);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.65rem !important;
        color: var(--text-2) !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }

    hr { border-color: var(--border) !important; }

    div[data-testid="stExpander"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0px !important;
    }

    /* テーブルスタイル */
    .cyb-table {
        width: 100%; border-collapse: collapse;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem; table-layout: fixed;
    }
    .cyb-table thead th {
        padding: 6px 10px;
        font-size: 0.58rem; letter-spacing: 1.8px;
        text-transform: uppercase; color: var(--text-2);
        font-weight: 700; background: transparent;
        border-bottom: 1px solid var(--border);
    }
    .cyb-table tbody tr:nth-child(odd)  { background: var(--surface); }
    .cyb-table tbody tr:nth-child(even) { background: var(--card); }
    .cyb-table tbody td {
        padding: 8px 10px; overflow: hidden;
        word-break: break-word; border: none; color: var(--text);
    }
    .cyb-table tbody td:nth-child(1) {
        color: var(--text-2); font-size: 0.78rem;
    }
    .td-ok {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px;
        background: rgba(0,255,136,.20); color: var(--green);
        font-weight: 900; font-size: 0.8rem;
        border-radius: 0; border: 1.5px solid rgba(0,255,136,.50);
    }
    .td-ng {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px;
        background: rgba(255,0,85,.20); color: var(--pink);
        font-weight: 900; font-size: 0.8rem;
        border-radius: 0; border: 1px solid rgba(255,0,85,.50);
    }
    .td-neu { color: var(--text-3); font-size: 1rem; }
    .ev-badge {
        display: inline-block; background: rgba(0,255,136,.15);
        color: var(--green); font-size: 0.72rem; font-weight: 700;
        padding: 2px 6px; white-space: nowrap;
    }
    .td-right { text-align: right; }

    /* スコアカード */
    .cyb-score-card {
        background: var(--surface);
        border: 1px solid var(--cyan);
        padding: 1rem; text-align: center;
        margin-bottom: 0.5rem;
        box-shadow: 0 0 10px rgba(0,243,255,0.1);
    }
    .cyb-score-label {
        font-size: 0.62rem; letter-spacing: 2px;
        text-transform: uppercase; color: var(--text-2); margin-bottom: 0.4rem;
    }
    .cyb-score-value {
        font-family: 'Orbitron', monospace;
        font-size: 2rem; font-weight: 700; line-height: 1;
    }
    .cyb-score-max { font-size: 0.65rem; color: var(--text-3); margin-top: 0.2rem; }

    /* メトリクスグリッド */
    .cyb-metric-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 0.4rem; margin-bottom: 0.8rem;
    }
    .cyb-metric-item {
        background: var(--surface);
        border: 1px solid var(--border);
        padding: 0.7rem 0.9rem;
    }
    .cyb-metric-lbl {
        font-size: 0.6rem; letter-spacing: 1.2px;
        text-transform: uppercase; color: var(--text-2);
        margin-bottom: 0.3rem;
    }
    .cyb-metric-val {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.25rem; font-weight: 700; color: var(--cyan);
        text-shadow: 0 0 6px var(--cyan);
    }
    .cyb-metric-sub {
        font-size: 0.75rem; color: var(--text-2); margin-top: 0.1rem;
    }

    /* 価格ヘッダー */
    .cyb-price-header {
        background: var(--surface);
        border: 1px solid var(--cyan);
        border-left: 3px solid var(--cyan);
        padding: 1rem 1.2rem; margin-bottom: 1rem;
        box-shadow: 0 0 15px rgba(0,243,255,0.1);
    }
    .cyb-ticker { font-size: 0.85rem; color: var(--text-2); letter-spacing: 2px; }
    .cyb-company { font-size: 1.1rem; font-weight: 700; color: var(--text); margin-top: 0.2rem; }
    .cyb-price-main {
        font-family: 'Orbitron', monospace;
        font-size: 2.2rem; font-weight: 700; margin-top: 0.6rem;
        letter-spacing: -0.5px; text-shadow: 0 0 10px currentColor;
    }
    .cyb-price-up   { color: var(--pink); }
    .cyb-price-down { color: var(--green); }
    .cyb-price-flat { color: var(--text); }
    .cyb-price-chg  { font-size: 0.85rem; margin-top: 0.2rem; }

    /* シグナルバナー */
    .cyb-signal-banner {
        padding: 1rem 1.2rem; margin-bottom: 0.8rem;
        display: flex; align-items: center; gap: 0.8rem;
        border-left: 3px solid;
    }
    .cyb-signal-text {
        font-family: 'Orbitron', monospace;
        font-size: 1rem; font-weight: 700; letter-spacing: 1px;
    }
    .cyb-signal-sub { font-size: 0.75rem; color: var(--text-2); margin-top: 0.1rem; }

    /* レンジグリッド */
    .cyb-range-grid {
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.4rem;
    }
    .cyb-range-item {
        background: var(--card); border: 1px solid var(--border);
        padding: 0.75rem; text-align: center;
    }
    .cyb-range-lbl {
        font-size: 0.58rem; letter-spacing: 1px; text-transform: uppercase;
        color: var(--text-2); margin-bottom: 0.25rem;
    }
    .cyb-range-val {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1rem; font-weight: 700; color: var(--cyan);
    }
    </style>
    """, unsafe_allow_html=True)


# ─── ヘルパー関数 ──────────────────────────

def _fmt(x, d=2):
    return "—" if x is None else f"{float(x):.{d}f}"

def _build_table(headers, rows):
    ths  = "".join(f"<th>{h}</th>" for h in headers)
    html = f'<table class="cyb-table"><thead><tr>{ths}</tr></thead><tbody>'
    for row in rows:
        tds = "".join(f"<td>{cell}</td>" for cell in row)
        html += f"<tr>{tds}</tr>"
    html += "</tbody></table>"
    return html


# ─── UI パーツ ──────────────────────────

def render_stat_header(data: Dict[str, Any]):
    symbol = data.get("symbol", "UNKNOWN")
    total_records = data.get("total_records", 0)
    
    st.markdown(f"""
    <div class="cyb-price-header">
      <div class="cyb-company">{symbol} 曜日別統計レポート</div>
      <div class="cyb-ticker">総レコード数: {total_records}</div>
      <div class="cyb-price-main">{total_records}</div>
      <div class="cyb-price-chg">データ期間: 300日</div>
    </div>
    """, unsafe_allow_html=True)


def render_weekday_stats(data: Dict[str, Any]):
    stats = data.get("weekday_stats", {})
    weekdays = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
    
    st.markdown("##### 📊 曜日別統計量")
    
    rows = []
    for weekday in weekdays:
        if weekday in stats:
            stat = stats[weekday]
            rows.append([
                weekday,
                f"{stat['count']}",
                f"{stat['mean']:.2f}",
                f"{stat['std']:.2f}",
                f"{stat['min']:.2f}",
                f"{stat['max']:.2f}"
            ])
    
    st.markdown(_build_table(["曜日", "件数", "平均", "標準偏差", "最小", "最大"], rows), unsafe_allow_html=True)


def render_test_results(data: Dict[str, Any]):
    tests = data.get("test_results", {})
    
    st.markdown("##### 🔬 統計検定結果")
    
    if "error" in tests:
        st.error(tests["error"])
        return
    
    # パラメトリック検定
    if 'parametric' in tests:
        param = tests['parametric']
        st.markdown("**パラメトリック検定:**")
        
        if 'anova' in param:
            anova = param['anova']
            status = "✅ 有意" if anova['significant'] else "❌ 有意差なし"
            st.markdown(f"- ANOVA: F={anova['f_statistic']:.4f}, p={anova['p_value']:.4f} ({status})")
            
            if anova['significant'] and 'posthoc_tukey' in param:
                st.markdown("  - Tukey-Kramer POST-HOC: 有意差あり")
    
    # ノンパラメトリック検定
    if 'nonparametric' in tests:
        nonparam = tests['nonparametric']
        st.markdown("**ノンパラメトリック検定:**")
        
        if 'kruskal_wallis' in nonparam:
            kw = nonparam['kruskal_wallis']
            status = "✅ 有意" if kw['significant'] else "❌ 有意差なし"
            st.markdown(f"- Kruskal-Wallis: H={kw['h_statistic']:.4f}, p={kw['p_value']:.4f} ({status})")
            
            if kw['significant'] and 'posthoc_steel_dwass' in nonparam:
                st.markdown("  - Steel-Dwass POST-HOC: 有意差あり")


def render_grouped_data_chart(data: Dict[str, Any]):
    grouped_data = data.get("grouped_data", {})
    
    st.markdown("##### 📈 曜日別データ分布")
    
    # 曜日ごとの平均をプロット
    weekdays = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
    means = []
    for weekday in weekdays:
        if weekday in grouped_data:
            df = pd.DataFrame(grouped_data[weekday])
            if not df.empty and 'Open' in df.columns:
                means.append(df['Open'].mean())
            else:
                means.append(0)
        else:
            means.append(0)
    
    chart_data = pd.DataFrame({
        '曜日': weekdays,
        '平均始値': means
    })
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x='曜日',
        y='平均始値',
        color=alt.value('#00f3ff')
    ).properties(
        height=300,
        background='transparent'
    )
    
    st.altair_chart(chart, use_container_width=True)


# ─── タブ: 概要 ────────────────────────────────────────────────────

def render_overview_tab(data: Dict[str, Any]):
    render_stat_header(data)
    render_weekday_stats(data)
    render_test_results(data)


# ─── タブ: 詳細 ────────────────────────────────────────────────────

def render_detail_tab(data: Dict[str, Any]):
    render_grouped_data_chart(data)
    
    st.markdown("##### 📋 生データ")
    grouped_data = data.get("grouped_data", {})
    for weekday, records in grouped_data.items():
        with st.expander(f"{weekday} ({len(records)}件)"):
            if records:
                df = pd.DataFrame(records)
                st.dataframe(df.head(10))


# ─── エントリーポイント ───────────────────────────────────────────

def run():
    _setup_style()
    
    st.title("📊 曜日別統計レポート")
    st.markdown("---")
    
    # サイドバー: 設定
    with st.sidebar:
        st.header("⚙️ 設定")
        ticker = st.text_input("ティッカーシンボル", value="SOL-JPY", key="ticker_input")
        period = st.selectbox("期間", ["1y", "6mo", "3mo"], index=0)
        
        if st.button("分析実行", use_container_width=True):
            with st.spinner("データを取得中..."):
                ticker_converted = convert_ticker(ticker)
                try:
                    data = get_stat_data_for_skin(ticker_converted, period)
                    st.session_state['stat_data'] = data
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state['stat_data'] = {"error": f"データ取得または分析に失敗しました: {str(e)}"}
    
    # メインコンテンツ
    if 'stat_data' in st.session_state:
        data = st.session_state['stat_data']
        
        if "error" in data:
            st.error(data["error"])
        else:
            tab1, tab2 = st.tabs(["📊 概要", "📈 詳細"])
            
            with tab1:
                render_overview_tab(data)
            
            with tab2:
                render_detail_tab(data)
    else:
        st.info("サイドバーからティッカーを入力して分析を実行してください。")


# ─── 開発・テスト用実行ブロック ──────────────────────────────────

if __name__ == "__main__":
    run()