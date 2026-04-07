import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from typing import Dict, Any

# 内部モジュールのインポート
from src.logic.output_stat import get_full_stat_report
from src.data.weekday_analysis import fetch_open_prices_with_dates

# ティッカー変換
def convert_ticker(raw: str) -> str:
    s = raw.strip()
    if not s:
        return ""
    t = s.upper()
    if t.endswith(".T"):
        return t
    if s.lower().endswith(".t"):
        return t[:-2] + ".T"
    if t.isdigit() and 4 <= len(t) <= 5:
        return t + ".T"
    return t

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
    mode = data.get("analysis_mode", "weekday")
    mode_label = "六曜モード" if mode == "rokuyou" else "曜日モード"
    
    st.markdown(f"""
    <div class="cyb-price-header">
      <div class="cyb-company">{symbol} {mode_label} 統計レポート</div>
      <div class="cyb-ticker">総レコード数: {total_records}</div>
      <div class="cyb-price-main">{total_records}</div>
      <div class="cyb-price-chg">データ期間: 2年</div>
    </div>
    """, unsafe_allow_html=True)


def render_weekday_stats(data: Dict[str, Any]):
    stats = data.get("weekday_stats", {})
    group_order = data.get("group_order", list(stats.keys()))
    mode = data.get("analysis_mode", "weekday")
    title = "六曜別統計量" if mode == "rokuyou" else "曜日別統計量"
    label = "六曜" if mode == "rokuyou" else "曜日"
    
    st.markdown(f"##### 📊 {title}")
    
    rows = []
    for group in group_order:
        if group in stats:
            stat = stats[group]
            rows.append([
                group,
                f"{stat['count']}",
                f"{stat['mean']:.2f}",
                f"{stat['std']:.2f}",
                f"{stat['min']:.2f}",
                f"{stat['max']:.2f}"
            ])
    
    st.markdown(_build_table([label, "件数", "平均", "標準偏差", "最小", "最大"], rows), unsafe_allow_html=True)


def render_test_results(data: Dict[str, Any]):
    tests = data.get("test_results", {})
    
    st.markdown("##### 🔬 統計検定結果")
    
    if "error" in tests:
        st.error(tests["error"])
        return
    
    # 判定ロジック
    decision = tests.get('decision', {})
    if decision:
        selected = decision.get('selected_test', 'unknown')
        use_parametric = decision.get('use_parametric', False)
        method_name = 'ANOVA' if use_parametric else 'Kruskal-Wallis'
        st.markdown(f"**推奨検定:** {method_name}")
        st.markdown(f"- 理由: {decision.get('reason', '判定情報なし')}" )
        st.markdown("---")
    
    # 正規性テスト
    if 'parametric' in tests and 'normality_tests' in tests['parametric']:
        st.markdown("**正規性テスト (Shapiro-Wilk):**")
        for weekday, res in tests['parametric']['normality_tests'].items():
            status = "正規" if res['normal'] else "非正規"
            st.markdown(f"- {weekday}: p={res['p_value']:.4f} ({status})")
        st.markdown("---")
    
    # 等分散テスト
    if 'parametric' in tests and 'homoscedasticity_test' in tests['parametric']:
        homo = tests['parametric']['homoscedasticity_test']
        status = "等分散" if homo['homoscedastic'] else "不等分散"
        st.markdown(f"**等分散テスト (Levene):** p={homo['p_value']:.4f} ({status})")
        st.markdown("---")
    
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
    group_order = data.get("group_order", list(grouped_data.keys()))
    mode = data.get("analysis_mode", "weekday")
    title = "六曜別データ分布" if mode == "rokuyou" else "曜日別データ分布"
    label = "六曜" if mode == "rokuyou" else "曜日"
    
    st.markdown(f"##### 📈 {title}")
    
    means = []
    for group in group_order:
        if group in grouped_data:
            df = pd.DataFrame(grouped_data[group])
            if not df.empty and 'Open' in df.columns:
                means.append(df['Open'].mean())
            else:
                means.append(0)
        else:
            means.append(0)
    
    chart_data = pd.DataFrame({
        label: group_order,
        '平均始値': means
    })
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X(label, type='nominal'),
        y=alt.Y('平均始値', type='quantitative'),
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
    
    # 全曜日のデータを統合（ダウンロード用）
    all_records = []
    for weekday, records in grouped_data.items():
        all_records.extend(records)
    
    # 全データダウンロードボタン
    if all_records:
        all_df = pd.DataFrame(all_records)
        csv_data = all_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 全データをCSVダウンロード",
            data=csv_data,
            file_name=f"{data.get('symbol', 'data')}_all_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown(f"**全データ: {len(all_records)}件**")
        st.markdown("---")
    
    # 曜日別に展開表示
    for weekday, records in grouped_data.items():
        with st.expander(f"{weekday} ({len(records)}件)"):
            if records:
                df = pd.DataFrame(records)
                st.dataframe(df, use_container_width=True)
                
                # 曜日別ダウンロードボタン
                csv_data_weekday = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"📥 {weekday}をCSVダウンロード",
                    data=csv_data_weekday,
                    file_name=f"{data.get('symbol', 'data')}_{weekday}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"download_{weekday}"
                )


