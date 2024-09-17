import numpy as np
import pandas as pd
def explore_percent(filepath: str):
    """
    Takes the diversity csv data, calculates the XPL% for every iteration, and then calculates the mean XPL%
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(axis=0, how='any', inplace=True)

    div_max = df['diversity'].max(axis='columns')
    df['xpl_percent'] = df['diversity'] / div_max * 100
    return df['xpl_percent'].mean()

def infeasible_percent(filepath: str):
    """
    Takes the F% (calculated while running experiments) and returns the mean
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    return df['f%'].mean()


