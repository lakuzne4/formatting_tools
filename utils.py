import pandas as pd
from pandas.api.types import is_numeric_dtype
from collections import defaultdict

def calc_one_total_row(df, total_name='Total', aggfunc='sum', fillna='', 
                       fillna_str='',
                       calculated_fields_func=None):
    """ подсчёт total по аггрегирующей функции для числовых типов данных"""
    col_order = df.columns.tolist()
    
    if df.index.nlevels == 1:
        total_index = [total_name]
    elif df.index.nlevels > 1:
        total_index = pd.MultiIndex.from_tuples([tuple([total_name] + [''] * (df.index.nlevels - 1))])
    
    cols_to_apply_aggfunc = df.select_dtypes(include=[np.number]).columns
    
    total = pd.DataFrame(df[cols_to_apply_aggfunc].agg(aggfunc).to_dict(), index=total_index)
    
    if isinstance(fillna, str):
        fillna = defaultdict(lambda: fillna)
    elif isinstance(fillna, dict):
        for col in col_order:
            if col not in fillna:
                fillna[col] = fillna_str
    
    for col in df.select_dtypes(exclude=[np.number]):
        total.loc[:, col] = fillna[col]
        
    # применить для задания нескольких функций подсчёта
    if calculated_fields_func is not None:
        if callable(calculated_fields_func):
            total = calculated_fields_func(total)
        elif isinstance(calculated_fields_func, list):
            
            for func in calculated_fields_func:
                total = func(total)
                
    
    new_cols = [i for i in total.columns.tolist() if i not in col_order]
    total = total[col_order + new_cols]
    
    return df.append(total)
    
def calc_total(df, 
               total_name='Total', 
               aggfunc='sum', 
               fillna='', 
               fillna_str='', 
               calculated_fields_func=None, 
               groups = None):

    if groups is not None:
        to_result = []
        for group_number, group in df.groupby(groups):
            to_result.append(calc_one_total_row(group, total_name, aggfunc, fillna, fillna_str, 
                                                calculated_fields_func))
        
        return pd.concat(to_result)
    else:
        return calc_one_total_row(df, total_name, aggfunc, fillna, fillna_str,
                                                calculated_fields_func)