# ─── エントリーポイント ───────────────────────────────────────────

def run():
    _setup_style()
    
    st.title("📊 統計レポート")
    st.markdown("---")
    
    # サイドバー: 設定
    with st.sidebar:
        st.header("⚙️ 設定")
        ticker = st.text_input("ティッカーシンボル", value="", key="ticker_input")
        period = st.selectbox("期間", ["2y", "1y", "6mo", "3mo"], index=0)
        
        current_mode = st.session_state.get("analysis_mode_select", "曜日モード")
        analysis_mode = "rokuyou" if current_mode == "六曜モード" else "weekday"

        if st.button("分析実行", use_container_width=True):
            with st.spinner("データを取得中..."):
                ticker_converted = convert_ticker(ticker)
                try:
                    raw_df = fetch_open_prices_with_dates(ticker_converted, period)
                    report = get_full_stat_report(raw_df, symbol=ticker_converted, mode=analysis_mode)
                    stat_data = {
                        "symbol": report["metadata"]["symbol"],
                        "total_records": report["metadata"]["total_records"],
                        "analysis_mode": report["metadata"].get("analysis_mode", "weekday"),
                        "weekday_stats": report["level_2_stats"],
                        "test_results": report["level_3_tests"],
                        "group_order": list(report["level_1_grouping"].keys()),
                        "grouped_data": {k: v.to_dict('records') for k, v in report["level_1_grouping"].items() if not v.empty},
                        "descriptions": report["descriptions"]
                    }
                    st.session_state['raw_df'] = raw_df
                    st.session_state['last_ticker'] = ticker_converted
                    st.session_state['last_period'] = period
                    st.session_state['last_analysis_mode'] = stat_data['analysis_mode']
                    st.session_state['stat_data'] = stat_data
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.session_state['stat_data'] = {"error": f"データ取得または分析に失敗しました: {str(e)}"}
        
        mode_select = st.selectbox("分析モード", ["曜日モード", "六曜モード"], index=0, key="analysis_mode_select")
        analysis_mode = "rokuyou" if mode_select == "六曜モード" else "weekday"
        
        if 'raw_df' in st.session_state and ticker and period:
            ticker_converted = convert_ticker(ticker)
            if ticker_converted == st.session_state.get('last_ticker') and period == st.session_state.get('last_period'):
                if st.session_state.get('last_analysis_mode') != analysis_mode:
                    report = get_full_stat_report(st.session_state['raw_df'], symbol=ticker_converted, mode=analysis_mode)
                    st.session_state['stat_data'] = {
                        "symbol": report["metadata"]["symbol"],
                        "total_records": report["metadata"]["total_records"],
                        "analysis_mode": report["metadata"].get("analysis_mode", "weekday"),
                        "weekday_stats": report["level_2_stats"],
                        "group_order": list(report["level_1_grouping"].keys()),
                        "grouped_data": {k: v.to_dict('records') for k, v in report["level_1_grouping"].items() if not v.empty},
                        "descriptions": report["descriptions"]
                    }
                    st.session_state['last_analysis_mode'] = analysis_mode
            else:
                if 'stat_data' in st.session_state:
                    st.warning("ティッカーまたは期間を変更した場合は、再度 [分析実行] をクリックしてください。")
                    st.session_state.pop('stat_data', None)
                    st.session_state.pop('raw_df', None)
                    st.session_state.pop('last_ticker', None)
                    st.session_state.pop('last_period', None)
                    st.session_state.pop('last_analysis_mode', None)
    
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