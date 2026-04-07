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
    data_lists = []
    labels = []
    group_order = list(grouped_data.keys())
    
    for group in group_order:
        if group in grouped_data and not grouped_data[group].empty:
            prices = grouped_data[group]['Open'].dropna().tolist()
            if len(prices) > 0:
                data_lists.append(prices)
                labels.extend([group] * len(prices))
    
    if len(data_lists) < 2:
        return {"error": "十分なデータがありません。少なくとも2つのグループのデータが必要です。"}
    
    # 全体のデータとラベル
    all_data = [item for sublist in data_lists for item in sublist]
    all_labels = labels
    
    results = {}
    
    # === パラメトリック検定 ===
    results['parametric'] = {}
    
    # 正規性テスト (Shapiro-Wilk)
    normality_results = {}
    for i, group in enumerate(group_order):
        if i < len(data_lists):
            stat, p = stats.shapiro(data_lists[i])
            normality_results[group] = {'statistic': stat, 'p_value': p, 'normal': p > 0.05}
    
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

def choose_test_strategy(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    正規性と等分散性の結果に基づいて、使用すべき検定手法を決定します。
    """
    param = results.get('parametric', {})
    normality_tests = param.get('normality_tests', {})
    normality_ok = all(res.get('normal', False) for res in normality_tests.values()) if normality_tests else False
    homoscedasticity_ok = param.get('homoscedasticity_test', {}).get('homoscedastic', False)
    use_parametric = normality_ok and homoscedasticity_ok
    selected_test = 'anova' if use_parametric else 'kruskal_wallis'
    reasons = []
    if not normality_ok:
        reasons.append('正規性が成立しない曜日があります')
    if not homoscedasticity_ok:
        reasons.append('等分散性が成立していません')
    if not reasons:
        reasons.append('正規性および等分散性が成立しました')

    return {
        'use_parametric': use_parametric,
        'selected_test': selected_test,
        'reason': ' / '.join(reasons),
        'normality_ok': normality_ok,
        'homoscedasticity_ok': homoscedasticity_ok
    }


def print_test_results(results: Dict[str, Any]):
    """
    検定結果を表示します。
    """
    if "error" in results:
        print(results["error"])
        return
    
    print("検定結果:")
    if 'parametric' in results:
        param = results['parametric']
        if 'normality_tests' in param:
            print("  正規性テスト (Shapiro-Wilk):")
            for weekday, res in param['normality_tests'].items():
                print(f"    {weekday}: statistic={res['statistic']:.4f}, p={res['p_value']:.4f}, normal={res['normal']}")
        if 'homoscedasticity_test' in param:
            homo = param['homoscedasticity_test']
            print(f"  等分散テスト (Levene): statistic={homo['statistic']:.4f}, p={homo['p_value']:.4f}, homoscedastic={homo['homoscedastic']}")
        if 'anova' in param:
            anova = param['anova']
            print(f"  ANOVA: F={anova['f_statistic']:.4f}, p={anova['p_value']:.4f}, significant={anova['significant']}")
            if anova['significant'] and 'posthoc_tukey' in param:
                print("    Tukey-Kramer POST-HOC: 有意差あり")
    if 'nonparametric' in results:
        nonparam = results['nonparametric']
        if 'kruskal_wallis' in nonparam:
            kw = nonparam['kruskal_wallis']
            print(f"  Kruskal-Wallis: H={kw['h_statistic']:.4f}, p={kw['p_value']:.4f}, significant={kw['significant']}")
            if kw['significant'] and 'posthoc_steel_dwass' in nonparam:
                print("    Steel-Dwass POST-HOC: 有意差あり")

def decide_and_print_tests(results: Dict[str, Any]):
    """
    正規性と等分散性の結果に基づいて、適切な検定を出力します。
    - すべての曜日が正規分布で等分散の場合: ANOVA
    - それ以外の場合: Kruskal-Wallis
    """
    if "error" in results:
        print(results["error"])
        return
    
    param = results.get('parametric', {})
    
    # 正規性チェック: すべての曜日が normal=True か
    normality_ok = True
    if 'normality_tests' in param:
        for res in param['normality_tests'].values():
            if not res['normal']:
                normality_ok = False
                break
    
    # 等分散チェック
    homoscedasticity_ok = param.get('homoscedasticity_test', {}).get('homoscedastic', False)
    
    print("\n[3] 統計検定結果:")
    
    # 正規性テスト出力
    if 'normality_tests' in param:
        print("  正規性テスト (Shapiro-Wilk):")
        for weekday, res in param['normality_tests'].items():
            print(f"    {weekday}: statistic={res['statistic']:.4f}, p={res['p_value']:.4f}, normal={res['normal']}")
    
    # 等分散テスト出力
    if 'homoscedasticity_test' in param:
        homo = param['homoscedasticity_test']
        print(f"  等分散テスト (Levene): statistic={homo['statistic']:.4f}, p={homo['p_value']:.4f}, homoscedastic={homo['homoscedastic']}")
    
    # ロジックに基づく検定出力
    if normality_ok and homoscedasticity_ok:
        print("  帰無仮説採択（正規分布かつ等分散） → パラメトリック検定 (ANOVA):")
        if 'anova' in param:
            anova = param['anova']
            print(f"    ANOVA: F={anova['f_statistic']:.4f}, p={anova['p_value']:.4f} ({'有意' if anova['significant'] else '有意差なし'})")
            if anova['significant'] and 'posthoc_tukey' in param:
                print("      Tukey-Kramer POST-HOC: 有意差あり")
    else:
        print("  帰無仮説棄却（正規分布でないか等分散でない） → ノンパラメトリック検定 (Kruskal-Wallis):")
        nonparam = results.get('nonparametric', {})
        if 'kruskal_wallis' in nonparam:
            kw = nonparam['kruskal_wallis']
            print(f"    Kruskal-Wallis: H={kw['h_statistic']:.4f}, p={kw['p_value']:.4f} ({'有意' if kw['significant'] else '有意差なし'})")
            if kw['significant'] and 'posthoc_steel_dwass' in nonparam:
                print("      Steel-Dwass POST-HOC: 有意差あり")

if __name__ == "__main__":
    # src パッケージ経由で weekday_analysis をインポートしてテスト
    try:
        from src.data.weekday_analysis import fetch_open_prices_with_dates, group_by_weekday
        
        symbol = "SOL-JPY"
        df = fetch_open_prices_with_dates(symbol)
        if not df.empty:
            grouped = group_by_weekday(df)
            results = perform_statistical_tests(grouped)
            print_test_results(results)
        else:
            print("データ取得に失敗しました。")
    except ImportError:
        print("src.data.weekday_analysis が見つからないか、必要なライブラリがインストールされていません。")