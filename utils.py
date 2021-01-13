import pandas as pd
from pandas.api.types import is_numeric_dtype

def calc_one_total_row(df, total_name='Total', aggfunc='sum', fillna=None, 
                       calculated_fields_func=None):
    """ подсчёт total по аггрегирующей функции для числовых типов данных"""
    if fillna is None:
        fillna = {}
    
    col_order = df.columns.tolist()
    
    if df.index.nlevels == 1:
        total_index = [total_name]
    elif df.index.nlevels > 1:
        total_index = pd.MultiIndex.from_tuples([tuple([total_name] + [''] * (df.index.nlevels - 1))])
    
    # выбрать все числовые колонки для применения функции аггрегации
    cols_to_apply_aggfunc = df.select_dtypes(include=[np.number]).columns
    if isinstance(fillna, dict):
        cols_to_apply_aggfunc = [i for i in cols_to_apply_aggfunc if i not in fillna]
    
    # применить функцию аггрегации
    total = pd.DataFrame(df[cols_to_apply_aggfunc].agg(aggfunc).to_dict(), index=total_index)
    
    # заполнить выбранные пользователем колонки пустыми значениями
    for col in fillna:
        total.loc[:, col] = fillna[col]
        
    for col in df.select_dtypes(exclude=[np.number]).columns:
        total.loc[:, col] = ''
        
    # подсчитать все вычисляемые поля на сделанной аггрегации
    if calculated_fields_func is not None:
        if callable(calculated_fields_func):
            total = calculated_fields_func(total)
        elif isinstance(calculated_fields_func, list):
            
            for func in calculated_fields_func:
                total = func(total)
                
    
#     new_cols = [i for i in total.columns.tolist() if i not in col_order]
#     total = total[col_order + new_cols]
    total = total[col_order]
    total = total.astype(df.dtypes, errors='ignore')
    
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
            subtotal = calc_one_total_row(group, total_name, aggfunc, fillna, 
                                                calculated_fields_func)
            to_result.append(subtotal)
        
        return pd.concat(to_result)
    else:
        return calc_one_total_row(df, total_name, aggfunc, fillna,
                                                calculated_fields_func)