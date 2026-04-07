import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scikit_posthocs as sp

def perform_statistical_tests(grouped_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    曜日ごとのデータに対してパラメトリック検定とノンパラメトリック検定を行います。
    
    パラメトリック検定: one-way ANOVA + Tukey-Kramer POST-HOC
    ノンパラメトリック検定: Kruskal-Wallis + Steel-Dwass POST-HOC
    
    戻り値: 検定結果の辞書
    """
    # 平日のデータのみを使用（月曜日～金曜日）
    weekdays = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
    data_lists = []
    labels = []
    
    for weekday in weekdays:
        if weekday in grouped_data and not grouped_data[weekday].empty:
            prices = grouped_data[weekday]['Open'].dropna().tolist()
            if len(prices) > 0:
                data_lists.append(prices)
                labels.extend([weekday] * len(prices))
    
    if len(data_lists) < 2:
        return {"error": "十分なデータがありません。少なくとも2つの曜日のデータが必要です。"}
    
    # 全体のデータとラベル
    all_data = [item for sublist in data_lists for item in sublist]
    all_labels = labels
    
    results = {}
    
    # === パラメトリック検定 ===
    results['parametric'] = {}
    
    # 正規性テスト (Shapiro-Wilk)
    normality_results = {}
    for i, weekday in enumerate(weekdays):
        if i < len(data_lists):
            stat, p = stats.shapiro(data_lists[i])
            normality_results[weekday] = {'statistic': stat, 'p_value': p, 'normal': p > 0.05}
    
    results['parametric']['normality_tests'] = normality_results
    
    # 等分散テスト (Levene)
    if len(data_lists) >= 2:
        stat, p = stats.levene(*data_lists)
        results['parametric']['homoscedasticity_test'] = {'statistic': stat, 'p_value': p, 'homoscedastic': p > 0.05}
    
    # One-way ANOVA
    if len(data_lists) >= 2:
        f_stat, p_value = stats.f_oneway(*data_lists)
        results['parametric']['anova'] = {'f_statistic': f_stat, 'p_value': p_value, 'significant': p_value < 0.05}
        
        # POST-HOC: Tukey-Kramer (有意差がある場合)
        if p_value < 0.05:
            tukey_result = pairwise_tukeyhsd(all_data, all_labels, alpha=0.05)
            results['parametric']['posthoc_tukey'] = {
                'summary': tukey_result.summary().as_text(),
                'reject': tukey_result.reject.tolist(),
                'meandiffs': tukey_result.meandiffs.tolist(),
                'p_values': tukey_result.pvalues.tolist(),
                'groups': [f"{tukey_result.groupsunique[i]}-{tukey_result.groupsunique[j]}" 
                          for i in range(len(tukey_result.groupsunique)) 
                          for j in range(i+1, len(tukey_result.groupsunique))]
            }
    
    # === ノンパラメトリック検定 ===
    results['nonparametric'] = {}
    
    # Kruskal-Wallis検定
    if len(data_lists) >= 2:
        h_stat, p_value = stats.kruskal(*data_lists)
        results['nonparametric']['kruskal_wallis'] = {'h_statistic': h_stat, 'p_value': p_value, 'significant': p_value < 0.05}
        
        # POST-HOC: Steel-Dwass (有意差がある場合)
        if p_value < 0.05:
            # Steel-Dwass法
            steel_dwass_result = sp.posthoc_dunn(all_data, all_labels, p_adjust='bonferroni')
            results['nonparametric']['posthoc_steel_dwass'] = {
                'p_values': steel_dwass_result.values.tolist(),
                'groups': steel_dwass_result.columns.tolist(),
                'index': steel_dwass_result.index.tolist()
            }
    
    return results

def print_test_results(results: Dict[str, Any]):
    """
    検定結果を表示します。
    """
    if "error" in results:
        print(results["error"])
        return
    
    print("=== パラメトリック検定結果 ===")
    
    # 正規性テスト
    print("\n正規性テスト (Shapiro-Wilk):")
    for weekday, res in results['parametric']['normality_tests'].items():
        print(f"  {weekday}: p={res['p_value']:.4f} ({'正規' if res['normal'] else '非正規'})")
    
    # 等分散テスト
    if 'homoscedasticity_test' in results['parametric']:
        res = results['parametric']['homoscedasticity_test']
        print(f"\n等分散テスト (Levene): p={res['p_value']:.4f} ({'等分散' if res['homoscedastic'] else '不等分散'})")
    
    # ANOVA
    if 'anova' in results['parametric']:
        res = results['parametric']['anova']
        print(f"\nOne-way ANOVA: F={res['f_statistic']:.4f}, p={res['p_value']:.4f} ({'有意' if res['significant'] else '有意差なし'})")
        
        if res['significant'] and 'posthoc_tukey' in results['parametric']:
            print("\nTukey-Kramer POST-HOC:")
            print(results['parametric']['posthoc_tukey']['summary'])
    
    print("\n=== ノンパラメトリック検定結果 ===")
    
    # Kruskal-Wallis
    if 'kruskal_wallis' in results['nonparametric']:
        res = results['nonparametric']['kruskal_wallis']
        print(f"\nKruskal-Wallis検定: H={res['h_statistic']:.4f}, p={res['p_value']:.4f} ({'有意' if res['significant'] else '有意差なし'})")
        
        if res['significant'] and 'posthoc_steel_dwass' in results['nonparametric']:
            print("\nSteel-Dwass POST-HOC (p値行列):")
            p_matrix = results['nonparametric']['posthoc_steel_dwass']['p_values']
            groups = results['nonparametric']['posthoc_steel_dwass']['groups']
            for i, row in enumerate(p_matrix):
                for j, p_val in enumerate(row):
                    if i < j:  # 上三角のみ表示
                        print(f"  {groups[i]} vs {groups[j]}: p={p_val:.4f}")

if __name__ == "__main__":
    # weekday_analysis.py からデータをインポートしてテスト
    try:
        from weekday_analysis import fetch_open_prices_with_dates, group_by_weekday
        
        symbol = "SOL-JPY"
        df = fetch_open_prices_with_dates(symbol)
        if not df.empty:
            grouped = group_by_weekday(df)
            results = perform_statistical_tests(grouped)
            print_test_results(results)
        else:
            print("データ取得に失敗しました。")
    except ImportError:
        print("weekday_analysis.pyが見つからないか、必要なライブラリがインストールされていません。")